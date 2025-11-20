import asyncio
import functools
import inspect
from collections import ChainMap
from collections.abc import Awaitable
from typing import Union, Any
from collections.abc import Callable

import pandas
import pandera
from decorator import decorator
from typing import TypeAlias

from constellate.thirdparty.pandas.validation.pandera import BaseConfig as PandaBaseConfig

PanderaSchema: TypeAlias = Union[pandera.DataFrameSchema, pandera.SeriesSchema]
PandasType: TypeAlias = Union[pandas.DataFrame, pandas.Series]

LibrarySchema: TypeAlias = Union[PanderaSchema]

AsyncOrSyncCallable: TypeAlias = Union[Callable[..., Any], Callable[..., Awaitable]]


def async_sync(wrapped_fn: AsyncOrSyncCallable, *fn_args, **fn_kwargs):
    # src: https://stackoverflow.com/a/68746329/219728
    if asyncio.iscoroutinefunction(wrapped_fn):

        @functools.wraps(wrapped_fn)
        async def _decorated(*args, **kwargs) -> Any:
            return await wrapped_fn(*args, **kwargs)

    else:

        @functools.wraps(wrapped_fn)
        def _decorated(*args, **kwargs) -> Any:
            return wrapped_fn(*args, **kwargs)

    return _decorated(*fn_args, **fn_kwargs)


class DataValidationError(Exception):
    pass


def pandera_schema_from_pydantic_schema(schema: LibrarySchema):
    if isinstance(schema, (pandera.DataFrameSchema, pandera.SeriesSchema)):
        return schema
    return schema.to_schema()


def _pydantic_schema_fix_config_inheritance(
    schema: pandera.api.dataframe.model.DataFrameModel = None,
):
    # src: https://github.com/unionai-oss/pandera/blob/63140c9af17314541a21f6629801fe09e90202a3/pandera/api/dataframe/model.py#L384

    def _get_schema_config_class(schema_class):
        return getattr(schema_class, pandera.api.dataframe.model._CONFIG_KEY, {})

    # Extract Config from pandera.api.*.model.DataFrameModel
    pandera_model_config_cls, _ = schema._collect_config_and_extras()
    options, _ = schema._extract_config_options_and_extras(pandera_model_config_cls)

    # Extract Config from hierarchy of schema.Config up to pandera.api.*.model.DataFrameModel.Config
    # (ie the missing Config not retrieved from  _collect_config_and_extras())
    schema_classes = [
        c for c in inspect.getmro(schema) if issubclass(c, pandera.api.pandas.model.DataFrameModel)
    ][:-1]
    for schema_class in reversed(schema_classes):
        schema_config_class = _get_schema_config_class(schema_class)
        config_classes = [
            config_class
            for config_class in inspect.getmro(schema_config_class)
            if issubclass(config_class, PandaBaseConfig)
        ]
        for config_class in reversed(config_classes):
            options2, _ = schema._extract_config_options_and_extras(config_class)
            options.update(options2)

    return type(
        f"{str(schema.__module__)}.Config",
        (pandera_model_config_cls,),
        dict(ChainMap(options)),
    )


def _pandera_checks(
    data: PandasType = None,
    schema: LibrarySchema = None,
    schema_validation_options: dict[str, Any] = None,
):
    row_total = len(data)
    sample_row_total = round(row_total * 0.25)
    head_row_total = round(row_total * 0.15)
    schema_validation_options = schema_validation_options or {
        # Head / Tail: 15 % of the rows
        "head": max(0, min(head_row_total if row_total > 100 else row_total, row_total)),
        "tail": max(0, min(head_row_total if row_total > 100 else row_total, row_total)),
        # Sample 25% of the rows
        "sample": max(0, min(sample_row_total if row_total > 100 else row_total, row_total)),
        "lazy": False,
        "inplace": True,
    }
    if schema is None:
        raise ValueError("Missing schema")

    try:
        pandera_schema = schema
        if not isinstance(schema, (pandera.DataFrameSchema, pandera.SeriesSchema)):
            # Convert Pandera's DataFrame Model (ie Pandera's DataFrame Model using pydantic like notation)
            # into a Pandera native's DataFrame Schema
            schema.__config__ = _pydantic_schema_fix_config_inheritance(schema=schema)
            pandera_schema = pandera_schema_from_pydantic_schema(schema=schema)

        # For list of checks carried out:
        # https://pandera.readthedocs.io/en/stable/lazy_validation.html
        return pandera_schema.validate(data, **schema_validation_options)
    except pandera.errors.SchemaError as e:
        # Case: lazy=False
        msg = (
            f"\n\n------- Schema Error # --------\n"
            f"Schema:{schema.__name__}\n"
            f"Detail: {''.join(list(e.args))}\n"
            f"Failure Cases: {e.failure_cases}\n"
            f"Ruled failed:{e.schema}"
        )
        raise DataValidationError(msg) from e
    except pandera.errors.SchemaErrors as e:
        # Case: lazy=True
        msg = ""
        for index, se in enumerate(e.schema_errors):
            error = se.get("error")
            msg += (
                f"\n\n------- Schema Error #{index} --------\n"
                f"Schema:{schema.__name__}\n"
                f"Reason: {se.get('reason_code')}\n"
                f"Detail: {''.join(list(error.args))}\n"
                f"Failure Cases: {error.failure_cases}\n"
                f"Ruled failed:{error.schema}"
            )
        raise DataValidationError(msg) from e


@decorator
def pandas_data_coerce_and_validate(
    fn: Callable,
    schema: LibrarySchema = None,
    schema_validation_options: dict[str, Any] = None,
    *fn_args,
    **fn_kwargs,
):
    """

    :param fn: Callable:
    :param schema: LibrarySchema:  (Default value = None)
    :param schema_validation_options: Dict[str:
    :param Any]:  (Default value = None)
    :param *fn_args:
    :param **fn_kwargs:

    """

    fn_check = None
    if isinstance(
        schema, (pandera.DataFrameSchema, pandera.SeriesSchema, pandera.api.base.model.MetaModel)
    ):
        fn_check = _pandera_checks
    else:
        raise NotImplementedError()

    fn_read_and_check = None
    if asyncio.iscoroutinefunction(fn):

        async def _read_and_check(
            fn_check=None,
            fn=None,
            schema=None,
            schema_validation_options=None,
            *fn_args,
            **fn_kwargs,
        ):
            data = await fn(*fn_args, **fn_kwargs)
            return fn_check(
                data=data, schema=schema, schema_validation_options=schema_validation_options
            )

        fn_read_and_check = _read_and_check

    else:

        def _read_and_check(
            fn_check=None,
            fn=None,
            schema=None,
            schema_validation_options=None,
            *fn_args,
            **fn_kwargs,
        ):
            data = fn(*fn_args, **fn_kwargs)
            return fn_check(
                data=data, schema=schema, schema_validation_options=schema_validation_options
            )

        fn_read_and_check = _read_and_check

    return fn_read_and_check(
        fn_check,
        fn,
        schema,
        schema_validation_options,
        *fn_args,
        **fn_kwargs,
    )
