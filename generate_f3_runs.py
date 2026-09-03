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

ERROR_MUTATIONS = {
    "AssertionError": """
def test_assertion_failure():
    \"\"\"Injected synthetic AssertionError.\"\"\"
    expected_status = 200
    actual_status = 500
    assert actual_status == expected_status, f"Expected {expected_status}, received {actual_status}"
""",
    "IndexError": """
def test_index_error():
    \"\"\"Injected synthetic IndexError.\"\"\"
    from src.app import get_list_item
    dataset = [10, 20, 30]
    get_list_item(dataset, 999)
""",
    "KeyError": """
def test_key_error():
    \"\"\"Injected synthetic KeyError.\"\"\"
    from src.app import get_dict_value
    config = {"env": "staging", "retries": 3}
    get_dict_value(config, "missing_auth_token")
""",
    "TypeError": """
def test_type_error():
    \"\"\"Injected synthetic TypeError.\"\"\"
    from src.app import calculate_division
    calculate_division("invalid_string", 5)
""",
    "ValueError": """
def test_value_error():
    \"\"\"Injected synthetic ValueError.\"\"\"
    from src.app import convert_to_int
    convert_to_int("unparseable_alphanumeric_0x99")
""",
    "AttributeError": """
def test_attribute_error():
    \"\"\"Injected synthetic AttributeError.\"\"\"
    from src.app import get_object_attribute
    get_object_attribute(object())
""",
    "ZeroDivisionError": """
def test_zero_division_error():
    \"\"\"Injected synthetic ZeroDivisionError.\"\"\"
    from src.app import calculate_division
    calculate_division(42, 0)
""",
    "FileNotFoundError": """
def test_file_not_found_error():
    \"\"\"Injected synthetic FileNotFoundError.\"\"\"
    from src.app import read_config_file
    read_config_file("fixtures/non_existent_pipeline_config.json")
""",
}


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


def read_baseline_tests() -> str:
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        return f.read()


def write_test_mutation(baseline_content: str, error_type: str):
    mutation = ERROR_MUTATIONS[error_type]
    full_content = f"{baseline_content}\n\n# --- SYNTHETIC F3 FAILURE MUTATION ---\n{mutation}"
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write(full_content)


def restore_baseline_tests(baseline_content: str):
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write(baseline_content)


def git_commit_and_push(iteration: int, error_type: str) -> str:
    subprocess.run(["git", "add", str(TEST_FILE)], check=True, capture_output=True)
    commit_msg = f"synthetic(F3): inject {error_type} [run #{iteration}]"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
    
    # Push with automated retry on transient network issues
    for attempt in range(3):
        res = subprocess.run(["git", "push", "origin", GIT_BRANCH], capture_output=True, text=True)
        if res.returncode == 0:
            break
        time.sleep(3)
    else:
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

        time.sleep(6)

    raise TimeoutError(f"Workflow polling timed out for commit {commit_sha}")


def fetch_and_save_artifacts(run: dict, error_type: str, commit_sha: str):
    run_id = run["id"]

    # 1. Save workflow metadata
    metadata_path = METADATA_DIR / f"{run_id}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2)

    # 2. Download and aggregate raw logs
    logs_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/logs"
    log_path = LOGS_DIR / f"{run_id}.log"
    log_res = requests.get(logs_url, headers=HEADERS, stream=True, timeout=30)

    if log_res.status_code == 200:
        try:
            with zipfile.ZipFile(io.BytesIO(log_res.content)) as z:
                combined_log = ""
                for filename in sorted(z.namelist()):
                    if filename.endswith(".txt"):
                        step_text = z.read(filename).decode("utf-8", errors="replace")
                        combined_log += f"\n--- STEP: {filename} ---\n{step_text}"
                with open(log_path, "w", encoding="utf-8") as f:
                    f.write(combined_log)
        except zipfile.BadZipFile:
            with open(log_path, "wb") as f:
                f.write(log_res.content)
    else:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Log retrieval failed with HTTP {log_res.status_code}")

    # 3. Compute duration
    started_at = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
    completed_at = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
    duration = round((completed_at - started_at).total_seconds(), 2)

    # 4. Append row to labels.csv
    record = {
        "run_id": str(run_id),
        "repo_name": f"{REPO_OWNER}/{REPO_NAME}",
        "commit_sha": commit_sha,
        "workflow_id": WORKFLOW_FILE,
        "stage": "test",
        "failure_type": "F3",
        "error_type": error_type,
        "status": run.get("conclusion", "failure"),
        "duration": duration,
    }

    with open(LABELS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writerow(record)


def choose_weighted_random_error(error_keys: list) -> str:
    """
    Selects an error type randomly using subtle weighting based on least-recently-used history.
    - Base weight for every error: 1.0
    - Tiny boost per run since last seen: +0.1
    Maintains true randomness as the dominant factor while preventing starvation.
    """
    history = []
    if LABELS_FILE.exists():
        with open(LABELS_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("failure_type") == "F3" and row.get("error_type"):
                    history.append(row.get("error_type").strip())

    total_runs = len(history)
    weights = []

    for err in error_keys:
        if err in history:
            # Find steps since last occurrence
            steps_since = total_runs - 1 - (len(history) - 1 - history[::-1].index(err))
        else:
            # Never seen yet: treat as max age
            steps_since = max(total_runs, 10)

        # Base weight 1.0 + subtle 0.1 aging nudge per run
        weight = 1.0 + (steps_since * 0.1)
        weights.append(weight)

    selected = random.choices(error_keys, weights=weights, k=1)[0]
    return selected


def main():
    parser = argparse.ArgumentParser(description="Synthetic F3 Test Failure Generation Engine")
    parser.add_argument("--runs", type=int, default=500, help="Total target F3 runs (default: 500)")
    parser.add_argument("--clean", action="store_true", help="Purge prior F3 data before starting")
    args = parser.parse_args()

    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN not found in environment or .env file.")

    existing_f3_runs = sync_and_prepare_labels(clean_f3=args.clean)
    baseline_content = read_baseline_tests()
    error_keys = list(ERROR_MUTATIONS.keys())

    if existing_f3_runs >= args.runs:
        print(f"Target of {args.runs} F3 runs already reached ({existing_f3_runs} present). Exiting.")
        return

    print(f"Starting F3 generator. Resuming from run {existing_f3_runs + 1}/{args.runs}...")

    try:
        for i in range(existing_f3_runs + 1, args.runs + 1):
            selected_error = choose_weighted_random_error(error_keys)


            # Apply mutation
            write_test_mutation(baseline_content, selected_error)

            # Git commit and push
            commit_sha = git_commit_and_push(iteration=i, error_type=selected_error)

            # Poll run completion
            run_data = poll_workflow_run(commit_sha)

            # Save artifacts and labels
            fetch_and_save_artifacts(run_data, selected_error, commit_sha)

            print(f"[F3 Progress: {i}/{args.runs}] {selected_error} -> Run ID: {run_data['id']} ({run_data.get('conclusion')})")
            time.sleep(2)

    finally:
        # Guarantee local workspace and git tree return to clean baseline
        restore_baseline_tests(baseline_content)
        subprocess.run(["git", "add", str(TEST_FILE)], capture_output=True)
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff_check.returncode != 0:
            subprocess.run(["git", "commit", "-m", "chore: restore baseline tests"], capture_output=True)
            subprocess.run(["git", "push", "origin", GIT_BRANCH], capture_output=True)


if __name__ == "__main__":
    main()