'''
End-to-end test for client/pytest_plugin.py: runs a real pytest subprocess
with --distributor_url pointed at a live server, and checks that tests were
actually routed through the distributor and their results reported back.
'''
from server import testing_server

SAMPLE_TESTS = '''
def test_one():
    assert True


def test_two():
    assert False
'''


def test_distributor_plugin_runs_tests_and_reports_results(pytester, live_server):
    ' Running pytest with --distributor_url should route tests through the real server '
    pytester.makepyfile(SAMPLE_TESTS)

    result = pytester.runpytest_subprocess('--distributor_url', live_server)

    result.assert_outcomes(passed=1, failed=1)

    run = next(iter(testing_server.run_dict.values()))
    assert run.test_results['test_one'].success is True
    assert run.test_results['test_two'].success is False
