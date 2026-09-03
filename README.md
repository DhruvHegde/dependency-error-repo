# CI/CD Failure Predictor & Dataset Generator (`log-generation`)

An automated synthetic failure generation and dataset collection framework designed to generate, execute, collect, and label real-world GitHub Actions CI/CD failure logs for training machine learning models in failure prediction, classification, and automated root-cause analysis.

---

## 🌐 1. Project-Wide Overview & Failure Taxonomy

In modern software engineering, CI/CD pipeline failures occur across different lifecycle stages. This Capstone project models and collects failure datasets across 5 standardized failure categories:

| Category | Failure Domain | Stage | Description | Branch Name |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | **Syntax / Code Errors** | `build` | Broken Python syntax, invalid indentation, unparseable code. | `feature/syntax-errors` |
| **F2** | **Dependency Errors** | `build` | Invalid `requirements.txt`, impossible package versions, missing packages. | `main` |
| **F3** | **Test Failures** *(This Branch)* | `test` | Controlled runtime exceptions, assertion errors, and Pytest test failures. | `feature/f3-test-failures` |
| **F4** | **Deployment / Env Errors** | `deploy` | Missing environment variables, broken release scripts, port conflicts. | `feature/f4-deployment-errors` |
| **Timeout** | **Workflow Timeouts** | `runtime` | Long-running jobs, hanging processes, infinite loops. | `feature/timeout-errors` |

---

## 🎯 2. Category F3 Role: Controlled Test Failures (`feature/f3-test-failures`)

This branch is specifically dedicated to **Category F3 (Controlled Test Failures)**.

### Mission & Responsibilities
1. **Scaffolding:** Maintain a testable baseline application (`src/app.py`) and test suite (`tests/test_app.py`).
2. **Synthetic Mutation Engine:** Dynamically inject 8 specific Python exception and assertion error types into the test suite.
3. **CI Execution:** Trigger and monitor dedicated GitHub Actions runs (`.github/workflows/f3_test.yml`).
4. **Log & Metadata Harvesting:** Automatically download raw console logs (`logs/F3/{run_id}.log`) and workflow JSON metadata (`metadata/F3/{run_id}.json`).
5. **Unified Dataset Registry (`labels.csv`):** Record run ID, commit SHA, error type, conclusion status, and duration while strictly protecting teammate data (`F1`, `F2`, `F4`).

---

## 🧪 3. The 8 Target Pytest Failure Mutations

Category F3 simulates realistic test failures mapping to 8 standard Python runtime exceptions and assertions:

| Error Type | Function Target | Mutation / Failure Trigger |
| :--- | :--- | :--- |
| **`AssertionError`** | `assert_positive(n)` | Passes negative number (`-5`), failing the assertion check. |
| **`IndexError`** | `get_list_item(lst, index)` | Accesses out-of-bounds list index (`999`). |
| **`KeyError`** | `get_dict_value(d, key)` | Accesses non-existent dictionary key (`"missing_key"`). |
| **`TypeError`** | `calculate_division(a, b)` | Passes non-numeric string type (`"two"`) instead of integer/float. |
| **`ValueError`** | `convert_to_int(val)` | Passes non-numeric string (`"not_an_int"`) to integer conversion. |
| **`AttributeError`** | `get_object_attribute(obj)` | Accesses undefined attribute on a dummy object. |
| **`ZeroDivisionError`** | `calculate_division(a, b)` | Passes denominator `b = 0`. |
| **`FileNotFoundError`** | `read_config_file(path)` | Attempts to open a non-existent configuration file path. |


### Mutation Selection Strategy
Error selection uses **weighted random sampling**. Every error starts with a base weight (`1.0`), and receives a subtle, incremental nudge (`+0.1`) for every run since it was last generated. This ensures true randomness dominates, while providing a mild preference for errors that haven't appeared recently to prevent starvation.

---

## 📂 4. Repository Directory Structure (Branch: `feature/f3-test-failures`)

```text
log-generation/
├── .github/workflows/
│   ├── ci.yml                 # Legacy CI workflow for F2 (Dependency Errors)
│   └── f3_test.yml            # Dedicated GitHub Actions CI workflow for Category F3
├── logs/
│   ├── F2/                    # Output logs for Category F2
│   └── F3/                    # Output raw console logs for Category F3 (*.log)
├── metadata/
│   ├── F2/                    # Run metadata for Category F2
│   └── F3/                    # Output workflow JSON metadata for Category F3 (*.json)
├── src/
│   └── app.py                 # Baseline testable application functions (F3)
├── tests/
│   └── test_app.py            # Baseline Pytest test suite (F3)
├── dataset_pipeline.py        # Unified orchestrator (Generator + Collector CLI)
├── generate_f3_runs.py        # Core failure generation, REST polling, and label engine
├── labels.csv                 # Master dataset run registry & labels
├── .env.example               # Template for environment configuration
└── README.md                  # Complete project & branch documentation
```

---

## 🚀 5. How to Run the Pipeline

Run the end-to-end dataset generation and collection pipeline with a single unified command:

```bash
python dataset_pipeline.py --category F3 --runs 8 --clean
```

### Breakdown of the Run Command
* **`python`**: The Python runtime interpreter.
* **`dataset_pipeline.py`**: The unified pipeline runner that handles failure injection, git commits, pushing to GitHub, polling GitHub Actions API, downloading logs, extracting metadata, updating `labels.csv`, and restoring the baseline.
* **`--category F3`**: Selects Category F3 (Controlled Test Failures).
* **`--runs 8`**: Executes 8 iterations covering all 8 Pytest error mutations.
* **`--clean`**: Purges prior F3 logs/metadata before starting fresh. *(Protects all non-F3 teammate rows in `labels.csv`).*

---

## ⚙️ 6. Execution Modes

1. **Clean / Fresh Generation Mode (`--clean` passed):**
   * Purges previous F3 logs in `logs/F3/`, metadata in `metadata/F3/`, and prior F3 label entries.
   * **Teammate Safety Guarantee:** Preserves all non-F3 rows (`F1`, `F2`, `F4`, etc.) in their original order.
   * Starts fresh from run 1 up to `--runs`.

2. **Resumption / Append Mode (No `--clean`):**
   * Inspects existing F3 runs in `labels.csv` and directories.
   * Skips completed runs and **appends** new F3 runs until the target `--runs` count is reached.

---

## 📊 7. Dataset Schema (`labels.csv`)

Master CSV schema tracking all dataset runs across all categories:
```csv
run_id,repo_name,commit_sha,workflow_id,stage,failure_type,error_type,status,duration
```
* **`run_id`**: GitHub Actions workflow run database ID (e.g., `33663993993`).
* **`repo_name`**: Target GitHub repository (`DhruvHegde/dependency-error-repo`).
* **`commit_sha`**: Full 40-character Git commit hash triggering the CI run.
* **`workflow_id`**: Workflow file name (`f3_test.yml`).
* **`stage`**: Pipeline failure stage (`test` for F3, `build` for F1/F2, `deploy` for F4).
* **`failure_type`**: Category code (`F1`, `F2`, `F3`, `F4`).
* **`error_type`**: Specific error injected (e.g., `AssertionError`, `IndexError`, etc.).
* **`status`**: Conclusion status (`failure` or `success`).
* **`duration`**: Total job execution duration in seconds.

