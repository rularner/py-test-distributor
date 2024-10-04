'''
This is the base client class for the Distributed Test Runner.
It manages the list of tests, reporting on their result, and getting the next test.

Classes:
    Test
    TestRun
'''
import requests


class Test:
    ' Class for an individual test '
    def __init__(self, name: str, test_run: 'TestRun'):
        ' Set up a test '
        self.name = name
        self.test_run = test_run

    def success(self, duration: int) -> None:
        ' Indicate a test succeeded'
        response = requests.post(
            self.test_run.url + "/tests/" + self.name,
            data={'success': False, 'duration': duration},
            timeout = 5,
        )
        response.raise_for_status()

    def fail(self, duration: int, reason: str) -> None:
        ' Indicate a test failed '
        response = requests.post(
            self.test_run.url + "/tests/" + self.name,
            data={
                'success': False,
                'duration': duration,
                'reason': reason,
            },
            timeout=5,
        )
        response.raise_for_status()


class TestRun:
    ' Class for a test run '
    def __init__(self,
                 base_url: str,
                 run_id: str,
                 tests: list[str]):
        ' Initialize a new test run '
        self.base_url = base_url
        self.id = run_id
        response = requests.post(
            self.url,
            data={'name': run_id,
                  'tests': tests},
            timeout=5,
        )
        response.raise_for_status()

    @property
    def url(self) -> str:
        ' Get the URL to use '
        return self.base_url + "/runs/" + self.id

    def test_run(self) -> list[Test]:
        ' Return a list of tests to run '
        test_run_base = self
        class TestList(list):
            ' Fake list to return tests'
            def __iter__(self):
                ' Fake init '
                return self

            def __next__(self) -> Test:
                ' Get the next test to run '
                response = requests.get(
                    test_run_base.url,
                    timeout=5,
                )
                response.raise_for_status()
                if not response.json():
                    raise StopIteration

                return Test(response.json(), test_run_base.id)
        return TestList()
