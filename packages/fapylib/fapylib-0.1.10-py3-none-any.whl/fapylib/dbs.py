""""
Doc String

"""
from typing import (
    Type, 
    TypeVar, 
    Generic, 
    List, 
    Optional
)

from datetime import datetime, timezone

from sqlmodel import (
    SQLModel, 
    MetaData, 
    Field, 
    Session,
    select, 
    and_, 
    or_, 
    func, 
    cast, 
    String
)

__all__ = ["ModMeta", "DbsMsvc"]

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
        query: QueryType,
        offset: int = 0,
        limit: int = 100,
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