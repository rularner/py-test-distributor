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
                              {'text': 'unjsonable'},
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
        mock_requests.post('http://localhost:8080/a',
                           [{'text': json.dumps({
                               'state': 'fail',
                               'duration': 5,
                               'reason': 'anything goes here',
                           })}])
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list('a')
        runTestList = list(testRun.test_list())
        test = runTestList[0]
        assert test.name == 'a'
        test.fail(duration=5, reason='anything goes here')

    def test_client_reports_success(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        mock_requests.post('http://localhost:8080/a',
                           [{'text': json.dumps({
                               'state': 'success',
                               'duration': 5,
                           })}])
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list('a')
        runTestList = list(testRun.test_list())
        test = runTestList[0]
        assert test.name == 'a'
        test.success(duration=5)

    def test_client_rerequests_if_asked(self, mock_requests):
        mock_requests.post('http://localhost:8080/')
        mock_requests.get('http://localhost:8080/',
                          [
                              {'text': json.dumps({'retry': True})},
                              {'text': json.dumps({'testName': 'a'})},
                              {'text': json.dumps({'tests': False})},
                          ])
        mock_requests.post('http://localhost:8080/',
                           [{'text': json.dumps({
                               'state': 'fail',
                               'duration': 5,
                               'reason': 'anything goes here',
                           })}])
        testRun = client.TestRun('http://localhost:8080/', 'host')
        testRun.set_test_list('a')
        # runTestList = list(testRun.test_list())
        # assert len(runTestList) == 1
        # test = runTestList[0]
        # assert test.name == 'a'
