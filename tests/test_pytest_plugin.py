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
    ' --distributor_url plus --distributor_run_id should route tests through the real server '
    pytester.makepyfile(SAMPLE_TESTS)

    result = pytester.runpytest_subprocess(
        '--distributor_url', live_server,
        '--distributor_run_id', 'run_a',
    )

    result.assert_outcomes(passed=1, failed=1)

    run = testing_server.run_dict['run_a']
    assert run.test_results['test_one'].success is True
    assert run.test_results['test_two'].success is False


def test_distributor_run_id_option_names_the_shared_run(pytester, live_server):
    ' --distributor_run_id should be used as the run name '
    pytester.makepyfile(SAMPLE_TESTS)

    pytester.runpytest_subprocess(
        '--distributor_url', live_server,
        '--distributor_run_id', 'shared_run',
    )

    assert list(testing_server.run_dict.keys()) == ['shared_run']


def test_distributor_plugin_skips_server_without_run_id(pytester, live_server):
    ' Without --distributor_run_id, pytest should run normally and never contact the server '
    pytester.makepyfile(SAMPLE_TESTS)

    result = pytester.runpytest_subprocess('--distributor_url', live_server)

    result.assert_outcomes(passed=1, failed=1)
    assert not testing_server.run_dict
