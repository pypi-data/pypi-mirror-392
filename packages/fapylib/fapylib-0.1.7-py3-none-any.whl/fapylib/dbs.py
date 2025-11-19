""""
Doc String

"""
from pathlib import Path
from alembic import command
from alembic.config import Config
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.schema import CreateSchema as create_schema
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlmodel import (
    SQLModel, 
    MetaData, 
    Field, 
    Session,
    inspect,
    text,
    select, 
    and_, 
    or_, 
    func, 
    cast, 
    String
)

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateType = TypeVar("CreateType", bound=SQLModel)
UpdateType = TypeVar("UpdateType", bound=SQLModel)
QueryType = TypeVar("QueryType", bound=SQLModel)

class ModMeta:
    def __init__(self, basemeta: MetaData):
        def utc_now() -> datetime:
            """Returns current UTC time."""
            return datetime.now(timezone.utc)

        class BaseMeta(SQLModel):
            created_at: datetime = Field(default_factory=utc_now)
            updated_at: datetime = Field(
                default_factory=utc_now,
                sa_column_kwargs={"onupdate": func.now()}
            )

            metadata = basemeta
        self.BaseMeta = BaseMeta

class DbsAmig:
    def __init__(
            self, 
            engine, 
            metadata: MetaData | List[MetaData],
            is_trgm: bool = True,
            ini_config : Optional[str|Path] = None,
            is_downgrade: bool = False,
            dep_env: Optional[str | Path] = None,
            init_mig: Optional[bool] = None,
            ):
        class Deploy(BaseSettings):
            init_mig: bool = False
            model_config = SettingsConfigDict(
                env_file= self.resolve_path(dep_env),
                env_file_encoding="utf-8",
                extra="ignore",
            )
        self.init_mig = init_mig or Deploy().init_mig
        self.engine = engine
        self.metadata = metadata
        self.is_trgm = is_trgm
        self.ini_config = str(ini_config) if ini_config is not None else None
        self.is_downgrade = is_downgrade

    @asynccontextmanager
    async def migspan(self):
        self.create_extrgm(self.engine, self.is_trgm)
        if isinstance(self.metadata, MetaData):
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
        if isinstance(self.metadata, List):
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

class DbsMsvc(Generic[ModelType, CreateType, UpdateType, QueryType]):
    def __init__(self, model: Type[ModelType], query_type: str = "all"):
        self.model = model
        self.query_type = query_type

    async def create(self, session: Session, data: CreateType) -> ModelType:
        db_obj = self.model.model_validate(data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    async def read(
        self,
        session: Session,
        offset: int = 0,
        limit: int = 100,
        query: Optional[QueryType] = None,
        query_type: Optional[str] = None,
    ) -> List[ModelType]:
        statement = select(self.model)

        if query:
            filters = []
            query_type = query_type or getattr(query, "query_type", self.query_type)
            query_fields = query.model_dump(exclude_unset=True)
            query_fields.pop("query_type", None)

            for field, value in query_fields.items():
                column = getattr(self.model, field, None)
                if column is not None and value is not None:
                    if query_type == "sim" and isinstance(value, str):
                        if " " in value.strip():
                            filters.append(func.similarity(column, value) > 0.3)
                        else:
                            filters.append(cast(column, String).ilike(f"{value}%"))
                    else:
                        filters.append(column == value)

            if filters:
                if query_type == "all":
                    statement = statement.where(and_(*filters))
                elif query_type == "any":
                    statement = statement.where(or_(*filters))
                elif query_type == "sim":
                    statement = statement.where(and_(*filters))

        return list(session.exec(statement.offset(offset).limit(limit)))

    async def read_byid(
        self, 
        session: Session, 
        id: int | str
    ) -> Optional[ModelType]:
        return session.get(self.model, id)

    async def update(
        self, 
        session: Session, 
        id: int | str, 
        data: CreateType | UpdateType
    ) -> Optional[ModelType]:
        db_obj = session.get(self.model, id)
        if db_obj is None:
            return None
        db_obj.sqlmodel_update(data.model_dump(exclude_unset=True))
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    async def delete_byid(
        self, 
        session: Session, 
        id: int | str
    ) -> bool:
        db_obj = session.get(self.model, id)
        if db_obj:
            session.delete(db_obj)
            session.commit()
            return True
        return False