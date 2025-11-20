from typing import Any
from constellate.database.sqlalchemy.sqlalchemydbconfig import SQLAlchemyDBConfig


# FIXME (prod) this method should not exit - it is standard in python dict
def pop_param_when_available(
    kwargs: dict = None, key: Any = None, default_value: Any = None
) -> dict[str, str] | SQLAlchemyDBConfig:
    return kwargs.pop(key, default_value)
