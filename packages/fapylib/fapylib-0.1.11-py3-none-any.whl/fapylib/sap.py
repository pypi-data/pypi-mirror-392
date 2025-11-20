"""
Doc String

"""
import secrets
from typing import List, Annotated
from sqlmodel import MetaData, Session
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Request, Depends
from starlette.middleware.sessions import SessionMiddleware


__all__ = ["SubMeta", "SubSpan", "SubMsvc"]

class Middleware:
    def __init__(self, app: FastAPI):
        self.app = app

    def _secret_key(self, length: int = 16) -> str:
        return secrets.token_urlsafe(length)

    def add_session(self, secret_key: str | None = None):
        if not secret_key:
            secret_key = self._secret_key()
        self.app.add_middleware(SessionMiddleware, secret_key=secret_key)

class PgsqlCore:
    def __init__(self):
        self.db = None

    def initdb(self, request: Request):
        session = request.app.state.db["session"]["pgsql"]
        engine = request.app.state.db["engine"]["pgsql"]
        if session:
            self.db = session()
        else:
            self.db = Session(
                autocommit=False, 
                autoflush=False, 
                bind=engine()
            )

    def sessdep(self, request: Request):
        self.initdb(request)
        try:
            if self.db:
                yield self.db
        finally:
            if self.db:
                self.db.close()

class SubMeta:
    def __init__(self, schema: str = "public"):
        self.schema = schema.lower()
        self.metadata = MetaData(schema=self.schema)

class SubSpan:
    def __init__(self, engine, session):
        self.engine = engine
        self.state = {
            "engine": {"pgsql": engine},
            "session": {"pgsql": session},
        }
        
    @asynccontextmanager
    async def lifespan(self, _app: FastAPI):
        _app.state.db = self.state
        yield



class SubMsvc:
    def __init__(self, name: str, routers: List[APIRouter]):
        self.name = name.lower()
        self.app = FastAPI(dependencies=[Depends(self.session)])
        self.middleware = Middleware(self.app)
        self.middleware.add_session()
        for router in routers:
            self.app.include_router(router)
        @self.app.get("/")
        async def root():
            return {"message": f"Hello {name.capitalize()} Microservice!"}
        
    @staticmethod
    def session(
        request: Request, 
        sess_pgs: Annotated[Session, Depends(PgsqlCore().sessdep)]
    ):
        """Injects session into request scope."""
        request.scope["db"] = {"pgsql": sess_pgs}