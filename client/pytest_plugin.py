# PyTest plugin
from pytest import Session, mark, Item, CallInfo, Parser, Config
from . import testing_client


def pytest_addoption(parser: Parser):
    group = parser.getgroup("terminal reporting", "reporting", after="general")
    group._addoption(
        '--distributor_url', action="store", dest="distributor_url",
        help=(
            "Test distributor server URL"
        )
    )


@mark.trylast
def pytest_configure(config: Config):
    if config.option.distributor_url and config.pluginmanager.hasplugin('testdistributor'):
        # Get the standard terminal reporter plugin...
        test_distributor = TestDistributor(config.option.distributor_url)

        # ...and replace it with our own instafailing reporter.
        config.pluginmanager.register(test_distributor, 'test_distributor')


class TestDistributor():
    def __init__(self, baseUrl: str, testRunnerName: str):
        self.test_run = testing_client.TestRun(baseUrl, testRunnerName)
        self.__current_test_item = None

    def pytest_runtestloop(self, session: Session):
        self.test_run.set_test_list([item.name for item in session.items])
        name_to_items = {item.name: item for item in session.items}

        class ListOverride(list):
            def __iter__(self):
                class CustomIter():
                    def next():
                        next_test = self.test_run.test_list.next()
                        return name_to_items[next_test.name]
        session.items = ListOverride()

    def pytest_runtest_makereport(self, item: Item, call: CallInfo[None]):
        if call and call.result:
            # success
            self.__current_test_item.success(item.duration)
        else:
            self.__current_test_item.failure(item.duration)
