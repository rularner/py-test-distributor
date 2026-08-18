# py-test-distributor

A client/server system for splitting a pytest suite across multiple test
runners, so each test in a run executes exactly once no matter how many
runners are pulling from it.

## How it works

- **Server** (`server/testing_server.py`, a FastAPI app) tracks named test
  runs. A run is created with a list of test names; runners then pull tests
  one at a time from its queue (`GET /runs/{run_id}/tests`) and post back
  pass/fail results (`POST /runs/{run_id}/tests/{test_id}`). If two runners
  register the same run id with the same test list, they share that queue
  instead of creating separate ones.
- **Client library** (`client/testing_client.py`) is a small `requests`-based
  wrapper around that API (`TestRun`, `Test`).
- **Pytest plugin** (`client/pytest_plugin.py`) is registered as the
  `testdistributor` `pytest11` entry point, so installing this package is
  enough to make it available to pytest — no `-p` flag needed. Passing both
  `--distributor_url` and `--distributor_run_id` activates it: it takes over
  pytest's test loop, registers a run with the server using the collected
  test names, pulls tests from the server one at a time, runs them, and
  reports results back. If `--distributor_run_id` is omitted, the plugin
  stays inactive and pytest runs normally without contacting the server at
  all — there's no random id and no queue for a single, unshared runner.

## Installation

```
pip install -e .           # client / pytest plugin only
pip install -e .[server]   # also pulls in fastapi/uvicorn, to run the server
```

## Running the server

```
python -m server.testing_server
```

Serves on `0.0.0.0:8000`.

## Using the pytest plugin

To split one suite across multiple runners, give them all the same
`--distributor_url` and `--distributor_run_id` — they'll then pull from the
same queue and each test in the shared list runs exactly once, on whichever
runner asks for it first:

```
pytest --distributor_url http://localhost:8000 --distributor_run_id ci-$BUILD_ID
```

All runners in a run must submit the exact same set of test names; a runner
that registers a run id with a different test list than the one already
registered gets an error.

`--distributor_url` without `--distributor_run_id` has no effect — the
plugin requires both to activate, so a single runner invoked without a run
id just runs its normal test list locally and never talks to the server.

## Running the tests

```
pytest client server tests
```

## Future features

- Track test durations in a backend database and use them to prioritize
  handing out the longest-running tests first, so runners tend to finish at
  the same time instead of one runner being stuck with the slow tests at the
  end.
- Re-run a failed test a second time on a different runner; if it passes,
  log the original run as intermittent and treat the test as passed.
