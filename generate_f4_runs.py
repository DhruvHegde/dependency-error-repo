import random
import subprocess
import time
import re

TOTAL_RUNS = 1
TEST_FILE = "test_app.py"
BRANCH = "feature/timeout-errors"

TIMEOUT_TEMPLATES = [
    """
def test_timeout_{id}():
    value = {rand1}
    while value < {rand2}:
        value += 1
""",

    """
def test_timeout_{id}():
    counter = {rand1}
    while counter != {rand2}:
        counter += 1
""",

    """
def test_timeout_{id}():
    import time
    time.sleep(9999)
""",

    """
def test_timeout_{id}():
    while True:
        time.sleep({sleep_time})
""",
]


def run_git(cmd):
    subprocess.run(cmd, check=True, shell=True)


def get_max_variant():
    result = subprocess.run(
        [
            "git",
            "log",
            "--grep=inject timeout failure variant",
            "--oneline"
        ],
        capture_output=True,
        text=True
    )

    numbers = []

    for line in result.stdout.splitlines():
        match = re.search(r"variant (\d+)", line)

        if match:
            numbers.append(int(match.group(1)))

    return max(numbers) if numbers else 0


def generate_test_file(run_id):
    template = random.choice(TIMEOUT_TEMPLATES)

    content = template.format(
        id=run_id,
        rand1=random.randint(100, 999),
        rand2=random.randint(100000, 999999),
        sleep_time=random.randint(600, 900)
    )

    with open(TEST_FILE, "w") as f:
        f.write("import time\n")
        f.write(content)


def main():

    print(
        f"Starting push cycle up to "
        f"{TOTAL_RUNS} F4 timeout failures..."
    )

    while True:

        max_variant = get_max_variant()

        if max_variant >= TOTAL_RUNS:
            print(
                f"Reached {max_variant} runs "
                f"(target {TOTAL_RUNS}). Done!"
            )
            break

        next_id = max_variant + 1

        print(
            f"--> Pushing F4 run "
            f"{next_id}/{TOTAL_RUNS}"
        )

        generate_test_file(next_id)

        run_git(f"git add {TEST_FILE}")

        run_git(
            f'git commit -m '
            f'"test(F4): inject timeout failure variant {next_id}"'
        )

        try:

            run_git(
                f"git pull --rebase origin {BRANCH}"
            )

            run_git(
                f"git push origin {BRANCH}"
            )

        except subprocess.CalledProcessError:

            print(
                "Push/rebase failed. "
                "Aborting rebase and retrying..."
            )

            subprocess.run(
                "git rebase --abort",
                shell=True
            )

            run_git(
                f"git pull --rebase origin {BRANCH}"
            )

            run_git(
                f"git push origin {BRANCH}"
            )

        time.sleep(1)


if __name__ == "__main__":
    main()