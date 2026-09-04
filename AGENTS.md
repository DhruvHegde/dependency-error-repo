# Repository Agent Guide

## F3 Scope

This repository generates synthetic GitHub Actions test-failure data. F3 is the active workflow. It injects one supported mutation into `tests/test_app.py`, runs matrix jobs, collects logs and metadata, and appends normalized records to `labels.csv`.

F2 is a separate legacy dependency-failure path. F1, F2, F4, and Timeout are taxonomy categories, not interchangeable F3 implementations. Work only on F3 unless the user explicitly asks for another category.

## Authoritative Files

Use these files as the source of truth:

- `generate_f3_runs.py`: F3 orchestration, batching, random selection, GitHub polling, cleanup, artifact collection, and labeling.
- `.github/workflows/f3_test.yml`: F3 CI execution and matrix contract.
- `.f3_batch.json`: generated matrix entries for the current batch.
- `automation/inject_mutation.py`: supported mutation definitions.
- `src/app.py`: baseline application functions.
- `tests/test_app.py`: baseline tests and injected failure tests.
- `labels.csv`: dataset registry and current CSV schema.
- `pytest.ini`: local pytest configuration.

`README.md` provides general background but may contain stale F3 claims. Trust the implementation and current CSV schema over conflicting README examples.

## F3 Workflow

The generator:

1. Normalizes `labels.csv` and preserves non-F3 rows.
2. Calculates how many F3 records remain to reach `--runs`.
3. Selects error types using weighted random selection.
4. Writes the selected entries to `.f3_batch.json`.
5. Adds a trigger comment to `tests/test_app.py`.
6. Commits and pushes to `feature/f3-test-failures`.
7. Polls GitHub Actions for the matching commit and completed workflow.
8. Reports each completed matrix job while the batch is running.
9. Collects matrix job metadata and raw job logs.
10. Appends one label record per collected job.

The workflow has a preparation job that reads `.f3_batch.json`, then creates a dynamic test matrix. Each batch contains between 1 and 250 jobs, uses Python 3.11, has `fail-fast: false`, and allows up to 250 parallel jobs. Each test job injects one mutation and runs:

```text
pytest tests/test_app.py -v
```

For 500 requested records, generation uses two serialized batches of 250 jobs. A smaller final batch is used when the remaining target is below 250.

## Random Selection

The supported error types are:

- `AssertionError`
- `IndexError`
- `KeyError`
- `TypeError`
- `ValueError`
- `AttributeError`
- `ZeroDivisionError`
- `FileNotFoundError`

Selection uses `random.Random(seed).choices()`. The weight for an error type is inversely related to its existing F3 count:

```text
weight = 1.0 / (1.0 + historical_count)
```

This gently favors error types that have appeared less often while still allowing duplicates. Selection does not guarantee equal distribution or one instance of every error type. When `--seed` is supplied, each batch uses a deterministic seed derived from the supplied seed and batch number.

## Labels And Artifacts

The exact `labels.csv` header is:

```text
run_number,dependency,repository,commit_sha,workflow_id,workflow_conclusion,failure_type,stage,validation_status,matched_pattern,log_file,metadata_file,timestamp
```

F3 invariants:

- `failure_type` is `F3`.
- `stage` is `test`.
- `workflow_id` is `f3_test.yml`.
- `dependency` and `matched_pattern` equal the selected error type.
- `run_number` is the GitHub Actions matrix job ID.
- `log_file` is `logs/F3/<job_id>.log`.
- `metadata_file` is `metadata/F3/<job_id>.json`.
- `timestamp` is the job `completed_at` value.
- Metadata `id` equals `run_number`.
- Metadata `head_sha` equals `commit_sha`.
- Metadata `run_id` is the parent workflow-run ID and may be shared by all jobs in a batch.
- Logs are raw GitHub job-log text and metadata files are raw GitHub job JSON.
- CSV row order may be nondeterministic because log downloads are parallelized.

The collector paginates GitHub job results, filters to `test-f3` jobs, deduplicates job IDs, reports progress as jobs complete, verifies the expected job count, downloads logs concurrently, and then writes labels.

## Safety Rules

- Do not modify F1, F2, F4, or Timeout behavior unless explicitly requested.
- `--clean` may remove only direct F3 files under `logs/F3/` and `metadata/F3/`, plus F3 rows in `labels.csv`.
- Preserve all non-F3 rows and non-F3 artifacts.
- Inspect `git status` before operational runs because the generator uses `git add -A`.
- Do not run concurrent generators or concurrent pushes to the shared branch.
- Verify repository, branch, workflow, credentials, and intended target count before remote execution.
- Never expose or commit `.env` or `GITHUB_TOKEN`.
- Do not use `requirements.txt` as the F3 dependency source; it contains a legacy invalid placeholder. F3 requires `requests`, `python-dotenv`, and pytest in the workflow.

## Validation

Run focused local checks before remote generation:

```text
python -m py_compile generate_f3_runs.py
pytest tests/test_app.py -q
python -m pytest -q
```

For registry validation:

- Confirm the exact 13-column header.
- Confirm every row has the same number of fields.
- Confirm every F3 `log_file` exists.
- Confirm every F3 `metadata_file` exists.
- Confirm artifact basenames match `run_number`.
- Confirm metadata IDs, commit SHAs, conclusions, timestamps, and error types match the CSV.
- Confirm there are no duplicate F3 job IDs.
- Confirm the number of collected jobs equals the requested target.

For metadata inspection, use:

```text
python -m json.tool metadata/F3/<job_id>.json
```

Operational commands that can mutate local or remote state include:

```text
python generate_f3_runs.py --runs N [--clean] [--seed S]
python dataset_pipeline.py --category F3 --runs N [--clean]
python test_workflow.py
```

Review their side effects before running them.
