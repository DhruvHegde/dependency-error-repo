import csv
import os


LABEL_COLUMNS = [
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


def append_label(row_data):
    file_exists = os.path.isfile("labels.csv")

    with open(
        "labels.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(LABEL_COLUMNS)

        writer.writerow(row_data)