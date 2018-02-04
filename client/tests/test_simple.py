from client import client
from unittest import TestCase
import requests_mock
import json


@requests_mock.mock()
class IntegrationTests(TestCase):
    def test_client_iterates_through_tests(self, mock_requests):
        mock_requests.post('http://localhost:8080/')

        def raise_if_hit():
            assert False
            raise Exception("should not get here")
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'testName': 'b'})},
                              {'text': json.dumps({'testName': 'c'})},
                              {'text': json.dumps({'tests': False})},
                              {'blah': raise_if_hit},
                          ])
        test_list = ['a', 'b', 'c']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        for test in testRun.test_list():
            assert test.name == test_list.pop(0)

    def test_client_reports_failures(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        mock_requests.post('http://localhost:8080/',
                           {
                               'state': 'fail',
                               'duration': 5,
                               'reason': 'anything goes here',
                           })
        test_list = ['a']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        test = testRun.test_list()[0]
        assert test.name == test_list.pop(0)
        test.fail(duration=5, reason='anything goes here')

    def test_client_reports_success(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        mock_requests.post('http://localhost:8080/',
                           {
                               'state': 'success',
                               'duration': 5,
                               'reason': 'anything goes here',
                           })
        test_list = ['a']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        test = testRun.test_list()[0]
        assert test.name == test_list.pop(0)
        test.success(duration=5, reason='anything goes here')

    def test_client_rerequests_if_asked(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        mock_requests.post('http://localhost:8080/',
                           {
                               'state': 'fail',
                               'duration': 5,
                               'reason': 'anything goes here',
                           })
        test_list = ['a']
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list(*test_list)
        test = testRun.test_list()[0]
        assert test.name == test_list.pop(0)
        test.fail(duration=5, reason='anything goes here')
