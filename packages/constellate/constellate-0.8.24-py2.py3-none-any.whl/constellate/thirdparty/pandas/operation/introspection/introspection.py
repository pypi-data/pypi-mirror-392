# from typing import Callable
#
# import pandas_log
# from decorator import decorator
#
#
# @decorator
# def pandas_data_operation_log(fn: Callable = None, *fn_args, **fn_kwargs):
#     with pandas_log.enable():
#         # FIXME(low) Log message with logger. Unclear if pandas-log support it
#         return fn(*fn_args, **fn_kwargs)
