from collections.abc import Iterable, AsyncGenerator

import pytest
from pyexpect import expect
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import Column, Integer, String, select, func, Row
from sqlalchemy.orm import declarative_base

from constellate.database.common.databasetype import DatabaseType
from constellate.database.sqlalchemy.execution.execute import (
    execute_scalars_one_or_none,
    execute_scalars_one,
    execute_scalars_all_iterable,
    execute_scalars_all_async_generator,
    # execute_scalars_stream_iterable,
    # execute_scalars_stream_async_generator,
    execute_passthrough_result,
    execute_discard_result,
    execute_scalar,
    execute_rows_all_iterable,
)
from constellate.database.sqlalchemy.expression.schema.create import CreateSchema
from constellate.database.sqlalchemy.expression.schema.drop import DropSchema
from constellate.database.sqlalchemy.expression.table.drop import DropTable
from tests.util.database_context import DatabaseContext

Base = declarative_base()


class SQLAlchemyTestR(Base):
    __tablename__ = "test_sqlachemy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String)


TEST_SQLALCHEMY_CLASSES = [SQLAlchemyTestR]


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_execute_query(database_context: DatabaseContext) -> None:
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        async with db.session_scope() as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        async with db.session_scope() as session:
            for r in [
                SQLAlchemyTestR(text="foo"),
                SQLAlchemyTestR(text="foo2"),
                SQLAlchemyTestR(text="foo3"),
            ]:
                session.add(r)

        async with db.session_scope() as session:

            async def _read(session: AsyncSession = None, conditions: list = None):
                return select(SQLAlchemyTestR).filter(*conditions)

            @execute_passthrough_result
            async def read_passthrough(text: str = None, **kwargs):
                return await _read(conditions=[SQLAlchemyTestR.text == text], **kwargs)

            result = await read_passthrough(session=session, text="foo")
            result = result.scalars().one()
            expect(isinstance(result, SQLAlchemyTestR)).equals(True)
            expect(result.id).equals(1)

            @execute_discard_result
            async def read_discard_result(text: str = None, **kwargs):
                return await _read(conditions=[SQLAlchemyTestR.text == text], **kwargs)

            result = await read_discard_result(session=session, text="foo")
            expect(result).equals(None)

            @execute_scalar
            async def read_scalar(text: str = None, **kwargs):
                return select(SQLAlchemyTestR.text, SQLAlchemyTestR.id).filter(
                    *[SQLAlchemyTestR.text == text]
                )

            result = await read_scalar(session=session, text="foo")
            expect(result).equals("foo")

            @execute_scalars_one_or_none
            async def read_scalars_one_or_none(text: str = None, **kwargs):
                return await _read(conditions=[SQLAlchemyTestR.text == text], **kwargs)

            result = await read_scalars_one_or_none(session=session, text="foo")
            expect(isinstance(result, SQLAlchemyTestR)).equals(True)
            expect(result.id).equals(1)

            result = await read_scalars_one_or_none(session=session, text="do not exist")
            expect(result).equals(None)

            @execute_scalars_one
            async def read_scalars_one(text: str = None, **kwargs):
                return await _read(conditions=[SQLAlchemyTestR.text == text], **kwargs)

            result = await read_scalars_one(session=session, text="foo")
            expect(isinstance(result, SQLAlchemyTestR)).equals(True)
            expect(result.id).equals(1)

            with pytest.raises(NoResultFound) as _excinfo:
                await read_scalars_one(session=session, text="do not exist")

            @execute_scalars_all_iterable
            async def read_scalars_all_iterable(**kwargs):
                return await _read(conditions=[], **kwargs)

            result = await read_scalars_all_iterable(session=session)
            expect(isinstance(result, Iterable)).equals(True)
            expect(len(list(result))).equals(3)

            @execute_scalars_all_async_generator
            async def read_scalars_all_async_generator(**kwargs):
                return await _read(conditions=[], **kwargs)

            result = await read_scalars_all_async_generator(session=session)
            expect(isinstance(result, AsyncGenerator)).equals(True)
            result = [r async for r in result]
            expect(len(result)).equals(3)

            @execute_rows_all_iterable
            async def read_rows_all_iterable(**kwargs):
                return await _read(conditions=[], **kwargs)

            result = await read_rows_all_iterable(session=session)
            expect(isinstance(result, Iterable)).equals(True)
            expect(all(map(lambda row: isinstance(row, Row), result))).equals(True)
            expect(len(result)).equals(3)

            # @execute_scalars_stream_iterable
            # async def read_stream_iterable(**kwargs):
            #     return await _read(conditions=[], **kwargs)
            #
            # result = await read_stream_iterable(session=session)
            # expect(isinstance(result, Iterable)).equals(True)
            # result = [r for r in result]
            # expect(len(result)).equals(3)
            #
            # @execute_scalars_stream_async_generator
            # async def read_stream_async_generator(**kwargs):
            #     return await _read(conditions=[], **kwargs)
            #
            # result = await read_stream_async_generator(session=session)
            # expect(isinstance(result, AsyncGenerator)).equals(True)
            # result = [r async for r in result]
            # expect(len(result)).equals(3)

        await db.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_setup_with_contextmanager(database_context: DatabaseContext) -> None:
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        async with db.session_scope() as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        async with db.session_scope() as session:
            test = SQLAlchemyTestR(text="foo")
            session.add(test)

        async with db.session_scope() as session:
            query = select(func.count(SQLAlchemyTestR.text).label("total")).where(
                SQLAlchemyTestR.text == "foo"
            )
            result = await session.execute(query)
            expect(result.scalar_one()).equals(1)

        await db.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_without_contextmanager(database_context: DatabaseContext) -> None:
    session = None
    conn = None
    try:
        await database_context.storage.setup2(options=database_context.setup_options)
        session = await database_context.storage.session_scope2()
        async with session.bind.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

        test = SQLAlchemyTestR(text="foo")
        session.add(test)
        await session.commit()

        query = select(func.count(SQLAlchemyTestR.text).label("total")).where(
            SQLAlchemyTestR.text == "foo"
        )
        result = await session.execute(query)
        expect(result.scalar_one()).equals(1)
    finally:
        if conn is not None:
            await conn.close()
        if session is not None:
            await session.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_setup_with_custom_execution_options_per_session(
    database_context: DatabaseContext,
) -> None:
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        async with db.session_scope(execution_options={"foo": "bar"}, bind="foo_engine") as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        await db.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_drop_table(database_context: DatabaseContext) -> None:
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        # Delete table (expects missing)
        async with db.session_scope() as session:
            with pytest.raises((sqlalchemy.exc.ProgrammingError, sqlalchemy.exc.OperationalError)):
                await session.execute(DropTable(element=SQLAlchemyTestR, if_exists=False))

        async with db.session_scope() as session:
            async with session.bind.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        # Delete table (expects it exists)
        async with db.session_scope() as session:
            await session.execute(DropTable(element=SQLAlchemyTestR, if_exists=False))

        # Delete table (expects missing)
        async with db.session_scope() as session:
            await session.execute(DropTable(element=SQLAlchemyTestR, if_exists=True))

        await db.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("database_context_schema", ["public"])
@pytest.mark.parametrize("database_context_schema_wiped", [False])
async def test_sqlalchemy_create_schema(database_context: DatabaseContext) -> None:
    schema_name = "test_foobar"
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        # DropTable schema
        async with db.session_scope() as session:
            if database_context.database_type in [DatabaseType.POSTGRESQL]:
                await session.execute(DropSchema(name=schema_name, if_exists=True))
            else:
                pass

        # Create schema (expecting none created before) if supported by the database
        async with db.session_scope() as session:
            if database_context.database_type in [DatabaseType.POSTGRESQL]:
                await session.execute(CreateSchema(name=schema_name, if_not_exists=False))
            else:
                with pytest.raises(NotImplementedError):
                    await session.execute(CreateSchema(name=schema_name, if_not_exists=False))

                return

        # Create schema (expecting none was created before)
        async with db.session_scope() as session:
            with pytest.raises(sqlalchemy.exc.ProgrammingError):
                await session.execute(CreateSchema(name=schema_name, if_not_exists=False))

        # Attempt to create schema (expecting one was created before)
        async with db.session_scope() as session:
            await session.execute(CreateSchema(name=schema_name, if_not_exists=True))

        # DropTable schema (expecting one was created before)
        async with db.session_scope() as session:
            await session.execute(DropSchema(name=schema_name, if_exists=False))

        await db.dispose()
