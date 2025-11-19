""""
Doc String

"""
from typing import (
    List, 
    Optional, 
    Iterable, 
    Iterator, 
    cast,
)
from pathlib import Path
from alembic import command

from alembic.config import Config
from alembic import context
from alembic.environment import MigrationContext
from alembic.operations.ops import (
    MigrationScript,
    MigrateOperation,
    DropTableOp,
    DropIndexOp,
    ModifyTableOps,
)
from logging.config import fileConfig
from contextlib import asynccontextmanager

from sqlalchemy import engine_from_config, pool
from sqlalchemy.schema import CreateSchema as create_schema
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlmodel import (
    SQLModel, 
    MetaData, 
    inspect,
    text
)

__all__ = ["DbsAmig", "EnvAlem"]

class EnvAlem:
    def __init__(self, pgurl: str, metalist: list):
        self.config = context.config
        self.pgurl = pgurl
        self.target_metadata = metalist

        if self.config.config_file_name:
            fileConfig(self.config.config_file_name)

    def include_object(self, object, name, type_, reflected, compare_to):
        return not (type_ == "table" and reflected and compare_to is None)

    def process_revision_directives(
        self,
        context: MigrationContext,
        revision: str | Iterable[str | None] | Iterable[str],
        directives: list[MigrationScript],
    ):
        if getattr(self.config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops and script.upgrade_ops.is_empty():
                directives.clear()

        script = directives[0]
        for directive in (script.upgrade_ops, script.downgrade_ops):
            if directive:
                tables_dropped = {
                    (op.table_name, op.schema)
                    for op in directive.ops
                    if isinstance(op, DropTableOp)
                }
                filtered_ops = list(self._filter_drop_indexes(directive.ops, tables_dropped))
                directive.ops = cast(list[MigrateOperation], filtered_ops)

    def _filter_drop_indexes(
        self,
        directives: list[MigrateOperation],
        tables_dropped: set[tuple[str, str | None]],
    ) -> Iterator[MigrateOperation]:
        for directive in directives:
            if isinstance(directive, ModifyTableOps) and (directive.table_name, directive.schema) in tables_dropped:
                filtered_inner = list(self._filter_drop_indexes(directive.ops, tables_dropped))
                directive.ops = cast(list[MigrateOperation], filtered_inner)
                if not directive.ops:
                    continue
            elif isinstance(directive, DropIndexOp) and (directive.table_name, directive.schema) in tables_dropped:
                continue
            yield directive

    def run_migrations_offline(self):
        self.config.set_main_option("sqlalchemy.url", self.pgurl)

        url = self.config.get_main_option("sqlalchemy.url")
        for target_meta in self.target_metadata:
            context.configure(
                url=url,
                target_metadata=target_meta,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
                process_revision_directives=self.process_revision_directives,
                include_object=self.include_object,
                render_as_batch=True,
                user_module_prefix="sqlmodel.sql.sqltypes.",
                template_args={
                    "schema_creation": f'op.execute("CREATE SCHEMA IF NOT EXISTS {target_meta.schema}")'
                },
                echo=True,
            )
            with context.begin_transaction():
                context.run_migrations()

    def run_migrations_online(self):
        self.config.set_main_option("sqlalchemy.url", self.pgurl)
        connectable = self.config.attributes.get('connectable')
        targetmeta = self.config.attributes.get('targetmeta')

        if connectable is None:
            connectable = engine_from_config(
                self.config.get_section(self.config.config_ini_section, {}),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )

        with connectable.connect() as connection:
            metas = [targetmeta] if targetmeta else self.target_metadata
            for meta in metas:
                context.configure(
                    connection=connection,
                    target_metadata=meta,
                    process_revision_directives=self.process_revision_directives,
                    include_object=self.include_object,
                    render_as_batch=True,
                    user_module_prefix="sqlmodel.sql.sqltypes.",
                    template_args={
                        "schema_creation": f'op.execute("CREATE SCHEMA IF NOT EXISTS {meta.schema}")'
                    },
                    echo=True,
                )
                with context.begin_transaction():
                    context.run_migrations()


class DbsAmig:
    def __init__(
            self, 
            engine, 
            metadata: MetaData | List[MetaData],
            is_trgm: bool = True,
            ini_config : Optional[str|Path] = None,
            is_downgrade: bool = False,
            dep_env: Optional[str | Path] = None,
            init_dbamig: Optional[bool] = None,
            ):
        class Deploy(BaseSettings):
            init_dbamig: bool = False
            model_config = SettingsConfigDict(
                env_file= self.resolve_path(dep_env),
                env_file_encoding="utf-8",
                extra="ignore",
            )
        self.init_dbamig = init_dbamig or Deploy().init_dbamig
        self.engine = engine
        self.metadata = metadata
        self.is_trgm = is_trgm
        self.ini_config = str(ini_config) if ini_config is not None else None
        self.is_downgrade = is_downgrade

    @asynccontextmanager
    async def migspan(self):
        self.create_extrgm(self.engine, self.is_trgm)
        if isinstance(self.metadata, MetaData) and self.init_dbamig:
            if self.ini_config is not None:
                self.alembic_migrate(
                    self.engine, 
                    self.metadata, 
                    self.ini_config,
                    self.is_downgrade
                    )
            else:
                self.create_schema(
                    self.engine, 
                    self.metadata
                    )
                self.create_tables(
                    self.engine, 
                    self.metadata
                    )
        yield

    def migrate(self):
        self.create_extrgm(self.engine, self.is_trgm)
        if isinstance(self.metadata, List) and self.init_dbamig:
            for metadata in self.metadata:
                if isinstance(metadata, MetaData):
                    if self.ini_config is not None:
                        self.alembic_migrate(
                            self.engine, 
                            metadata, 
                            self.ini_config,
                            self.is_downgrade
                        )
                    else:
                        self.create_schema(
                            self.engine, 
                            metadata
                        )
                        self.create_tables(
                            self.engine, 
                            metadata
                        )

    @staticmethod
    def create_extrgm(engine, is_trgm: bool = True):
        if is_trgm:
            with engine().connect() as connection:
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
                connection.commit()

    @staticmethod
    def create_schema(engine, metadata):
        schema = metadata.schema
        with engine().connect() as connection:
            if schema and not inspect(connection).has_schema(schema):
                connection.execute(create_schema(schema))
                connection.commit()

    @staticmethod
    def create_tables(engine, metadata):
        if metadata and metadata.schema:
            metadata.create_all(engine())

        else:
            SQLModel.metadata.create_all(engine())

    @staticmethod
    def alembic_migrate(engine, metadata, ini_config, is_downgrade: bool =False):
        def init_migrate(metadata):
            cfg = Config(ini_config)
            cfg.attributes['connectable'] = engine()
            cfg.attributes['targetmeta'] = metadata
            if is_downgrade:
                command.downgrade(cfg, "head")
            else:
                command.upgrade(cfg, "head")
        if metadata and metadata.schema:
            init_migrate(metadata)

        else:
            init_migrate(SQLModel.metadata)
    
    @staticmethod
    def resolve_path(path: Optional[str | Path], default: Optional[str] = None) -> str | None:
        return str(path) if path and Path(path).exists() else default