"""
Server that keeps track of which tests to run next.
"""

from . import server

from unittest import TestCase
from fastapi.testclient import TestClient

client = TestClient(server.app)


class UnitTests(TestCase):
    def test_base_server(self):
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
