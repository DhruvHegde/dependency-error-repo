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


def get_latest_run():

    command = (
        "gh run list "
        "--limit 1 "
        "--json databaseId,status,conclusion"
    )

    output = run(command)

    data = json.loads(output)

    if not data:
        return None

    return data[0]


def wait_for_completion():

    waited = 0

    while waited < MAX_WAIT:

        run_info = get_latest_run()

        if run_info is None:
            time.sleep(POLL_INTERVAL)
            waited += POLL_INTERVAL
            continue

        status = run_info["status"]

        print(f"Workflow status: {status}")

        if status == "completed":
            return run_info

        time.sleep(POLL_INTERVAL)
        waited += POLL_INTERVAL

    raise TimeoutError("Workflow did not finish within the timeout.")