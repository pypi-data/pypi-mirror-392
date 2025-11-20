#!/usr/bin/env python
import multiprocessing
import time
from io import StringIO
from logging import StreamHandler

from pyexpect import expect

from constellate.logger.simple import (
    setup_main_process_loggers,
    setup_any_process_loggers,
    setup_child_process_loggers,
    setup_standalone_process_loggers,
    teardown_loggers,
)
from constellate.storage.filesystem.tmpfs.rambacked import mkd_tmpfs


def setup_function() -> None:
    pass


def teardown_function():
    pass


def create_test_logging_dict_config(
    root_logger_name: str | None = None,
    stream_1: StringIO = StringIO(),
    stream_2: StringIO = StringIO(),
) -> dict[
    str,
    (
        int
        | bool
        | dict[str, dict[str, str]]
        | dict[str, dict[str, str | StringIO]]
        | dict[str, dict[str, list[str] | str]]
    ),
]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"detailed": {"class": "logging.Formatter", "format": "%(message)s"}},
        "handlers": {
            "console1": {
                "class": "logging.StreamHandler",
                "stream": stream_1,
                "level": "DEBUG",
                "formatter": "detailed",
            },
            "console2": {
                "class": "logging.StreamHandler",
                "stream": stream_2,
                "level": "DEBUG",
                "formatter": "detailed",
            },
        },
        "loggers": {
            f"{root_logger_name}.test": {"handlers": ["console1"], "level": "DEBUG"},
            f"{root_logger_name}.test.innertest": {"handlers": ["console2"], "level": "DEBUG"},
        },
    }


def test_logger_standalone_default(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_default") as tmp_dir:
        setup_any_process_loggers(root_logger_name=root_logger_name, log_dir_path=str(tmp_dir))
        loggers = setup_standalone_process_loggers()

        for _logger, name in [
            (loggers.app, "app"),
            (loggers.network, "network"),
            (loggers.database, "database"),
            (loggers.media, "media"),
        ]:
            stream = StringIO()
            loggers.app.addHandler(StreamHandler(stream=stream))

            msg = f"{name}-record"
            loggers.app.info(msg)

            stream.seek(0)
            lines = stream.readlines()
            expect(1).to_equal(len(lines))
            expect(f"{msg}\n").within(lines)

        teardown_loggers(loggers=loggers, timeout=None)


def test_logger_standalone_non_default_1(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_non_default") as tmp_dir:
        template_dict = {
            "root": {
                "logger": "default",  # Field mandatory
                "level": "WARN",
                "app": {
                    "logger": "default",  # Field mandatory
                    "foo": {
                        "logger": "default",
                        "bar": {
                            "logger": "default",
                        },
                    },
                },
            }
        }
        setup_any_process_loggers(
            root_logger_name=root_logger_name,
            log_dir_path=str(tmp_dir),
            template_dict=template_dict,
        )
        loggers = setup_standalone_process_loggers()

        vectors = {
            1: {"logger": loggers.app.foo.bar, "name": "app.foo.bar", "stream": StringIO()},
            2: {"logger": loggers.app.foo, "name": "app.foo", "stream": StringIO()},
            3: {"logger": loggers.app, "name": "app", "stream": StringIO()},
        }

        # Setup handler per logger
        for _index, obj in vectors.items():
            stream = obj.get("stream", None)
            logger = obj.get("logger", None)
            logger.addHandler(StreamHandler(stream=stream))

        propagated_messages = []
        for index, obj in vectors.items():
            stream = obj.get("stream", None)
            logger = obj.get("logger", None)
            name = obj.get("name", None)

            msg = f"{name}-record"
            logger.info(msg)
            propagated_messages.append(msg)

            stream.seek(0)
            lines = stream.readlines()
            expect(len(propagated_messages)).to_equal(len(lines))
            for msg in propagated_messages:
                expect(f"{msg}\n").within(lines)

        teardown_loggers(loggers=loggers, timeout=None)


def test_logger_standalone_non_default_2(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_non_default") as tmp_dir:
        stream_1 = StringIO()
        stream_2 = StringIO()
        config_dict = create_test_logging_dict_config(
            root_logger_name=root_logger_name, stream_1=stream_1, stream_2=stream_2
        )
        setup_any_process_loggers(
            root_logger_name=root_logger_name, log_dir_path=str(tmp_dir), config_dict=config_dict
        )
        loggers = setup_standalone_process_loggers()
        loggers.test.info("test-record")
        loggers.test.innertest.info("innertest-record")

        stream_1.seek(0)
        lines = stream_1.readlines()
        expect(2).to_equal(len(lines))
        expect("test-record\n").within(lines)
        expect("innertest-record\n").within(lines)

        stream_2.seek(0)
        lines = stream_2.readlines()
        expect(1).to_equal(len(lines))
        expect("innertest-record\n").within(lines)

        teardown_loggers(loggers=loggers, timeout=None)


def _worker_test_logger_main_and_child_loggers_non_default(root_logger_name, loggers_settings):
    with mkd_tmpfs(prefix="test_logger_main_and_child_loggers") as tmp_dir:
        config_dict = create_test_logging_dict_config(
            root_logger_name=root_logger_name, stream_1=StringIO()
        )
        setup_any_process_loggers(
            root_logger_name=root_logger_name,
            log_dir_path=str(tmp_dir),
            config_dict=config_dict,
        )
        loggers = setup_child_process_loggers(mode_settings=loggers_settings)
        loggers.test.info("client-test-record")
        loggers.test.innertest.info("client-innertest-record")
        teardown_loggers(loggers=loggers, timeout=None)


def test_logger_main_and_child_loggers_non_default(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_main_and_child_loggers") as tmp_dir:
        stream_1 = StringIO()
        stream_2 = StringIO()
        config_dict = create_test_logging_dict_config(
            root_logger_name=root_logger_name, stream_1=stream_1, stream_2=stream_2
        )
        setup_any_process_loggers(
            root_logger_name=root_logger_name, log_dir_path=str(tmp_dir), config_dict=config_dict
        )
        loggers = setup_main_process_loggers()
        loggers.test.info("master-test-record")
        loggers.test.innertest.info("master-innertest-record")

        proc = multiprocessing.Process(
            target=_worker_test_logger_main_and_child_loggers_non_default,
            args=[root_logger_name, loggers.settings()],
        )
        proc.start()
        proc.join()

        # Give time to python interpreter to read incoming logs
        time.sleep(10.0)

        stream_1.seek(0)
        lines = stream_1.readlines()
        expect(4).to_equal(len(lines))
        expect("master-test-record\n").within(lines)
        expect("master-innertest-record\n").within(lines)
        expect("client-test-record\n").within(lines)
        expect("client-innertest-record\n").within(lines)

        stream_2.seek(0)
        lines = stream_2.readlines()
        expect(2).to_equal(len(lines))
        expect("master-innertest-record\n").within(lines)
        expect("client-innertest-record\n").within(lines)


class TestExceptionString(BaseException):
    def __init__(self, *args, tag: str = None):
        super().__init__(*args)
        self._tag = tag

    def __str__(self):
        return self._tag


def test_logger_print_exception_str(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_default") as tmp_dir:
        setup_any_process_loggers(root_logger_name=root_logger_name, log_dir_path=str(tmp_dir))
        loggers = setup_standalone_process_loggers()

        for _logger, name in [
            (loggers.app, "app"),
        ]:
            stream = StringIO()
            loggers.app.addHandler(StreamHandler(stream=stream))

            try:
                raise TestExceptionString(tag="found")
            except BaseException:
                msg = f"{name}-record"
                loggers.app.info(msg, exc_info=1)

            stream.seek(0)
            lines = stream.readlines()
            expect(f"{msg}\n").within(lines)
            expect(
                f"{'.'.join([TestExceptionString.__module__, TestExceptionString.__name__])}: found\n"
            ).within(lines)

        teardown_loggers(loggers=loggers, timeout=None)


def test_logger_print_no_exception_str(root_logger_name: str) -> None:
    with mkd_tmpfs(prefix="test_logger_default") as tmp_dir:
        setup_any_process_loggers(root_logger_name=root_logger_name, log_dir_path=str(tmp_dir))
        loggers = setup_standalone_process_loggers()

        for _logger, name in [
            (loggers.app, "app"),
        ]:
            stream = StringIO()
            loggers.app.addHandler(StreamHandler(stream=stream))

            msg = f"{name}-record"
            loggers.app.info(msg)

            stream.seek(0)
            lines = stream.readlines()
            expect(f"{msg}\n").within(lines)

        teardown_loggers(loggers=loggers, timeout=None)
