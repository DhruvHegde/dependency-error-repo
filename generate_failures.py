from numpy import rint

from automation.git_utils import commit_and_push
from automation.log_utils import download_workflow_log
from automation.state_utils import load_state, save_state
from automation.validator import validate_workflow_log_file
from automation.workflow_utils import wait_for_run

from config import TOTAL_RUNS


def load_dependencies():
    with open("dependency_errors.txt") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]


def update_requirements(package):
    with open("requirements.txt", "w") as f:
        f.write(package + "\n")


def main():

    dependencies = load_dependencies()

    state = load_state()

    current = state["current_run"]

    if current >= TOTAL_RUNS:
        print("Dataset generation complete.")
        return

    dependencies = load_dependencies()
    print(dependencies)
    print("Current index:", current)
    package = dependencies[current % len(dependencies)]

    print(f"Run {current+1}")
    print(f"Dependency: {package}")

    try:
        update_requirements(package)

        sha = commit_and_push(
            f"Dependency Error Run {current+1}"
        )
        print("Commit SHA:", sha)

        workflow = wait_for_run(sha)
        print(f"Workflow completed: {workflow['databaseId']}")

        log_path = download_workflow_log(workflow, current+1)
        print(f"Downloaded log: {log_path}")

        validation = validate_workflow_log_file(log_path)
        print(f"Validation result: {validation['status']}")
        print(f"Dependency error: {validation['is_dependency_error']}")

        if validation["matched_pattern"] is not None:
            print(f"Matched pattern: {validation['matched_pattern']}")

        if validation["matched_line"] is not None:
            print(f"Matched line: {validation['matched_line']}")

        if validation["status"] != "valid":
            if validation["status"] == "error":
                print(f"Validation error: log file could not be read or was missing: {log_path}")
            else:
                print(f"Validation failed: log does not contain a known dependency error pattern: {log_path}")
            print("Current run failed validation and state was not advanced.")
            return

        state["current_run"] += 1
        state["last_dependency"] = package
        save_state(state)
    except Exception as exc:
        print("Exception type:", type(exc))
        print("Exception repr:", repr(exc))
        print("Exception str:", str(exc))
        raise

    # except Exception as exc:
    #     print(f"Error during dependency run {current+1}: {exc}")
    #     print("Current run failed and state was not advanced.")
    #     return


if __name__ == "__main__":
    main()