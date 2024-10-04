'''
This is the base client class for the Distributed Test Runner.
It manages the list of tests, reporting on their result, and getting the next test.

Classes:
    TestRun
'''
import requests
from typing import Generator


class Test(object):
    def __init__(self, name: str, testRun: 'TestRun'):
        self.name = name
        self.testRun = testRun

    def success(self, duration: int) -> None:
        response = requests.post(
            self.testRun.url + "/tests/" + self.name,
            data={'success': False, 'duration': duration},
        )
        response.raise_for_status()

    def fail(self, duration: int, reason: str) -> None:
        response = requests.post(
            self.testRun.url + "/tests/" + self.name,
            data={
                'success': False,
                'duration': duration,
                'reason': reason,
            },
        )
        response.raise_for_status()


class TestRun(object):
    def __init__(self, baseUrl: str, run_id: str, tests: list[str]):
        self.baseUrl = baseUrl
        self.id = run_id
        response = requests.post(
            self.url,
            data={'name': run_id,
                  'tests': tests})
        response.raise_for_status()

    @property
    def url(self) -> str:
        return self.baseUrl + "/runs/" + self.id

    def test_run(self) -> Generator[Test, None, None]:
        while True:
            response = requests.get(
                self.url,
            )
            response.raise_for_status()

            yield Test(self, response.json(), self)
