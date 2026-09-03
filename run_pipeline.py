import argparse
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Unified CI/CD Failure Generation & Collection Pipeline")
    parser.add_argument("--category", type=str, default="F3", choices=["F2", "F3"], help="Failure category to generate and collect")
    parser.add_argument("--runs", type=int, default=8, help="Number of runs to execute")
    parser.add_argument("--clean", action="store_true", help="Clean prior category data and logs before execution")
    args = parser.parse_args()

    print(f"=== Unified Pipeline Runner: Category {args.category} ===")

    if args.category == "F3":
        cmd = [sys.executable, "generate_f3_runs.py", "--runs", str(args.runs)]
        if args.clean:
            cmd.append("--clean")
        
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    elif args.category == "F2":
        print("Category F2 currently uses legacy generator (generate_failures.py).")
        cmd = [sys.executable, "generate_failures.py"]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    else:
        print(f"Unknown category: {args.category}")
        sys.exit(1)

if __name__ == "__main__":
    main()
