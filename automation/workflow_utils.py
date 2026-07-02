import json
import subprocess
import time

from config import POLL_INTERVAL, MAX_WAIT


def run(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout


def get_runs():

    cmd = (
        "gh run list "
        "--limit 20 "
        "--json databaseId,headSha,status,conclusion"
    )

    output = run(cmd)

    return json.loads(output)


def wait_for_run(commit_sha):

    waited = 0

    while waited < MAX_WAIT:

        runs = get_runs()

        for workflow in runs:

            if workflow["headSha"] == commit_sha:

                print(
                    f"Found workflow {workflow['databaseId']} "
                    f"Status: {workflow['status']}"
                )

                if workflow["status"] == "completed":
                    return workflow

        time.sleep(POLL_INTERVAL)

        waited += POLL_INTERVAL

    raise TimeoutError("Workflow not found.")