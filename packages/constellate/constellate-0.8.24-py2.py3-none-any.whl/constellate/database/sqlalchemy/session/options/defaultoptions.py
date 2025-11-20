from collections import ChainMap

from sqlalchemy.util import EMPTY_DICT


class DefaultOptions:
    @staticmethod
    def __inject_options(options: dict = None, default_options: dict = None) -> dict:
        if options is None:
            options = {}
        if default_options is None:
            default_options = {}
        return dict(ChainMap(options, default_options))

    @staticmethod
    def inject_default_bind_arguments(
        bind_arguments: dict | None = EMPTY_DICT,
        kw: dict = EMPTY_DICT,
        defaults_bind_arguments: dict = EMPTY_DICT,
    ) -> tuple[dict | None, dict]:
        if bind_arguments is not None:
            return (
                DefaultOptions.__inject_options(
                    options=bind_arguments,
                    default_options=defaults_bind_arguments,
                ),
                kw,
            )
        else:
            return bind_arguments, DefaultOptions.__inject_options(
                options=kw.get("bind_arguments", EMPTY_DICT),
                default_options=defaults_bind_arguments,
            )

    @staticmethod
    def inject_default_execution_options(
        execution_options: dict | None = EMPTY_DICT,
        kw: dict = EMPTY_DICT,
        default_execution_options: dict = EMPTY_DICT,
    ) -> tuple[dict | None, dict]:
        if execution_options is not None:
            return (
                DefaultOptions.__inject_options(
                    options=execution_options,
                    default_options=default_execution_options,
                ),
                kw,
            )
        else:
            return execution_options, DefaultOptions.__inject_options(
                options=kw.get("execution_options", EMPTY_DICT),
                default_options=default_execution_options,
            )
