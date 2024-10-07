"""
Server that keeps track of which tests to run next.
"""

from unittest import TestCase
from fastapi.testclient import TestClient

import testing_server

client = TestClient(testing_server.app)


class UnitTests(TestCase):
    "Initial unit tests"

    def test_base_server(self):
        "See if server works with easy requests"
        response = client.post(
            "/runs",
            # headers={"X-Token": "hailhydra"},
            json={
                'name': 'run_1',
                'tests': ['test_a']
            },
        )
        print(response)
        assert response.status_code == 200

        response = client.get(
            "/runs/run_1/tests",
            # headers={"X-Token": "hailhydra"},
        )
        print(response)
        assert response.status_code == 200
        assert response.json() == "test_a"

        response = client.post(
            "/runs/run_1/tests/test_a",
            # headers={"X-Token": "hailhydra"},
            json={
                "duration": 200,
                "success": True,
            },
        )
        assert response.status_code == 200
