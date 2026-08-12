import subprocess


def run(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return result.stdout.strip()

def commit_and_push(message):
    print("Adding files...")
    run("git add .")

    print("Committing...")
    run(f'git commit -m "{message}"')

    print("Getting branch...")
    branch = run("git branch --show-current")
    print("Branch:", branch)

    print("Pushing...")
    run(f"git push origin {branch}")

    print("Getting SHA...")
    sha = run("git rev-parse HEAD")

    return sha


# def commit_and_push(message):

#     run("git add .")

#     run(f'git commit -m "{message}"')

#     branch = run("git branch --show-current")
#     run(f"git push origin {branch}")

#     sha = run("git rev-parse HEAD")

#     return sha