"""
Server that keeps track of which tests to run next.
"""

from unittest import TestCase
from fastapi.testclient import TestClient

from . import testing_server

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

    def test_reposting_same_run_is_a_noop(self):
        "Posting the same run name with the same tests twice should not error"
        payload = {'name': 'run_repost', 'tests': ['test_a', 'test_b']}
        first = client.post("/runs", json=payload)
        assert first.status_code == 200

        second = client.post("/runs", json=payload)
        assert second.status_code == 200

    def test_reposting_same_run_with_different_tests_conflicts(self):
        "Posting the same run name with a different test list should 400"
        client.post("/runs", json={'name': 'run_conflict', 'tests': ['test_a']})

        response = client.post("/runs", json={'name': 'run_conflict', 'tests': ['test_b']})
        assert response.status_code == 400
