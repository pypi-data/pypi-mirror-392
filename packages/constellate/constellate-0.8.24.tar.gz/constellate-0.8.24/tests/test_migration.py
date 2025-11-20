from typing import Any

import attr
import more_itertools

from pyexpect import expect
import pytest
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from sqlalchemy import case

from constellate.database.common.databasetype import DatabaseType
from constellate.database.migration.standard.table import (
    MigrationR,
    _MigrationR,
    _MigrationVersionR,
    _MigrationActivityR,
)
from constellate.database.migration.migrationcontext import (
    MigrationContext,
    MigrationLimitedRun,
)
from constellate.database.migration.constant import (
    MigrationKind,
    MigrationCompatibility,
    MigrationAction,
)
from constellate.database.sqlalchemy.execution.execute import (
    execute_scalars_all_iterable,
    execute_scalars_one_or_none,
)
from constellate.database.sqlalchemy.expression.schema.drop import DropSchema
from constellate.database.sqlalchemy.expression.table.presence import HasTable
from .data import test_migration as test_migration_pkg
from _pytest.fixtures import FixtureRequest
from tests.util.database_context import DatabaseContext

Base = declarative_base()


class MigrationTest1R(Base):
    __tablename__ = "test_migration_1"
    __table_args__ = {"schema": "per_unit"}

    did = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class MigrationTest2R(Base):
    __tablename__ = "test_migration_2"
    __table_args__ = {"schema": "per_unit"}

    did = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class MigrationTest3R(Base):
    __tablename__ = "test_migration_3"
    __table_args__ = {"schema": "per_unit"}

    did = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class MigrationTest4R(Base):
    __tablename__ = "test_migration_4"
    __table_args__ = {"schema": "per_unit"}

    did = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class MigrationTest5R(Base):
    __tablename__ = "test_migration_5"
    __table_args__ = {"schema": "per_unit"}

    did = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class PostApplyTestStep0001R(Base):
    __tablename__ = "test_post_apply_step_0001"
    __table_args__ = {"schema": "per_unit"}

    created_on = Column(Integer, primary_key=True)


TEST_MIGRATION_CLASSES = [
    MigrationTest1R,
    MigrationTest2R,
    MigrationTest3R,
    MigrationTest4R,
    MigrationTest5R,
]
TEST_MIGRATION_POST_APPLY_CLASSES = [PostApplyTestStep0001R]


class LibMigrationR(_MigrationR):
    __tablename__ = _MigrationR.__tablename__
    __table_args__ = {"extend_existing": True, "schema": "per_unit"}


class LibMigrationActivityR(_MigrationActivityR):
    __tablename__ = _MigrationActivityR.__tablename__
    __table_args__ = {"extend_existing": True, "schema": "per_unit"}


class LibMigrationVersionR(_MigrationVersionR):
    __tablename__ = _MigrationVersionR.__tablename__
    __table_args__ = {"extend_existing": True, "schema": "per_unit"}


_MIGRATION_PERMANENT_TABLES = [
    LibMigrationR,
    LibMigrationActivityR,
    LibMigrationVersionR,
]  # "_MigrationLockR" == excluded since never permanent

_MIGRATION_PERMANENT_TABLES_NAMES = [t.__tablename__ for t in _MIGRATION_PERMANENT_TABLES]


async def _migration_standard_table_found(session: AsyncSession = None, schema: str = None):
    await session.execute(text(f"SET search_path TO {schema}"))

    found_total = 0
    for table_name in _MIGRATION_PERMANENT_TABLES_NAMES:
        found = await _table_found(session=session, schema=schema, table_name=table_name)
        found_total = found_total + (1 if found else 0)

    if found_total != len(_MIGRATION_PERMANENT_TABLES_NAMES):
        raise ValueError()


# async def _table_found(session:AsyncSession=None, schema:str=None, table_name:str=None) -> bool:
#     stmt = text(
#         f"SELECT EXISTS ( SELECT FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name   = '{table_name}' ); ;"
#     )
#     result = await session.execute(stmt)
#     result = result.fetchall()
#     return True if (len(result) == 1 and result[0][0] is True) else False


async def _table_found(
    session: AsyncSession = None, schema: str = None, table_name: str = None
) -> bool:
    result = await session.execute(HasTable(table=table_name, schema_name=schema))
    return result.first()[0]


def schema_supported(db_type: DatabaseType = DatabaseType.UNKNOWN) -> bool:
    supported = {DatabaseType.POSTGRESQL: True, DatabaseType.SQLITE: False}.get(db_type, None)
    if supported is None:
        raise NotImplementedError()
    return supported


def custom_schema_requested(
    schema: str = None, default_schema: str = None, db_type: DatabaseType = DatabaseType.UNKNOWN
) -> bool:
    return schema_supported(db_type=db_type) and schema != (default_schema or "public")


@attr.s(kw_only=True, auto_attribs=True)
class FileContext:
    filename: str = None
    kind: MigrationKind = None
    table_created: Any = None
    tracked: bool = True


def migration_context_kwargs(schema: str = None, custom_schema_requested: bool = None) -> dict:
    kwargs = {}
    if custom_schema_requested:
        kwargs.update({"schema": schema})
    return kwargs


def strategy_context(
    strategy: list[str] = None, migration_files: list[FileContext] = None
) -> tuple[list[FileContext], list[FileContext]]:
    if strategy is not None and migration_files is not None:
        if strategy == ["first_half"]:
            first_half, _ = more_itertools.divide(2, migration_files)
            second_half = iter([])
        elif strategy == ["first_half", "second_half"]:
            first_half, second_half = more_itertools.divide(2, migration_files)
        elif strategy == ["complete"]:
            first_half = migration_files
            second_half = iter([])
        else:
            raise NotImplementedError()

        return list(first_half), list(second_half)


_MIGRATION_DIRECTORIES = {}
_MIGRATION_DIRECTORIES["modern_0"] = [
    FileContext(
        filename="0000.up.00.bar.sql", kind=MigrationKind.SCHEMA, table_created=MigrationTest1R
    ),
    FileContext(
        filename="0000.up.01.foo.sql", kind=MigrationKind.SCHEMA, table_created=MigrationTest2R
    ),
    FileContext(
        filename="0001.up.00.bar.sql", kind=MigrationKind.DATA, table_created=MigrationTest3R
    ),
    FileContext(
        filename="0001.up.01.foo.sql", kind=MigrationKind.DATA, table_created=MigrationTest4R
    ),
    FileContext(filename="0001.up.02.fab.py", kind=MigrationKind.DATA, table_created=None),
    FileContext(
        filename="0002.up.00.bar.sql", kind=MigrationKind.UNKNOWN, table_created=MigrationTest5R
    ),
    FileContext(
        filename="post-apply.sql",
        kind=MigrationKind.UNKNOWN,
        table_created=PostApplyTestStep0001R,
        tracked=False,
    ),
]


@pytest.mark.parametrize("database_context_schema", ["public", "schema_0"])
@pytest.mark.parametrize("database_context_schema_wiped", [True])
@pytest.mark.parametrize("directory", ["modern_0"])
@pytest.mark.parametrize("strategy", [["first_half"], ["first_half", "second_half"], ["complete"]])
@pytest.mark.parametrize("skip_executing_migration_file", [False, True])
@pytest.mark.asyncio
async def test_migration(
    request: FixtureRequest,
    database_context: DatabaseContext,
    directory: str,
    strategy: list[str],
    skip_executing_migration_file: bool,
) -> None:
    schema = request.getfixturevalue("database_context_schema")
    custom_schema_provided = custom_schema_requested(
        schema=schema, db_type=database_context.database_type
    )
    kwargs = migration_context_kwargs(schema=schema, custom_schema_requested=custom_schema_provided)
    first_half_file_contexts, second_half_file_contexts = strategy_context(
        strategy=strategy, migration_files=_MIGRATION_DIRECTORIES[directory]
    )

    def _non_empty_file_contexts(x):
        return len(x) > 0

    accumumulated_file_contexts = []
    for file_contexts in filter(
        _non_empty_file_contexts, [first_half_file_contexts, second_half_file_contexts]
    ):
        accumumulated_file_contexts.extend(file_contexts)
        migrate_up_to_file = (
            accumumulated_file_contexts[-1] if len(accumumulated_file_contexts) > 0 else None
        )
        for setup_options in database_context.setup_options.get("engines", []):
            limited_run = {}
            if migrate_up_to_file:
                limited_run.update({"table_populated_up_to_file": migrate_up_to_file.filename})

            limited_run.update({"skip_executing_script": skip_executing_migration_file})

            setup_options.update(
                {
                    "migration_context": MigrationContext(
                        database_type=database_context.database_type,
                        action=MigrationAction.UPGRADE,
                        root_pkg_name=test_migration_pkg,
                        directory=directory,
                        compatibility=MigrationCompatibility.V0,
                        dry=MigrationLimitedRun(**limited_run),
                        **kwargs,
                    ),
                }
            )

        async with database_context.storage.setup(options=database_context.setup_options) as db:
            # Migrate it
            await db.migrate(options=database_context.setup_options)

            # Verify library migration scripts have ran and created tables
            async with db.session_scope() as session:
                if schema_supported(db_type=database_context.database_type):
                    await _migration_standard_table_found(session=session, schema=schema)

            # Verify user migration scripts have run in the expected order
            async with db.session_scope() as session:

                @execute_scalars_all_iterable
                async def _read_migrations(*args, **kwargs) -> list[MigrationR]:
                    return select(MigrationR).order_by(MigrationR.applied_at.asc())

                available_files = accumumulated_file_contexts
                migrations = await _read_migrations(session=session)

                # Check all scripts have been applied
                applied_file_names = [m.migration_id for m in migrations]
                available_file_names = [t.filename for t in available_files if t.tracked]
                expect(applied_file_names).to_equal(available_file_names)
                expect(len(applied_file_names)).to_equal(len(available_file_names))

                # Check all scripts have been mark with the right kind
                applied_kinds = [m.kind for m in migrations]
                available_kinds = [t.kind for t in available_files if t.tracked]
                expect(applied_kinds).to_equal(available_kinds)
                expect(len(applied_kinds)).to_equal(len(available_kinds))

                # Check all scripts have been paired with the suitable parent
                parent_hash = None
                for index, m in enumerate(migrations):
                    expect(m.parent_hash).to_equal(None if index == 0 else parent_hash)
                    parent_hash = m.migration_hash

            # Verify user migration scripts have run and created tables
            async with db.session_scope() as session:
                # Check each script created a new table
                test_migration_classes = [
                    fc.table_created
                    for fc in file_contexts
                    if fc.tracked and fc.table_created in TEST_MIGRATION_CLASSES
                ]
                for class_ in test_migration_classes:
                    if skip_executing_migration_file:
                        found = await _table_found(
                            session=session, schema=schema, table_name=class_.__tablename__
                        )
                        expect(found).to_equal(False)
                    else:
                        test = class_(did=0, name="foo")
                        session.add(test)
                await session.commit()

                # Check post-apply script created a new table
                test_migration_post_apply_classes = [
                    fc.table_created
                    for fc in file_contexts
                    if not fc.tracked and fc.table_created in TEST_MIGRATION_POST_APPLY_CLASSES
                ]
                for class_ in test_migration_post_apply_classes:
                    if skip_executing_migration_file:
                        found = await _table_found(
                            session=session, schema=schema, table_name=class_.__tablename__
                        )
                        expect(found).to_equal(False)
                    else:
                        test = class_(created_on=1)
                        session.add(test)
                await session.commit()

                # Check python script created an additional row in table
                if "0001.up.02.fab.py" in [fc.filename for fc in accumumulated_file_contexts]:
                    if not skip_executing_migration_file:

                        @execute_scalars_one_or_none(stmt=True)
                        async def _read_python_step_row(did: str = None, *args, **kwargs):
                            return select(MigrationTest4R).where(MigrationTest4R.did == did)

                        expect("python_step").to_equal(
                            (await _read_python_step_row(session=session, did=1)).name
                        )

            await db.dispose()


@pytest.mark.parametrize("database_context_concurrent_max", [3])
@pytest.mark.parametrize("database_context_concurrent_migration_serialized", [False, True])
@pytest.mark.parametrize("database_context_concurrent_schema", ["public", "schema_0"])
@pytest.mark.parametrize("database_context_concurrent_schema_wiped", [True])
@pytest.mark.parametrize("directory", ["modern_0"])
@pytest.mark.asyncio
async def test_migration_concurrency(
    request: FixtureRequest, database_context_concurrent: DatabaseContext, directory: str
) -> None:
    database_context = database_context_concurrent
    schema = request.getfixturevalue("database_context_concurrent_schema")
    custom_schema_provided = custom_schema_requested(
        schema=schema, db_type=database_context.database_type
    )
    kwargs = migration_context_kwargs(schema=schema, custom_schema_requested=custom_schema_provided)

    # Setup migration per config
    for setup_options in database_context.setup_options.get("engines", []):
        setup_options.update(
            {
                "migration_context": MigrationContext(
                    database_type=database_context.database_type,
                    action=MigrationAction.UPGRADE,
                    root_pkg_name=test_migration_pkg,
                    directory=directory,
                    compatibility=MigrationCompatibility.V0,
                    **kwargs,
                ),
            }
        )

    async with database_context.storage.setup(options=database_context.setup_options) as db:
        # Migrate concurrently amongst configs
        await db.migrate(options=database_context.setup_options)

        for config in db.config_manager.filter(key=lambda x: True):
            async with db.session_scope(config=config) as session:
                for class_ in TEST_MIGRATION_CLASSES:
                    test = class_(did=0, name="foo")
                    session.add(test)
                    await session.commit()

        await db.dispose()


@pytest.mark.parametrize("database_context_schema", ["public", "schema_0"])
@pytest.mark.parametrize("database_context_schema_wiped", [True])
@pytest.mark.parametrize("directory", ["modern_1"])
@pytest.mark.asyncio
async def test_migration_database_compatible_version_check(
    request: FixtureRequest,
    database_context: DatabaseContext,
    directory: str,
) -> None:
    # Migrate database
    schema = request.getfixturevalue("database_context_schema")
    custom_schema_provided = custom_schema_requested(
        schema=schema, default_schema="default_schema", db_type=database_context.database_type
    )
    kwargs = migration_context_kwargs(schema=schema, custom_schema_requested=custom_schema_provided)

    for setup_options in database_context.setup_options.get("engines", []):
        setup_options.update(
            {
                "migration_context": MigrationContext(
                    database_type=database_context.database_type,
                    action=MigrationAction.UPGRADE,
                    root_pkg_name=test_migration_pkg,
                    directory=directory,
                    compatibility=MigrationCompatibility.V0,
                    **kwargs,
                ),
            }
        )

    async with database_context.storage.setup(options=database_context.setup_options) as db:
        await db.migrate(options=database_context.setup_options)

    class LibMigrationVersion2R(_MigrationVersionR):
        __tablename__ = LibMigrationVersionR.__tablename__
        __table_args__ = {
            "extend_existing": True,
            **({"schema": "per_unit"} if custom_schema_provided else {}),
        }

    # Check database user version
    for setup_options in database_context.setup_options.get("engines", []):
        setup_options.update(
            {
                "database_user_version_compatible_query": select(
                    case((LibMigrationVersion2R.version >= 0, True), else_=False)
                )
                .filter(*[LibMigrationVersion2R.version >= 0])
                .limit(1),
                **(
                    {"engine_execution_options": {"schema_translate_map": {"per_unit": schema}}}
                    if custom_schema_provided
                    else {}
                ),
            }
        )

    async with database_context.storage.setup(options=database_context.setup_options) as db:
        compatible = await db.database_compatible(options=database_context.setup_options)
        expect(compatible).to_equal(True)


@pytest.mark.parametrize("database_context_schema", ["public", "schema_0"])
@pytest.mark.parametrize("database_context_schema_wiped", [True])
@pytest.mark.parametrize("directory", ["modern_1"])
@pytest.mark.asyncio
async def test_sqlalchemy_migrate_with_auto_create_schema_when_missing(
    request: FixtureRequest, database_context: DatabaseContext, directory: str
) -> None:
    schema = request.getfixturevalue("database_context_schema")
    if not schema_supported(db_type=database_context.database_type):
        return

    # Setup schema name per config
    for setup_options in database_context.setup_options.get("engines", []):
        setup_options.update({"database_schema_name": schema})

    # Schema auto creation
    async with database_context.storage.setup(options=database_context.setup_options) as db:
        await db.migrate(options=database_context.migrate_options)
        async with db.session_scope() as session:
            await session.execute(DropSchema(name=schema, if_exists=False))

        await db.dispose()
