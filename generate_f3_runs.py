import os
import random
import subprocess
import time
import re

TOTAL_RUNS = 150
TEST_FILE = "test_app.py"

FAILURE_TEMPLATES = [
    """
def test_assertion_mismatch_{id}():
    expected = {rand1}
    actual = {rand2}
    assert expected == actual, f"Expected {{expected}} but got {{actual}}"
""",
    """
def test_index_out_of_bounds_{id}():
    data = [1, 2, 3]
    val = data[{rand1}]
    assert val > 0
""",
    """
def test_missing_dict_key_{id}():
    config = {{"timeout": 30, "retries": 3}}
    val = config["missing_key_{rand2}"]
    assert val == True
""",
    """
def test_type_mismatch_{id}():
    result = "string_value" + {rand1}
    assert result is not None
"""
]

def run_git(cmd):
    subprocess.run(cmd, check=True, shell=True)

def get_max_variant():
    res = subprocess.run(['git', 'log', '--grep=inject test failure variant', '--oneline'], capture_output=True, text=True)
    nums = []
    for line in res.stdout.splitlines():
        m = re.search(r'variant (\d+)', line)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0

def generate_test_file(run_id):
    template = random.choice(FAILURE_TEMPLATES)
    content = template.format(
        id=run_id,
        rand1=random.randint(100, 999),
        rand2=random.randint(1000, 9999)
    )
    with open(TEST_FILE, "w") as f:
        f.write("import pytest\n")
        f.write(content)

def main():
    print(f"Starting push cycle up to {TOTAL_RUNS} F3 test failures...")
    while True:
        max_var = get_max_variant()
        if max_var >= TOTAL_RUNS:
            print(f"Reached {max_var} runs (target {TOTAL_RUNS}). Done!")
            break
        
        next_id = max_var + 1
        print(f"--> Pushing run {next_id}/{TOTAL_RUNS}")
        generate_test_file(next_id)
        run_git(f"git add {TEST_FILE}")
        run_git(f'git commit -m "test(F3): inject test failure variant {next_id}"')
        try:
            run_git("git pull --rebase origin feature/test-failures")
            run_git("git push origin feature/test-failures")
        except subprocess.CalledProcessError:
            print("Push/pull encountered conflict or error, handling and retrying...")
            subprocess.run("git rebase --abort", shell=True)
            run_git("git pull --rebase origin feature/test-failures")
            run_git("git push origin feature/test-failures")
        time.sleep(1)

if __name__ == "__main__":
    main()
