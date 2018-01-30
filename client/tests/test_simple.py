from client import client
from unittest import TestCase
import requests_mock


class IntegrationTests(TestCase):
    @requests_mock.mock()
    def test_client_integration(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        test_list = ['a', 'b', 'c']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        for test in testRun.test_list():
            assert test.name == test_list.pop()
            test.success(duration=5)
