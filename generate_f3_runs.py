import random
import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "DhruvHegde")
REPO_NAME = os.getenv("REPO_NAME", "dependency-error-repo")
GIT_BRANCH = os.getenv("GIT_BRANCH", "feature/f3-test-failures")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "f3_test.yml")

LOGS_DIR = Path("logs/F3")
METADATA_DIR = Path("metadata/F3")
LABELS_FILE = Path("labels.csv")
TEST_FILE = Path("tests/test_app.py")

CSV_COLUMNS = [
    "run_id",
    "repo_name",
    "commit_sha",
    "workflow_id",
    "stage",
    "failure_type",
    "error_type",
    "status",
    "duration",
]

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

ERROR_TYPES = [
    "AssertionError",
    "IndexError",
    "KeyError",
    "TypeError",
    "ValueError",
    "AttributeError",
    "ZeroDivisionError",
    "FileNotFoundError",
]


def sync_and_prepare_labels(clean_f3: bool) -> int:
    """Enforces canonical schema, handles isolated cleanup, and returns existing F3 count."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    if clean_f3:
        for f in LOGS_DIR.glob("*"):
            if f.is_file():
                f.unlink()
        for f in METADATA_DIR.glob("*"):
            if f.is_file():
                f.unlink()

    if not LABELS_FILE.exists():
        with open(LABELS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
        return 0

    preserved_rows = []
    f3_count = 0

    with open(LABELS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        
        # Detect if file was written with old 5-column header or malformed layout
        is_canonical = header == CSV_COLUMNS

        for row in reader:
            if not row:
                continue

            row_dict = {}
            if is_canonical and len(row) == len(CSV_COLUMNS):
                row_dict = dict(zip(CSV_COLUMNS, row))
            elif len(row) >= 9:
                # Realign previously mismatched 9-element rows
                row_dict = {
                    "run_id": row[0],
                    "repo_name": row[1],
                    "commit_sha": row[2],
                    "workflow_id": row[3],
                    "stage": row[4],
                    "failure_type": row[5],
                    "error_type": row[6],
                    "status": row[7],
                    "duration": row[8],
                }
            elif len(row) == 5:
                row_dict = {
                    "run_id": row[0],
                    "repo_name": row[1],
                    "commit_sha": "",
                    "workflow_id": "",
                    "stage": row[4],
                    "failure_type": row[3],
                    "error_type": "",
                    "status": row[2],
                    "duration": "",
                }

            is_f3 = (
                row_dict.get("failure_type") == "F3"
                or (len(row) > 5 and row[5] == "F3")
                or (len(row) > 3 and row[3] == "F3")
            )

            if is_f3:
                if not clean_f3:
                    preserved_rows.append(row_dict)
                    f3_count += 1
            else:
                preserved_rows.append(row_dict)

    # Overwrite file ensuring strict 9-column header
    with open(LABELS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(preserved_rows)

    return f3_count


def git_commit_and_push(batch_num: int) -> str:
    subprocess.run(["git", "add", str(TEST_FILE)], check=True, capture_output=True)
    commit_msg = f"synthetic(F3): parallel matrix batch run #{batch_num}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
    
    success = False
    for attempt in range(3):
        res = subprocess.run(["git", "push", "origin", GIT_BRANCH], capture_output=True, text=True)
        if res.returncode == 0:
            success = True
            break
        time.sleep(5)
    if not success:
        raise RuntimeError(f"Git push failed: {res.stderr}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    return sha.stdout.strip()


def poll_workflow_run(commit_sha: str, timeout_sec: int = 360) -> dict:
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs"
    params = {"head_sha": commit_sha, "branch": GIT_BRANCH}
    start_time = time.time()

    while time.time() - start_time < timeout_sec:
        try:
            res = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if res.status_code == 200:
                runs = res.json().get("workflow_runs", [])
                if runs:
                    run = runs[0]
                    if run.get("status") == "completed":
                        return run
            elif res.status_code in (403, 429):
                # Rate limit backoff
                retry_after = int(res.headers.get("Retry-After", 30))
                print(f"[Rate Limit] Backing off for {retry_after}s...")
                time.sleep(retry_after)
            elif res.status_code >= 500:
                time.sleep(10)
        except requests.exceptions.RequestException:
            time.sleep(5)

        time.sleep(2)

    raise TimeoutError(f"Workflow polling timed out for commit {commit_sha}")


def fetch_and_save_matrix_artifacts(run: dict, commit_sha: str):
    run_id = run["id"]

    jobs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    jobs_res = requests.get(jobs_url, headers=HEADERS, timeout=30)
    if jobs_res.status_code != 200:
        print(f"[Warning] Failed to fetch jobs for run {run_id} (HTTP {jobs_res.status_code})")
        return

    jobs = jobs_res.json().get("jobs", [])

    for job in jobs:
        job_id = job["id"]
        job_name = job.get("name", "")
        
        matched_error = "AssertionError"
        for err in ERROR_TYPES:
            if err in job_name:
                matched_error = err
                break

        metadata_path = METADATA_DIR / f"{job_id}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(job, f, indent=2)

        log_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job_id}/logs"
        log_path = LOGS_DIR / f"{job_id}.log"
        log_res = requests.get(log_url, headers=HEADERS, timeout=30)

        if log_res.status_code == 200:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(log_res.text)
        else:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(f"Log retrieval failed with HTTP {log_res.status_code}")

        started_at_str = job.get("started_at")
        completed_at_str = job.get("completed_at")
        duration = 0.0
        if started_at_str and completed_at_str:
            started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00"))
            completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
            duration = round((completed_at - started_at).total_seconds(), 2)

        conclusion = job.get("conclusion", "failure")

        record = {
            "run_id": str(job_id),
            "repo_name": f"{REPO_OWNER}/{REPO_NAME}",
            "commit_sha": commit_sha,
            "workflow_id": WORKFLOW_FILE,
            "stage": "test",
            "failure_type": "F3",
            "error_type": matched_error,
            "status": conclusion,
            "duration": duration,
        }

        with open(LABELS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writerow(record)

        print(f"  -> Job {job_id} ({job_name}): {conclusion} [{matched_error}] ({duration}s)")


def main():
    parser = argparse.ArgumentParser(description="High-Speed Parallel Matrix F3 Test Failure Generation Engine")
    parser.add_argument("--runs", type=int, default=500, help="Total target F3 runs (default: 500)")
    parser.add_argument("--clean", action="store_true", help="Purge prior F3 data before starting")
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not found in environment or .env file.")

    existing_f3_runs = sync_and_prepare_labels(clean_f3=args.clean)
    
    batch_size = 16
    target_batches = (args.runs + batch_size - 1) // batch_size
    current_batch = existing_f3_runs // batch_size

    if existing_f3_runs >= args.runs:
        print(f"Target of {args.runs} F3 runs already reached ({existing_f3_runs} present). Exiting.")
        return

    print(f"Starting High-Speed Parallel Matrix F3 Generator.")
    print(f"Existing runs: {existing_f3_runs}. Target runs: {args.runs}. Executing in batches of {batch_size}...")

    try:
        for b in range(current_batch + 1, target_batches + 1):
            print(f"\n[Batch {b}/{target_batches}] Triggering matrix run (16 parallel jobs)...")
            
            commit_sha = git_commit_and_push(batch_num=b)
            run_data = poll_workflow_run(commit_sha)
            fetch_and_save_matrix_artifacts(run_data, commit_sha)

            print(f"[Batch {b} Complete] Workflow Run ID: {run_data['id']}")
            time.sleep(1)

    finally:
        print("Parallel generation batch run finished.")


if __name__ == "__main__":
    main()
