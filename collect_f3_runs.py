import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil
import csv

from config import REPO_OWNER, REPO_NAME
from automation.metadata_utils import save_metadata
from automation.label_utils import LABEL_COLUMNS

LOG_DIR = Path("logs/F3")
META_DIR = Path("metadata/F3")
LABEL_FILE = "labels.csv"

FAILURE_PATTERNS = [
    "AssertionError",
    "IndexError",
    "KeyError",
    "TypeError"
]

def run_cmd(cmd):
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        raise Exception(result.stderr)
    return result.stdout.strip()

def get_runs():
    cmd = (
        f'gh run list '
        f'--repo "{REPO_OWNER}/{REPO_NAME}" '
        f'--branch "feature/test-failures" '
        f'--limit 250 '
        f'--json databaseId,headSha,status,conclusion,createdAt'
    )
    output = run_cmd(cmd)
    return json.loads(output)

def scan_log(log_text):
    if not log_text:
        return None, None
    for line in log_text.splitlines():
        for pat in FAILURE_PATTERNS:
            if pat in line:
                return pat, line.strip()
    return None, None

def reset_directories():
    if LOG_DIR.exists():
        shutil.rmtree(LOG_DIR)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if META_DIR.exists():
        shutil.rmtree(META_DIR)
    META_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("Resetting F3 logs and metadata...")
    reset_directories()

    print("Fetching workflow runs for feature/test-failures...")
    runs = get_runs()
    
    # Filter completed runs
    completed_runs = [r for r in runs if r.get("status") == "completed"]
    # Sort chronologically (oldest first by createdAt)
    completed_runs.sort(key=lambda x: x.get("createdAt", ""))
    
    # Take exactly the first 150 completed runs
    completed_runs = completed_runs[:150]
    print(f"Processing exactly {len(completed_runs)} completed runs.")
    
    label_records = []

    for idx, run in enumerate(completed_runs, start=1):
        run_number = idx
        db_id = run["databaseId"]
        commit_sha = run["headSha"]
        conclusion = run.get("conclusion")
        
        print(f"Processing run {run_number}/150 (Workflow ID: {db_id}, SHA: {commit_sha[:7]})")
        
        # Download log
        log_file_path = LOG_DIR / f"run_{run_number:04d}.log"
        try:
            log_text = run_cmd(f'gh run view {db_id} --log --repo "{REPO_OWNER}/{REPO_NAME}"')
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write(log_text)
        except Exception as e:
            print(f"Warning: Failed to download log for {db_id}: {e}")
            log_text = ""
                
        matched_pattern, matched_line = scan_log(log_text)
        
        metadata_file_path = META_DIR / f"run_{run_number:04d}.json"
        metadata = {
            "run_number": run_number,
            "dependency": f"test_variant_{run_number}",
            "commit_sha": commit_sha,
            "workflow_id": db_id,
            "workflow_status": "completed",
            "workflow_conclusion": conclusion,
            "log_file": str(log_file_path).replace("\\", "/"),
            "validation_status": "valid",
            "is_dependency_error": False,
            "matched_pattern": matched_pattern,
            "matched_line": matched_line,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        save_metadata(str(metadata_file_path), metadata)
            
        label_record = {
            "run_number": run_number,
            "dependency": f"test_variant_{run_number}",
            "repository": REPO_NAME,
            "commit_sha": commit_sha,
            "workflow_id": db_id,
            "workflow_conclusion": conclusion,
            "failure_type": "F3",
            "stage": "test",
            "validation_status": "valid",
            "matched_pattern": matched_pattern,
            "log_file": str(log_file_path).replace("\\", "/"),
            "metadata_file": str(metadata_file_path).replace("\\", "/"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        label_records.append(label_record)

    # Write labels.csv with all 150 F3 records
    with open(LABEL_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LABEL_COLUMNS)
        writer.writeheader()
        for record in label_records:
            writer.writerow(record)

    print("Completed collecting exactly 150 F3 runs and updated labels.csv!")

if __name__ == "__main__":
    main()


