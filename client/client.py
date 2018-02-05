import requests


class TestRun(object):
    def __init__(self, baseUrl: str, testRunner: str):
        self.baseUrl = baseUrl
        self.testRunner = testRunner

    def set_test_list(self, *args):
        requests.post(self.baseUrl, data={'test_list': args})

    def test_list(self):
        class Test(object):
            def __init__(self, testList, name: str):
                self.name = name
                self.testList = testList

            def success(self, duration: int):
                response = requests.post(
                    self.testList.baseUrl + self.name,
                    data={'state': 'success', 'duration': duration},
                )
                response.raise_for_status()

            def fail(self, duration: int, reason: str):
                response = requests.post(
                    self.testList.baseUrl + self.name,
                    data={
                        'state': 'fail',
                        'duration': duration,
                        'reason': reason,
                    },
                )
                response.raise_for_status()

        while True:
            response = requests.get(
                self.baseUrl,
                data={'runner': self.testRunner}).json()
            print("**************", response)
            if not response.get('testName', False):
                break
            if response.get('retry', False):
                continue
            yield Test(self, response['testName'])
