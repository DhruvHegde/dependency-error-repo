from automation.git_utils import commit_and_push

def load_dependencies():
    with open("dependency_errors.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def update_requirements(package):
    with open("requirements.txt", "w") as f:
        f.write(package + "\n")

def main():
    dependencies = load_dependencies()

    package = dependencies[0]

    print(f"Using dependency: {package}")

    update_requirements(package)

    commit_and_push(f"Generate dependency error: {package}")

if __name__ == "__main__":
    main()