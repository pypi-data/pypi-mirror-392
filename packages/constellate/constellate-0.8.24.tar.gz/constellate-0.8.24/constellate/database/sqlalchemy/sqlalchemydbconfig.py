import logging

import attr
from sqlalchemy.orm import sessionmaker

from constellate.database.sqlalchemy.config.dbconfigtype import DBConfigType
from constellate.database.sqlalchemy.sqlalchemyengineconfig import _EngineConfig
from constellate.database.sqlalchemy.sqlalchemymigrationconfig import _MigrationConfig


# FIXME Rename SQLAlchemyDBConfig into DBConfig ?
@attr.s(kw_only=True, frozen=False, eq=True, auto_attribs=True)
class SQLAlchemyDBConfig:
    # Generic Identification
    type: DBConfigType = None
    # Database user unique identifier
    identifier: str = None
    # Engine conf
    engine_config: _EngineConfig = None
    # Session conf
    session_maker: sessionmaker = None
    # Logging conf
    logger: logging.Logger = None
    is_logger_default: bool = None
    # Migration
    migration: _MigrationConfig = None
    # Misc conf
    options: dict = None
