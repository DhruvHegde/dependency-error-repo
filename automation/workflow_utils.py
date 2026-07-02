import json
import subprocess
import time

from config import (
    WORKFLOW_FILE,
    POLL_INTERVAL,
    MAX_WAIT
)


def run(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout.strip()


def get_workflow_runs():

    command = (
        f'gh run list '
        f'--workflow "{WORKFLOW_FILE}" '
        '--event push '
        '--limit 20 '
        '--json databaseId,headSha,status,conclusion'
    )

    output = run(command)

    return json.loads(output)


def wait_for_run(commit_sha):

    elapsed = 0

    while elapsed < MAX_WAIT:

        runs = get_workflow_runs()

        for workflow in runs:

            if workflow["headSha"] == commit_sha:

                print(
                    f'Workflow {workflow["databaseId"]} : '
                    f'{workflow["status"]}'
                )

                if workflow["status"] == "completed":
                    return workflow

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    raise TimeoutError(
        "Timed out waiting for GitHub Actions."
    )