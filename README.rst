Python Test Distributor
++++++++++++++++++++++++

A client/server system for splitting a pytest suite across multiple test
runners, so each test in a run executes exactly once no matter how many
runners are pulling from it.

`The source for this project is available here
<https://github.com/rularner/py-test-distributor/>`_.

Installing this package registers a pytest plugin (``testdistributor``)
automatically, so ``pip install`` is the only setup step needed on a test
runner. Steps to run:

- Install this package: ``pip install test-distributor`` (add the
  ``[server]`` extra on the machine that will host the server:
  ``pip install test-distributor[server]``)
- Start the server: ``python -m server.testing_server``
- To split one suite across multiple runners, give them all the same
  ``--distributor_url`` and ``--distributor_run_id``, so they pull from the
  same queue: ``pytest --distributor_url http://localhost:8000
  --distributor_run_id ci-run-42``
- ``--distributor_run_id`` is required to activate the plugin;
  ``--distributor_url`` alone has no effect, and a runner invoked without a
  run id just runs its tests locally without contacting the server.
