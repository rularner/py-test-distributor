' PyTest plugin '
from pytest import Session, mark, CallInfo, Parser, Config
from . import testing_client


def pytest_addoption(parser: Parser):
    ' Add configuration options. '
    group = parser.getgroup("terminal reporting", "reporting", after="general")
    group._addoption(  # pylint: disable=protected-access
        '--distributor_url', action="store", dest="distributor_url",
        help=(
            "Test distributor server URL"
        )
    )
    group._addoption(  # pylint: disable=protected-access
        '--distributor_run_id', action="store", dest="distributor_run_id",
        help=(
            "Shared run id. Runners started with the same --distributor_url and "
            "--distributor_run_id pull from the same test queue. Required to "
            "enable the distributor; without it, --distributor_url is ignored "
            "and pytest runs normally."
        )
    )


@mark.trylast
def pytest_configure(config: Config):
    ' Configure the plugin.'
    if (config.option.distributor_url and config.option.distributor_run_id
            and config.pluginmanager.hasplugin('testdistributor')):
        # Get the standard terminal reporter plugin...
        test_distributor = TestDistributor(
            config.option.distributor_url, config.option.distributor_run_id)

        # ...and replace it with our own instafailing reporter.
        config.pluginmanager.register(test_distributor, 'test_distributor')


class TestDistributor():
    ' Class to manage tests in pytest. '
    def __init__(self, base_url: str, run_id: str):
        ' Initialize. '
        self.__current_test = None
        self.__base_url = base_url
        self.__run_id = run_id

    def pytest_runtestloop(self, session: Session) -> bool:
        ' Run tests in whatever order the distributor hands them out '
        test_run = testing_client.TestRun(self.__base_url,
                                          self.__run_id,
                                          [item.name for item in session.items])
        name_to_items = {item.name: item for item in session.items}

        for remote_test in test_run.test_run():
            self.__current_test = remote_test
            item = name_to_items[remote_test.name]
            item.config.hook.pytest_runtest_protocol(item=item, nextitem=None)
            if session.shouldfail or session.shouldstop:
                break
        return True

    def pytest_runtest_makereport(self, call: CallInfo[None]):
        ' Report the result of the test that just ran back to the distributor '
        if call.when != 'call' or self.__current_test is None:
            return
        if call.excinfo is None:
            self.__current_test.success(int(call.duration))
        else:
            self.__current_test.fail(int(call.duration), reason=str(call.excinfo.value))
