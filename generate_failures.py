import os
import json
import time
from automation.git_utils import commit_and_push
from automation.workflow_utils import wait_for_run, download_logs
from config import TOTAL_RUNS, LOG_FOLDER, METADATA_FOLDER, FAILURE_TYPE

def load_scenarios():
    with open("deployment_errors.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def main():
    scenarios = load_scenarios()
    os.makedirs(LOG_FOLDER, exist_ok=True)
    os.makedirs(METADATA_FOLDER, exist_ok=True)
    
    print(f"Starting generation for {TOTAL_RUNS} runs of {FAILURE_TYPE}...")
    
    for i in range(1, TOTAL_RUNS + 1):
        scenario = scenarios[i % len(scenarios)]
        print(f"\n--- Run {i}/{TOTAL_RUNS}: {scenario} ---")
        
        # Modify a state file to force a Git commit
        state_file = f"state_{FAILURE_TYPE.lower()}.json"
        with open(state_file, "w") as f:
            json.dump({"run": i, "scenario": scenario}, f)
            
        sha = commit_and_push(f"Auto-trigger F4: {scenario} run {i}")
        if not sha:
            print("Commit failed, skipping...")
            continue
            
        print(f"Waiting for workflow on commit {sha[:7]}...")
        time.sleep(10) # Buffer for Actions to register
        
        # This will use your team's existing workflow_utils to grab the data
        status = wait_for_run(sha)
        print(f"Workflow finished with status: {status}")
        
        # Download and format
        download_logs(sha, i, LOG_FOLDER, METADATA_FOLDER)
        print(f"Saved logs and metadata for run {i}")

if __name__ == "__main__":
    main()