""""
Doc String

"""
from enum import Enum

from sqlmodel import SQLModel, Session
from fastapi.responses import JSONResponse
from typing import TypeVar, Generic, Type, List, Dict, Any, Annotated, Optional, cast
from fastapi import  APIRouter, Depends, Request, HTTPException, status, Query


__all__ = ["AprSrvc", "AprResp", "AprMsvc"]

# Define type variables
PublicType = TypeVar("PublicType", bound=SQLModel)
CreateType = TypeVar("CreateType", bound=SQLModel)
UpdateType = TypeVar("UpdateType", bound=SQLModel)
QueryType = TypeVar("QueryType", bound=SQLModel)


        
class AprSrvc(Generic[PublicType, CreateType, UpdateType, QueryType]):
    def __init__(
        self,
        crud_obj,
        public_schema: Type[PublicType], 
    ):
        self.crud = crud_obj
        self.public_schema = public_schema
        
    async def create(
        self,
        session: Session,
        data: CreateType,
    ) -> PublicType:
        obj = await self.crud.create(session=session, data=data)
        return self.public_schema.model_validate(obj)

    async def read(
        self,
        session: Session,
        query: QueryType,
        offset: int = 0,
        limit: int = 100,
        query_type: Optional[str] = None,
    ) -> List[PublicType]:
        results = await self.crud.read(
            session=session,
            offset=offset,
            limit=limit,
            query=query,
            query_type = query_type,
        )
        return [self.public_schema.model_validate(obj) for obj in results]

    async def read_by_id(
        self,
        session: Session,
        id: int | str,
    ) -> Optional[PublicType]:
        obj = await self.crud.read_byid(session=session, id=id)
        return self.public_schema.model_validate(obj) if obj else None

    async def replace(
        self,
        session: Session,
        id: int | str,
        data: CreateType,
    ) -> PublicType:
        existing = await self.crud.read_byid(session=session, id=id)
        if not existing or existing.id != id:
            created = await self.crud.create(session=session, data=data)
            return self.public_schema.model_validate(created)
        updated = await self.crud.update(session=session, id=id, data=data)
        return self.public_schema.model_validate(updated)

    async def update(
        self,
        session: Session,
        id: int | str,
        data: UpdateType,
    ) -> Optional[PublicType]:
        existing = await self.crud.read_byid(session=session, id=id)
        if existing and existing.id == id:
            updated = await self.crud.update(session=session, id=id, data=data)
            return self.public_schema.model_validate(updated)
        return None

    async def delete(
        self,
        session: Session,
        id: int | str,
    ) -> None:
        existing = await self.crud.read_byid(session=session, id=id)
        if existing and existing.id == id:
            await self.crud.delete_byid(session=session, id=id)
        
class AprResp(Generic[PublicType, CreateType, UpdateType, QueryType]):
    def __init__(
        self,
        service_obj
    ):
        self.service = service_obj
    
    async def create(
            self,
            request: Request,
            data: Annotated[CreateType, Depends()],
        ) -> PublicType:
        try:
            db_session = request.scope["db"]["pgsql"]
            result = await self.service.create(
                session=db_session,
                data=data,
            )
            return result
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Create Model Failed {exc}",
            ) from exc
    
    async def get(
        self,
        request: Request,
        query: Annotated[QueryType, Depends()],
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
        query_type: Optional[str] = None,
    ) -> List[PublicType]:
        try:
            db_session = request.scope["db"]["pgsql"]
            results = await self.service.read(
                session=db_session,
                offset=offset,
                limit=limit,
                query=query,
                query_type = query_type,
            )
            return results
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Data Request Failed {exc}",
            ) from exc

    async def get_byid(
        self,
        request: Request,
        id: int | str,
    ) -> PublicType:
        try:
            db_session = request.scope["db"]["pgsql"]
            result = await self.service.read_by_id(
                session=db_session,
                id=id,
            )
            return result
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Data Request Failed {exc}",
            ) from exc

    async def replace(
        self,
        request: Request,
        id: int | str,
        data: Annotated[CreateType, Depends()],
    ) -> PublicType:
        try:
            db_session = request.scope["db"]["pgsql"]
            result = await self.service.replace(
                session=db_session,
                id=id,
                data=data,
            )
            return result
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Replace Model Failed {exc}",
            ) from exc

    async def update(
        self,
        request: Request,
        id: int | str,
        data: Annotated[UpdateType, Depends()],
    ) -> PublicType:
        try:
            db_session = request.scope["db"]["pgsql"]
            result = await self.service.update(
                session=db_session,
                id=id,
                data=data,
            )
            return result
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Update Model Failed {exc}",
            ) from exc

    async def delete(
        self,
        request: Request,
        id: int | str,
    ) -> JSONResponse:
        try:
            db_session = request.scope["db"]["pgsql"]
            await self.service.delete(
                session=db_session,
                id=id,
            )
            return JSONResponse(content={"removed": True}, status_code=200)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error: Delete Failed {exc}",
            ) from exc
        
class AprMsvc:
    def __init__(
        self,
        prefix: str = "",
        tags: List[str | Enum] | None = None,
        resp_map: Dict[str, Any] | None = None,
    ):
        self.router = APIRouter(
            prefix=prefix,
            tags=tags,
            responses={404: {"description": "Not found"}},
        )
        if resp_map is not None:
            self._register_routes(resp_map)

    def _register_routes(self, resp_map):
        for name, resp in resp_map.items():
            self._add_routes(name, resp)

    def _add_routes(self, name: str, resp: Any):
        # POST /<name>
        @self.router.post(f"/{name}")
        async def create(_response=Depends(resp.create)):
            """Create item"""
            return _response

        # GET /<name>
        @self.router.get(f"/{name}")
        async def get(_response=Depends(resp.get)):
            """Get list of items"""
            return _response

        # GET /<name>/{id}
        @self.router.get(f"/{name}/{{id}}")
        async def get_byid(_response=Depends(resp.get_byid)):
            """Get item by ID"""
            return _response

        # PUT /<name>/{id}
        @self.router.put(f"/{name}/{{id}}")
        async def replace(_response=Depends(resp.replace)):
            """Replace item"""
            return _response

        # PATCH /<name>/{id}
        @self.router.patch(f"/{name}/{{id}}")
        async def update(_response=Depends(resp.update)):
            """Update item"""
            return _response

        # DELETE /<name>/{id}
        @self.router.delete(f"/{name}/{{id}}")
        async def delete(_response=Depends(resp.delete)):
            """Delete item"""
            return _response