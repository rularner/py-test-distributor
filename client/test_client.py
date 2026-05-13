' Tests for testing client '
from unittest import TestCase
import responses

import testing_client


@responses.activate
class UnitTests(TestCase):
    ' Simple tests for test client'
    def setUp(self):
        ' Setup for all tests '
        responses.add(responses.POST, 'http://localhost:8080/runs')

        responses.add(responses.GET,
                      'http://localhost:8080/runs/run_1/tests/',
                      ['a', 'b', 'c', None],
                      )

    def test_client_iterates_through_tests(self):
        ' Test client iteration '
        test_run = testing_client.TestRun(
            'http://localhost:8080/',
            'run_1',
            ['a', 'b', 'c']
        )
        self.assertEqual(['a', 'b', 'c'],
                         [test.name for test in list(test_run.test_run())]
                         )

    def test_client_reports_failures(self):
        ' Test client failure reporting '
        responses.add(responses.POST, 'http://localhost:8080/runs/run_1/tests/a/')
        test_run = testing_client.TestRun('http://localhost:8080/', 'run_1', ['a'])
        [test1, _, _] = list(test_run.test_run())
        assert test1.name == 'a'
        test1.fail(duration=5)

    def test_client_reports_success(self):
        ' Test client success reporting '
        responses.add(responses.POST, 'http://localhost:8080/runs/run_1/tests/a/')

        test_run = testing_client.TestRun('http://localhost:8080/', 'host', ['a', 'b', 'c'])
        [test1, _, _] = list(test_run.test_run())
        assert test1.name == 'a'
        test1.success(duration=5)
