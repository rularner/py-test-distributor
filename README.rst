Python Distributed Test Runner Client
++++++++++++++=======================

This is the client for the Python Distributed Test Runner.  It
exposes a list that should be initialized with a list of tests,
and will then return a subset of those tests one-by-one.

`The source for this project is available here
<https://github.com/rularner/py-test-distributor/>`_.

This is currently compatible with PyTest.  Steps to run:
- Install this package
- Start the server: `python test_distributor.server.server`
- Run your tests with the client plugin enabled: `pytest -m test_distributor.client.pytest_plugin <any other arguments>`
