from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlalchemy.future import Connection, Engine
from sqlalchemy.orm import Session


def get_execution_options(
    connectable: (
        AsyncSession | AsyncEngine | AsyncConnection | Session | Engine | Connection
    ) = None,
    default_value: dict = None,
) -> dict | None:
    async_connectable = isinstance(connectable, (AsyncSession, AsyncEngine, AsyncConnection))

    def get_sync_connectable(connectable):
        if isinstance(connectable, AsyncConnection):
            return connectable.sync_connection
        if isinstance(connectable, AsyncEngine):
            return connectable.sync_engine
        if isinstance(connectable, AsyncSession):
            return connectable.sync_session

        raise NotImplementedError()

    sync_connectable = connectable if not async_connectable else get_sync_connectable(connectable)
    execution_options = getattr(sync_connectable, "_execution_options", None)
    return execution_options if execution_options is not None else default_value
