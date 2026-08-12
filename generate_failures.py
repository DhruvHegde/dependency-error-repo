from automation.git_utils import commit_and_push
from automation.log_utils import download_workflow_log
from automation.state_utils import load_state, save_state
from automation.workflow_utils import wait_for_run

from config import TOTAL_RUNS


def load_dependencies():
    with open("dependency_errors.txt") as f:
        return [x.strip() for x in f if x.strip()]


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

        state["current_run"] += 1
        state["last_dependency"] = package
        save_state(state)

    except Exception as exc:
        print(f"Error during dependency run {current+1}: {exc}")
        print("Current run failed and state was not advanced.")
        return


if __name__ == "__main__":
    main()