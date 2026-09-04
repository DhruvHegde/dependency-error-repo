import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import random
import subprocess
import time
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
BATCH_FILE = Path(".f3_batch.json")
BATCH_SIZE = 250

CSV_COLUMNS = [
    "run_number",
    "dependency",
    "repository",
    "commit_sha",
    "workflow_id",
    "workflow_conclusion",
    "failure_type",
    "stage",
    "validation_status",
    "matched_pattern",
    "log_file",
    "metadata_file",
    "timestamp",
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


def select_error_types(count: int, seed: int | None = None) -> list[str]:
    """Select errors randomly while gently favoring less-used types."""
    rng = random.Random(seed)
    counts = {error_type: 0 for error_type in ERROR_TYPES}
    if LABELS_FILE.exists():
        with open(LABELS_FILE, "r", newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                error_type = row.get("dependency", "")
                if row.get("failure_type") == "F3" and error_type in counts:
                    counts[error_type] += 1

    selected = []
    for _ in range(count):
        weights = [1.0 / (1.0 + counts[error_type]) for error_type in ERROR_TYPES]
        error_type = rng.choices(ERROR_TYPES, weights=weights, k=1)[0]
        selected.append(error_type)
        counts[error_type] += 1
    return selected


def write_batch_spec(batch_size: int, seed: int | None = None) -> list[dict[str, object]]:
    """Write the randomized matrix consumed by the dynamic workflow."""
    error_types = select_error_types(batch_size, seed=seed)
    entries = [
        {"sample": index, "error_type": error_type}
        for index, error_type in enumerate(error_types, start=1)
    ]
    BATCH_FILE.write_text(json.dumps({"include": entries}, indent=2), encoding="utf-8")
    return entries


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
        
        is_canonical = header == CSV_COLUMNS

        for row in reader:
            if not row:
                continue

            if is_canonical and len(row) == len(CSV_COLUMNS):
                row_dict = dict(zip(CSV_COLUMNS, row))
            else:
                row_dict = migrate_legacy_row(row)

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

    # Overwrite file ensuring the canonical schema.
    with open(LABELS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(preserved_rows)

    return f3_count


def migrate_legacy_row(row: list[str]) -> dict[str, str]:
    """Convert the previous label layouts into the current registry schema."""
    if len(row) >= 9:
        run_number, repository, commit_sha, workflow_id, stage = row[:5]
        failure_type, error_type, status = row[5:8]
    elif len(row) == 5:
        run_number, repository, status, failure_type, stage = row
        commit_sha = ""
        workflow_id = ""
        error_type = ""
    else:
        return {column: "" for column in CSV_COLUMNS}

    metadata_file = f"metadata/F3/{run_number}.json" if failure_type == "F3" else ""
    log_file = f"logs/F3/{run_number}.log" if failure_type == "F3" else ""
    timestamp = ""
    if metadata_file and Path(metadata_file).exists():
        with open(metadata_file, "r", encoding="utf-8") as metadata_stream:
            metadata = json.load(metadata_stream)
        timestamp = metadata.get("completed_at", "")

    return {
        "run_number": run_number,
        "dependency": error_type,
        "repository": repository,
        "commit_sha": commit_sha,
        "workflow_id": workflow_id,
        "workflow_conclusion": status,
        "failure_type": failure_type,
        "stage": stage,
        "validation_status": status,
        "matched_pattern": error_type,
        "log_file": log_file,
        "metadata_file": metadata_file,
        "timestamp": timestamp,
    }


def git_commit_and_push(batch_num: int) -> str:
    # Ensure there is a file change to commit
    timestamp_comment = f"\n# Trigger batch {batch_num} at {time.time()}\n"
    with open(TEST_FILE, "a", encoding="utf-8") as f:
        f.write(timestamp_comment)

    # Add all changes (including deletions from --clean)
    subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
    commit_msg = f"synthetic(F3): parallel matrix batch run #{batch_num}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
    
    success = False
    for attempt in range(3):
        # Ensure we are up to date before pushing
        subprocess.run(["git", "pull", "--rebase", "origin", GIT_BRANCH], capture_output=True)
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
                for r in runs:
                    if (WORKFLOW_FILE in r.get("path", "") or r.get("name") == "F3 Test Failures CI") and r.get("status") == "completed":
                        return r
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


def fetch_and_save_matrix_artifacts(run: dict, commit_sha: str, expected_jobs: int):
    run_id = run["id"]

    jobs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/jobs"
    jobs = []
    page = 1
    while True:
        jobs_res = requests.get(
            jobs_url,
            headers=HEADERS,
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        if jobs_res.status_code != 200:
            raise RuntimeError(f"Failed to fetch jobs for run {run_id} (HTTP {jobs_res.status_code})")
        page_jobs = jobs_res.json().get("jobs", [])
        jobs.extend(page_jobs)
        if len(page_jobs) < 100:
            break
        page += 1

    jobs = [job for job in jobs if job.get("name", "").startswith("test-f3 (")]
    unique_jobs = {job["id"]: job for job in jobs}
    jobs = list(unique_jobs.values())
    if len(jobs) != expected_jobs:
        raise RuntimeError(f"Expected {expected_jobs} F3 jobs, collected {len(jobs)}")

    def download_job(job: dict) -> dict:
        job_id = job["id"]
        job_name = job.get("name", "")
        matched_error = next(
            (error_type for error_type in ERROR_TYPES if error_type in job_name),
            "AssertionError",
        )
        metadata_path = METADATA_DIR / f"{job_id}.json"
        metadata_path.write_text(json.dumps(job, indent=2), encoding="utf-8")

        log_path = LOGS_DIR / f"{job_id}.log"
        log_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/jobs/{job_id}/logs"
        log_res = requests.get(log_url, headers=HEADERS, timeout=30)
        log_text = log_res.text if log_res.status_code == 200 else f"Log retrieval failed with HTTP {log_res.status_code}"
        log_path.write_text(log_text, encoding="utf-8")

        completed_at_str = job.get("completed_at") or ""
        return {
            "job": job,
            "matched_error": matched_error,
            "metadata_path": metadata_path,
            "log_path": log_path,
            "timestamp": completed_at_str,
        }

    records = []
    with ThreadPoolExecutor(max_workers=min(32, expected_jobs)) as executor:
        futures = [executor.submit(download_job, job) for job in jobs]
        for future in as_completed(futures):
            records.append(future.result())

    with open(LABELS_FILE, "a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS)
        for result in records:
            job = result["job"]
            job_id = job["id"]
            job_name = job.get("name", "")
            matched_error = result["matched_error"]
            metadata_path = result["metadata_path"]
            log_path = result["log_path"]
            completed_at_str = result["timestamp"]
            started_at_str = job.get("started_at")
            duration = 0.0
            if started_at_str and completed_at_str:
                started_at = datetime.fromisoformat(started_at_str.replace("Z", "+00:00"))
                completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
                duration = round((completed_at - started_at).total_seconds(), 2)

            conclusion = job.get("conclusion", "failure")
            record = {
                "run_number": str(job_id),
                "dependency": matched_error,
                "repository": f"{REPO_OWNER}/{REPO_NAME}",
                "commit_sha": commit_sha,
                "workflow_id": WORKFLOW_FILE,
                "workflow_conclusion": conclusion,
                "failure_type": "F3",
                "stage": "test",
                "validation_status": conclusion,
                "matched_pattern": matched_error,
                "log_file": str(log_path).replace("\\", "/"),
                "metadata_file": str(metadata_path).replace("\\", "/"),
                "timestamp": completed_at_str,
            }
            writer.writerow(record)
            print(f"  -> Job {job_id} ({job_name}): {conclusion} [{matched_error}] ({duration}s)")


def main():
    parser = argparse.ArgumentParser(description="High-Speed Parallel Matrix F3 Test Failure Generation Engine")
    parser.add_argument("--runs", type=int, default=500, help="Total target F3 runs (default: 500)")
    parser.add_argument("--clean", action="store_true", help="Purge prior F3 data before starting")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for reproducible error selection")
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not found in environment or .env file.")

    existing_f3_runs = sync_and_prepare_labels(clean_f3=args.clean)
    
    if existing_f3_runs >= args.runs:
        print(f"Target of {args.runs} F3 runs already reached ({existing_f3_runs} present). Exiting.")
        return

    remaining = args.runs - existing_f3_runs
    batch_number = 1
    print("Starting randomized F3 generator.")
    print(f"Existing runs: {existing_f3_runs}. Target runs: {args.runs}. Batch limit: {BATCH_SIZE}...")

    try:
        while remaining > 0:
            batch_size = min(BATCH_SIZE, remaining)
            print(f"\n[Batch {batch_number}] Triggering randomized matrix run ({batch_size} jobs)...")
            write_batch_spec(batch_size, seed=None if args.seed is None else args.seed + batch_number)
            
            commit_sha = git_commit_and_push(batch_num=batch_number)
            run_data = poll_workflow_run(commit_sha)
            fetch_and_save_matrix_artifacts(run_data, commit_sha, expected_jobs=batch_size)

            print(f"[Batch {batch_number} Complete] Workflow Run ID: {run_data['id']}")
            remaining -= batch_size
            batch_number += 1
            time.sleep(1)

    finally:
        print("Parallel generation batch run finished.")


if __name__ == "__main__":
    main()
