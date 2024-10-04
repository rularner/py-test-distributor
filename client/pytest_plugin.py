' PyTest plugin '
from random import randint
from pytest import Session, mark, Item, CallInfo, Parser, Config
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


@mark.trylast
def pytest_configure(config: Config):
    ' Configure the plugin.'
    if config.option.distributor_url and config.pluginmanager.hasplugin('testdistributor'):
        # Get the standard terminal reporter plugin...
        test_distributor = TestDistributor(config.option.distributor_url, f'{randint}')

        # ...and replace it with our own instafailing reporter.
        config.pluginmanager.register(test_distributor, 'test_distributor')


class TestDistributor():
    ' Class to manage tests in pytest. '
    def __init__(self, base_url: str, test_runner_name: str):
        ' Initialize. '
        self.__current_test_item = None
        self.__base_url = base_url
        self.__test_runner_name = test_runner_name

    def pytest_runtestloop(self, session: Session):
        ' Run tests in a loop '
        test_run = testing_client.TestRun(self.__base_url,
                                          self.__test_runner_name,
                                          [item.name for item in session.items])
        name_to_items = {item.name: item for item in session.items}

        class ListOverride(list):
            ' Class representing the list of tests '
            def __iter__(self):
                ' When iterated... '
                return self

            def __next__(self):
                ' return next test '
                next_test = test_run.test_run()
                return name_to_items[next_test]
        session.items = ListOverride()

    def pytest_runtest_makereport(self, item: Item, call: CallInfo[None]):
        ' Create a report '
        if call and call.result:
            # success
            self.__current_test_item.success(item.duration)
        else:
            self.__current_test_item.failure(item.duration)
