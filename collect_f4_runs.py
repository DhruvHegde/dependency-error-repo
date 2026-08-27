import json
import csv
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from config import REPO_OWNER, REPO_NAME
from automation.metadata_utils import save_metadata
from automation.label_utils import LABEL_COLUMNS


LOG_DIR = Path("logs/F4")
META_DIR = Path("metadata/F4")
LABEL_FILE = "labels.csv"

BRANCH = "feature/timeout-errors"

TOTAL_RUNS = 500

FAILURE_PATTERNS = [
    "timed out after",
    "The action 'Run Tests' has timed out",
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
        f'--branch "{BRANCH}" '
        f'--workflow "timeout-ci.yml" '
        f'--limit 1000 '
        f'--json databaseId,headSha,status,conclusion,createdAt'
    )

    output = run_cmd(cmd)

    return json.loads(output)


def get_f4_commits():

    output = run_cmd(
        'git log --format="%H %s" '
        '--grep="F4 timeout variant" '
        '--all'
    )

    commits = {}

    for line in output.splitlines():

        if not line.strip():
            continue

        sha, message = line.split(" ", 1)

        match = re.search(
            r"F4 timeout variant (\d+)",
            message
        )

        if match:

            run_number = int(
                match.group(1)
            )

            commits[run_number] = sha

    return commits


def scan_log(log_text):

    if not log_text:
        return None, None

    for line in log_text.splitlines():

        for pattern in FAILURE_PATTERNS:

            if pattern.lower() in line.lower():

                return pattern, line.strip()

    return None, None


def reset_directories():

    if LOG_DIR.exists():
        shutil.rmtree(LOG_DIR)

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if META_DIR.exists():
        shutil.rmtree(META_DIR)

    META_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def main():

    print(
        "Resetting F4 logs and metadata..."
    )

    reset_directories()

    print(
        f"Fetching workflow runs for {BRANCH}..."
    )

    runs = get_runs()

    print(
        "Finding generated F4 commits..."
    )

    f4_commits = get_f4_commits()

    print(
        f"Found {len(f4_commits)} "
        f"generated F4 commits."
    )

    if not f4_commits:

        print(
            "No F4 generator commits found."
        )

        return

    completed_runs = []

    for run in runs:

        sha = run.get("headSha")

        if sha not in f4_commits.values():
            continue

        if run.get("status") != "completed":
            continue

        completed_runs.append(run)

    completed_runs.sort(
        key=lambda x: f4_commits.get(
            x["headSha"],
            999999
        )
    )

    completed_runs = completed_runs[
        :TOTAL_RUNS
    ]

    print(
        f"Processing {len(completed_runs)} "
        f"completed F4 runs."
    )

    label_records = []

    for run in completed_runs:

        commit_sha = run["headSha"]

        run_number = f4_commits[
            commit_sha
        ]

        db_id = run["databaseId"]

        conclusion = run.get(
            "conclusion"
        )

        print(
            f"Processing F4 run "
            f"{run_number}/{TOTAL_RUNS} "
            f"(Workflow ID: {db_id}, "
            f"SHA: {commit_sha[:7]})"
        )

        log_file_path = (
            LOG_DIR /
            f"run_{run_number:04d}.log"
        )

        try:

            log_text = run_cmd(
                f'gh run view {db_id} '
                f'--log '
                f'--repo "{REPO_OWNER}/{REPO_NAME}"'
            )

            with open(
                log_file_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(log_text)

        except Exception as e:

            print(
                f"Warning: Failed to download "
                f"log for {db_id}: {e}"
            )

            log_text = ""

            with open(
                log_file_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write("")

        matched_pattern, matched_line = scan_log(
            log_text
        )

        validation_status = (
            "valid"
            if matched_pattern
            else "invalid"
        )

        metadata_file_path = (
            META_DIR /
            f"run_{run_number:04d}.json"
        )

        timestamp = (
            datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

        metadata = {

            "run_number":
                run_number,

            "dependency":
                f"timeout_variant_{run_number}",

            "commit_sha":
                commit_sha,

            "workflow_id":
                db_id,

            "workflow_status":
                "completed",

            "workflow_conclusion":
                conclusion,

            "log_file":
                str(log_file_path).replace(
                    "\\",
                    "/"
                ),

            "validation_status":
                validation_status,

            "is_dependency_error":
                False,

            "matched_pattern":
                matched_pattern,

            "matched_line":
                matched_line,

            "timestamp":
                timestamp
        }

        save_metadata(
            str(metadata_file_path),
            metadata
        )

        label_record = {

            "run_number":
                run_number,

            "dependency":
                f"timeout_variant_{run_number}",

            "repository":
                REPO_NAME,

            "commit_sha":
                commit_sha,

            "workflow_id":
                db_id,

            "workflow_conclusion":
                conclusion,

            "failure_type":
                "F4",

            "stage":
                "test",

            "validation_status":
                validation_status,

            "matched_pattern":
                matched_pattern,

            "log_file":
                str(log_file_path).replace(
                    "\\",
                    "/"
                ),

            "metadata_file":
                str(metadata_file_path).replace(
                    "\\",
                    "/"
                ),

            "timestamp":
                timestamp
        }

        label_records.append(
            label_record
        )

    with open(
        LABEL_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=LABEL_COLUMNS
        )

        writer.writeheader()

        for record in label_records:

            writer.writerow(record)

    print(
        f"Completed collecting "
        f"{len(label_records)} F4 runs."
    )


if __name__ == "__main__":
    main()