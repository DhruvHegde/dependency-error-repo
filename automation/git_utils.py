import subprocess


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


def commit_and_push(message):

    run("git add .")

    run(f'git commit -m "{message}"')

    branch = run("git branch --show-current")
    run(f"git push origin {branch}")

    sha = run("git rev-parse HEAD")

    return sha