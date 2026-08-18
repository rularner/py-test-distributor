' Shared fixtures for running a real, live copy of the distributor server in tests '
import socket
import threading
import time

import pytest
import uvicorn

from server import testing_server

pytest_plugins = ["pytester"]


def _free_port() -> int:
    ' Find an unused local port to run the test server on '
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


@pytest.fixture
def live_server():
    ' Start a real distributor server on a free local port and yield its base URL '
    testing_server.run_dict.clear()
    port = _free_port()
    base_url = f'http://127.0.0.1:{port}'
    config = uvicorn.Config(testing_server.app, host='127.0.0.1', port=port, log_level='warning')
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    try:
        yield base_url
    finally:
        server.should_exit = True
        thread.join(timeout=5)
