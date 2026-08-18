'''
End-to-end tests that run the real client against a real, live server.

No mocks: these exist specifically to catch client/server contract
mismatches (wrong URLs, wrong payload encoding, wrong response shapes)
that per-component unit tests with mocked HTTP can miss.
'''
from client import testing_client
from server import testing_server


def test_client_runs_all_tests_and_reports_results(live_server):
    ' A client should receive every queued test exactly once and be able to report results '
    test_run = testing_client.TestRun(live_server, 'integration_run', ['a', 'b', 'c'])

    seen = []
    for test in test_run.test_run():
        seen.append(test.name)
        if test.name == 'b':
            test.fail(duration=1, reason='expected failure')
        else:
            test.success(duration=1)

    assert {'a', 'b', 'c'} == set(seen)

    results = testing_server.run_dict['integration_run'].test_results
    assert {'a', 'b', 'c'} == set(results.keys())
    assert results['a'].success
    assert not results['b'].success
    assert results['c'].success


def test_reconnecting_to_same_run_shares_the_queue(live_server):
    ' A second client joining the same run should not re-create it or duplicate tests '
    first = testing_client.TestRun(live_server, 'shared_run', ['a', 'b'])
    second = testing_client.TestRun(live_server, 'shared_run', ['a', 'b'])

    seen = [test.name for test in first.test_run()] + [test.name for test in second.test_run()]
    assert {'a', 'b'} == set(seen)
