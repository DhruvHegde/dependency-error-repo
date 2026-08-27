import json
import csv
import re
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
WORKFLOW = "timeout-ci.yml"

TARGET_VALID = 500

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

    output = run_cmd(
        f'gh run list '
        f'--repo "{REPO_OWNER}/{REPO_NAME}" '
        f'--branch "{BRANCH}" '
        f'--workflow "{WORKFLOW}" '
        f'--limit 1000 '
        f'--json databaseId,headSha,status,conclusion,createdAt'
    )

    return json.loads(output)


def get_f4_commits():

    output = run_cmd(
        'git log --format="%H %s" --all '
        '--grep="inject timeout failure variant"'
    )

    commits = {}

    for line in output.splitlines():

        if not line.strip():
            continue

        sha, message = line.split(" ", 1)

        match = re.search(
            r"inject timeout failure variant (\d+)",
            message
        )

        if match:
            commits[
                int(match.group(1))
            ] = sha

    return commits


def scan_log(log_text):

    if not log_text:
        return None, None

    for line in log_text.splitlines():

        for pattern in FAILURE_PATTERNS:

            if pattern.lower() in line.lower():
                return pattern, line.strip()

    return None, None


def main():

    runs = get_runs()
    commits = get_f4_commits()

    sha_to_variant = {
        sha: variant
        for variant, sha in commits.items()
    }

    print(
        f"Found {len(commits)} generated F4 commits."
    )

    candidates = []

    for run in runs:

        sha = run.get("headSha")

        if sha not in sha_to_variant:
            continue

        if run.get("status") != "completed":
            continue

        candidates.append(run)

    candidates.sort(
        key=lambda r: sha_to_variant[
            r["headSha"]
        ]
    )

    print(
        f"Found {len(candidates)} completed "
        f"generated runs."
    )

    # First collect all genuinely valid timeout runs.
    valid_runs = []

    for run in candidates:

        db_id = run["databaseId"]

        try:

            log_text = run_cmd(
                f'gh run view {db_id} --log '
                f'--repo "{REPO_OWNER}/{REPO_NAME}"'
            )

        except Exception:
            continue

        matched_pattern, matched_line = scan_log(
            log_text
        )

        if matched_pattern:

            valid_runs.append(
                (
                    run,
                    log_text,
                    matched_pattern,
                    matched_line
                )
            )

    print(
        f"Found {len(valid_runs)} "
        f"genuine F4 timeout runs."
    )

    if len(valid_runs) < TARGET_VALID:

        raise RuntimeError(
            f"Only {len(valid_runs)} valid F4 runs found. "
            f"Need {TARGET_VALID}."
        )

    # Keep exactly 500 valid runs.
    valid_runs = valid_runs[:TARGET_VALID]

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    META_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    label_records = []

    for index, (
        run,
        log_text,
        matched_pattern,
        matched_line
    ) in enumerate(
        valid_runs,
        start=1
    ):

        run_number = index

        db_id = run["databaseId"]
        commit_sha = run["headSha"]
        conclusion = run.get("conclusion")

        log_file = (
            LOG_DIR /
            f"run_{run_number:04d}.log"
        )

        metadata_file = (
            META_DIR /
            f"run_{run_number:04d}.json"
        )

        with open(
            log_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(log_text)

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
                str(log_file).replace(
                    "\\",
                    "/"
                ),

            "validation_status":
                "valid",

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
            str(metadata_file),
            metadata
        )

        label_records.append({

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
                "valid",

            "matched_pattern":
                matched_pattern,

            "log_file":
                str(log_file).replace(
                    "\\",
                    "/"
                ),

            "metadata_file":
                str(metadata_file).replace(
                    "\\",
                    "/"
                ),

            "timestamp":
                timestamp
        })

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
        writer.writerows(label_records)

    print(
        f"Successfully created "
        f"{len(label_records)} valid F4 labels."
    )


if __name__ == "__main__":
    main()