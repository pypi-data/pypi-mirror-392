"""
Doc String

"""
from typing import Dict, Any, Annotated, Optional, List
from fastapi import FastAPI, Request, Depends
from sqlmodel import MetaData, Session
from contextlib import asynccontextmanager, AsyncExitStack

__all__ = ["AppMeta", "AppSpan", "AppMsvc"]

class AppMeta:
    def __init__(self, metas: Dict[str, MetaData]):
        self.metalist = list(metas.values())
        self.schmlist = list(metas.keys())
        self.metadict = metas


class AppSpan:
        def __init__(
                self,
                amigs: Optional[List[Any]] = None,
                spans: Optional[Dict[FastAPI, Any]] = None,
            ):
            self.amig_list = amigs or []
            self.span_dict = spans or {} 

        @asynccontextmanager
        async def lifespan(self, app: FastAPI):
            app.state.appspan = True
            async with AsyncExitStack() as stack:
                # Manage the lifecycle of sub_app
                for subamig in self.amig_list:
                    await stack.enter_async_context(subamig())
                for subapp, subspan in self.span_dict.items():
                    await stack.enter_async_context(subspan(subapp))
                yield

class AppMsvc:
    def __init__(self, apps: Dict[str, FastAPI], lifespan, sessdep: Optional[Any] = None):
        depends = [Depends(self.session(sessdep))] if sessdep is not None else None
        self.app = FastAPI(dependencies= depends,  lifespan=lifespan)
        app_msg = {"message": "Hello Multi Micro Services API!"}
        for key, subapp in apps.items():
            self.app.mount(f"/{key}", subapp)
            app_msg[key] = f"{key.capitalize()} Service at '/{key}'"
        @self.app.get("/")
        async def root():
            return app_msg
        
    @staticmethod
    def session(sessdep):
        def _session(
            request: Request, 
            sess_pgs: Annotated[Session, Depends(sessdep)]
        ):
            """Injects session into request scope."""
            request.scope["db"] = {"pgsql": sess_pgs}
        return _session
        
        