from automation.git_utils import commit_and_push
from automation.state_utils import load_state, save_state

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

    update_requirements(package)

    commit_and_push(
        f"Dependency Error Run {current+1}"
    )

    state["current_run"] += 1
    state["last_dependency"] = package

    save_state(state)


if __name__ == "__main__":
    main()