import json
import csv
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import REPO_OWNER, REPO_NAME
from automation.metadata_utils import save_metadata
from automation.label_utils import LABEL_COLUMNS


LOG_DIR = Path("logs/F4")
META_DIR = Path("metadata/F4")
LABEL_FILE = "labels.csv"

BRANCH = "feature/timeout-errors"
WORKFLOW = "timeout-ci.yml"

TARGET_VALID = 500

OLD_VARIANT_MAX = 500
NEW_VARIANT_MIN = 501
NEW_VARIANT_MAX = 758

MAX_WORKERS = 12

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

            variant = int(match.group(1))

            commits[variant] = sha

    return commits


def scan_log(log_text):

    if not log_text:
        return None, None

    for line in log_text.splitlines():

        for pattern in FAILURE_PATTERNS:

            if pattern.lower() in line.lower():

                return pattern, line.strip()

    return None, None


def download_log(run):

    db_id = run["databaseId"]

    try:

        log_text = run_cmd(
            f'gh run view {db_id} '
            f'--log '
            f'--repo "{REPO_OWNER}/{REPO_NAME}"'
        )

        return run, log_text, None

    except Exception as e:

        return run, "", str(e)


def main():

    print("Fetching generated F4 runs...")

    runs = get_runs()

    print(f"GitHub returned {len(runs)} runs.")

    print("Finding F4 generator commits...")

    commits = get_f4_commits()

    print(
        f"Found {len(commits)} generated F4 commits."
    )

    sha_to_variant = {
        sha: variant
        for variant, sha in commits.items()
    }

    generated_runs = []

    for run in runs:

        sha = run.get("headSha")

        if sha not in sha_to_variant:
            continue

        if run.get("status") != "completed":
            continue

        generated_runs.append(run)

    print(
        f"Found {len(generated_runs)} "
        f"completed generated runs."
    )

    # Only failed runs can possibly contain the timeout failure.
    failed_runs = [
        run
        for run in generated_runs
        if run.get("conclusion") == "failure"
    ]

    print(
        f"Only downloading logs for "
        f"{len(failed_runs)} failed runs."
    )

    old_failed = []
    replacement_failed = []

    for run in failed_runs:

        variant = sha_to_variant[
            run["headSha"]
        ]

        if variant <= OLD_VARIANT_MAX:

            old_failed.append(run)

        elif (
            NEW_VARIANT_MIN
            <= variant
            <= NEW_VARIANT_MAX
        ):

            replacement_failed.append(run)

    print(
        f"Original failed runs: "
        f"{len(old_failed)}"
    )

    print(
        f"Replacement failed runs: "
        f"{len(replacement_failed)}"
    )

    # Download old failed logs in parallel.
    print("Checking original F4 failures...")

    old_valid = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                download_log,
                run
            )
            for run in old_failed
        ]

        completed = 0

        for future in as_completed(futures):

            run, log_text, error = future.result()

            completed += 1

            variant = sha_to_variant[
                run["headSha"]
            ]

            if error:

                print(
                    f"[{completed}/{len(old_failed)}] "
                    f"Variant {variant}: "
                    f"log download failed"
                )

                continue

            matched_pattern, matched_line = scan_log(
                log_text
            )

            if matched_pattern:

                old_valid.append(
                    (
                        run,
                        log_text,
                        matched_pattern,
                        matched_line
                    )
                )

                print(
                    f"[{completed}/{len(old_failed)}] "
                    f"Variant {variant}: VALID"
                )

            else:

                print(
                    f"[{completed}/{len(old_failed)}] "
                    f"Variant {variant}: not F4"
                )

    print(
        f"Found {len(old_valid)} "
        f"valid original F4 runs."
    )

    if len(old_valid) < 242:

        raise RuntimeError(
            f"Expected at least 242 valid "
            f"original F4 runs, found "
            f"{len(old_valid)}."
        )

    # We need exactly 242 from the original dataset.
    old_valid.sort(
        key=lambda item:
        sha_to_variant[
            item[0]["headSha"]
        ]
    )

    old_valid = old_valid[:242]

    # All replacement variants are deliberately
    # guaranteed timeout tests.
    #
    # Download their logs so the final dataset
    # contains the actual GitHub Actions output.
    print(
        f"Downloading {len(replacement_failed)} "
        f"replacement F4 logs..."
    )

    replacement_results = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [
            executor.submit(
                download_log,
                run
            )
            for run in replacement_failed
        ]

        completed = 0

        for future in as_completed(futures):

            run, log_text, error = future.result()

            completed += 1

            variant = sha_to_variant[
                run["headSha"]
            ]

            if error:

                print(
                    f"[{completed}/{len(replacement_failed)}] "
                    f"Variant {variant}: DOWNLOAD FAILED"
                )

                continue

            matched_pattern, matched_line = scan_log(
                log_text
            )

            if matched_pattern:

                replacement_results.append(
                    (
                        run,
                        log_text,
                        matched_pattern,
                        matched_line
                    )
                )

                print(
                    f"[{completed}/{len(replacement_failed)}] "
                    f"Variant {variant}: VALID"
                )

            else:

                print(
                    f"[{completed}/{len(replacement_failed)}] "
                    f"Variant {variant}: INVALID"
                )

    print(
        f"Valid replacement F4 runs: "
        f"{len(replacement_results)}"
    )

    if len(replacement_results) < 258:

        raise RuntimeError(
            f"Expected 258 valid replacement "
            f"F4 runs, found "
            f"{len(replacement_results)}."
        )

    replacement_results.sort(
        key=lambda item:
        sha_to_variant[
            item[0]["headSha"]
        ]
    )

    replacement_results = replacement_results[:258]

    # Combine:
    #
    # 242 original valid F4
    # +
    # 258 replacement valid F4
    #
    # = 500
    all_valid = (
        old_valid +
        replacement_results
    )

    if len(all_valid) != TARGET_VALID:

        raise RuntimeError(
            f"Final dataset contains "
            f"{len(all_valid)} runs instead of "
            f"{TARGET_VALID}."
        )

    # Recreate output directories.
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    META_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Sort deterministically.
    all_valid.sort(
        key=lambda item:
        sha_to_variant[
            item[0]["headSha"]
        ]
    )

    label_records = []

    print("Writing final 500-run dataset...")

    for final_number, (
        run,
        log_text,
        matched_pattern,
        matched_line
    ) in enumerate(
        all_valid,
        start=1
    ):

        commit_sha = run["headSha"]

        db_id = run["databaseId"]

        conclusion = run.get(
            "conclusion"
        )

        original_variant = sha_to_variant[
            commit_sha
        ]

        log_file = (
            LOG_DIR /
            f"run_{final_number:04d}.log"
        )

        metadata_file = (
            META_DIR /
            f"run_{final_number:04d}.json"
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
            .replace(
                "+00:00",
                "Z"
            )
        )

        metadata = {

            "run_number":
                final_number,

            "source_variant":
                original_variant,

            "dependency":
                f"timeout_variant_{original_variant}",

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
                final_number,

            "dependency":
                f"timeout_variant_{original_variant}",

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

        writer.writerows(
            label_records
        )

    print(
        "======================================"
    )

    print(
        "F4 DATASET COMPLETE"
    )

    print(
        f"Valid F4 records: {len(label_records)}"
    )

    print(
        "======================================"
    )


if __name__ == "__main__":
    main()