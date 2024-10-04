from . import testing_client
from unittest import TestCase
import responses


@responses.activate
class UnitTests(TestCase):
    def setUp(self):
        responses.add(responses.POST, 'http://localhost:8080/runs')

        responses.add(responses.GET,
                      'http://localhost:8080/runs/run_1/tests/',
                      ['a', 'b', 'c', None],
                      )

    def test_client_iterates_through_tests(self, mock_requests):
        testRun = testing_client.TestRun(
            'http://localhost:8080/',
            'run_1',
            ['a', 'b', 'c']
        )
        self.assertEqual(['a', 'b', 'c'],
                         [test.name for test in list(testRun.test_run())]
                         )

    def test_client_reports_failures(self, mock_requests):
        responses.add(responses.POST, 'http://localhost:8080/runs/run_1/tests/a/')
        testRun = testing_client.TestRun('http://localhost:8080/', 'run_1', ['a'])
        [test1, _, _] = list(testRun.test_run())
        assert test1.name == 'a'
        test1.fail(duration=5)

    def test_client_reports_success(self, mock_requests):
        responses.add(responses.POST, 'http://localhost:8080/runs/run_1/tests/a/')

        testRun = testing_client.TestRun('http://localhost:8080/', 'host')
        [test1, _, _] = list(testRun.test_list())
        assert test1.name == 'a'
        test1.success(duration=5)
