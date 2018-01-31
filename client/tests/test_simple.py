from client import client
from unittest import TestCase
import requests_mock
import json


class IntegrationTests(TestCase):
    @requests_mock.mock()
    def test_client_iterates_through_tests(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'testName': 'b'})},
                              {'text': json.dumps({'testName': 'c'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        test_list = ['a', 'b', 'c']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        for test in testRun.test_list():
            assert test.name == test_list.pop(0)
