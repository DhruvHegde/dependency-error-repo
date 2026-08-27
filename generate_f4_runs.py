import random
import subprocess
import re
import time

TOTAL_REPLACEMENTS = 258
START_VARIANT = 501
TEST_FILE = "test_app.py"
BRANCH = "feature/timeout-errors"


def run_git(cmd):
    subprocess.run(cmd, check=True, shell=True)


def get_existing_variants():
    result = subprocess.run(
        [
            "git",
            "log",
            "--format=%s",
            "--all"
        ],
        capture_output=True,
        text=True
    )

    variants = set()

    for line in result.stdout.splitlines():

        match = re.search(
            r"F4 timeout variant (\d+)",
            line
        )

        if match:
            variants.add(
                int(match.group(1))
            )

    return variants


def generate_test_file(run_id):

    sleep_time = random.randint(600, 900)

    content = f"""import time

def test_timeout_{run_id}():
    while True:
        time.sleep({sleep_time})
"""

    with open(TEST_FILE, "w") as f:
        f.write(content)


def main():

    existing_variants = get_existing_variants()

    target_variants = range(
        START_VARIANT,
        START_VARIANT + TOTAL_REPLACEMENTS
    )

    remaining = [
        n for n in target_variants
        if n not in existing_variants
    ]

    print(
        f"Need to generate "
        f"{len(remaining)} replacement F4 runs."
    )

    for index, variant in enumerate(
        remaining,
        start=1
    ):

        print(
            f"--> Pushing replacement "
            f"{index}/{len(remaining)} "
            f"(variant {variant})"
        )

        generate_test_file(variant)

        run_git(
            f"git add {TEST_FILE}"
        )

        run_git(
            f'git commit -m '
            f'"test(F4): inject timeout failure variant {variant}"'
        )

        run_git(
            f"git pull --rebase origin {BRANCH}"
        )

        run_git(
            f"git push origin {BRANCH}"
        )

        time.sleep(1)

    print("Replacement generation complete.")


if __name__ == "__main__":
    main()