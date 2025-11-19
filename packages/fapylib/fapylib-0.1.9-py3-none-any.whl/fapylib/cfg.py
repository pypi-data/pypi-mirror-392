"""
PostgreSQL configuration, engine, and session management using Pydantic and SQLModel.
"""

from pathlib import Path
from typing import Annotated, Optional
from functools import lru_cache
from fastapi import Request, Depends
from sqlmodel import create_engine, Session
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["PgsCore", "SrvCore"]

class SrvCore:
    class Base(BaseSettings):
        host: str = "0.0.0.0"
        port: int = 8080
        reload: bool = False

    def __init__(self, dep_env: Optional[str | Path] = None, srv_env: Optional[str | Path] = None):

        class Deploy(BaseSettings):
            srv_env: str = ".env"
            model_config = SettingsConfigDict(
                env_file= self.resolve_path(dep_env),
                env_file_encoding="utf-8",
                extra="ignore",
            )
        self.env_path = self.resolve_path(srv_env, Deploy().srv_env)
    
    @property
    def config(self):
        return self.get_config(self.env_path)
    
    @classmethod
    @lru_cache
    def get_config(cls, srv_env : Optional[str | Path] = None):
        env_path = cls.resolve_path(srv_env, ".env")

        class Config(cls.Base):
            model_config = SettingsConfigDict(
                env_file=env_path,
                env_file_encoding="utf-8",
                extra="ignore",
            )
        return Config()
    
    @staticmethod
    def resolve_path(path: Optional[str | Path], default: Optional[str] = None) -> str | None:
        return str(path) if path and Path(path).exists() else default

class PgsCore:
    class Base(BaseSettings):
        postgres_host: str = "0.0.0.0"
        postgres_port: int = 5432
        postgres_database: str = "sqlapp"
        postgres_username: str = "usr"
        postgres_password: str = "pwd"
        postgres_admin_username: str = "adminusr"
        postgres_admin_password: str = "adminpwd"

    def __init__(
            self, 
            dep_env: Optional[str | Path] = None, 
            pgs_env: Optional[str | Path] = None, 
            pgs_secrets: Optional[str | Path] = None,
            is_admin: bool = False
        ):
        class Deploy(BaseSettings):
            pgs_env: str = ".env"
            pgs_secrets: str = "."

            model_config = SettingsConfigDict(
                env_file=self.resolve_path(dep_env),
                env_file_encoding="utf-8",
                extra="ignore",
            )
        self.env_path = self.resolve_path(pgs_env, Deploy().pgs_env)
        self.secrets_path = self.resolve_path(pgs_secrets, Deploy().pgs_secrets)
        self.is_admin = is_admin

    @property
    def pgurl(self):
        return self.get_pgurl(self.env_path, self.secrets_path, self.is_admin)
        
    def engine(self):
        return self.get_engine(self.env_path, self.secrets_path, self.is_admin)
        
    def session(self):
        return Session(autocommit=False, autoflush=False, bind=self.engine())

    def sessdep(self):
        db = self.session()
        try:
            yield db
        finally:
            db.close()

    def sesspgs(self):
        def _sesspgs(
            request: Request, 
            sess_pgs: Annotated[Session, Depends(self.sessdep)]
        ):
            """Injects session into request scope."""
            request.scope["db"] = {"pgsql": sess_pgs}
        return _sesspgs


    @classmethod
    @lru_cache
    def get_config(
        cls, 
        pgs_env : Optional[str | Path] = None, 
        pgs_secrets : Optional[str | Path] = None
    ):
        class Config(cls.Base):
            model_config = SettingsConfigDict(
                env_file=cls.resolve_path(pgs_env, ".env"),
                env_file_encoding="utf-8",
                extra="ignore",
                secrets_dir=cls.resolve_path(pgs_secrets, ".")
            )
        return Config()
    
    @classmethod
    def get_pgurl(
        cls, 
        pgs_env : Optional[str | Path] = None, 
        pgs_secrets : Optional[str | Path] = None, 
        is_admin: bool = False
        ):
        env_path = cls.resolve_path(pgs_env, ".env")
        secrets_path = cls.resolve_path(pgs_secrets, ".")
        cfg = cls.get_config(env_path, secrets_path)
        return (
                "postgresql://{username}:{password}@{host}:{port}/{db_name}".format(
                    host=cfg.postgres_host,
                    port=cfg.postgres_port,
                    db_name=cfg.postgres_database,
                    username=cfg.postgres_admin_username if is_admin else cfg.postgres_username,
                    password=cfg.postgres_admin_password if is_admin else cfg.postgres_password,
                )
            )
    
    @classmethod
    @lru_cache
    def get_engine(
        cls, 
        pgs_env : Optional[str | Path] = None, 
        pgs_secrets : Optional[str | Path] = None,
        is_admin: bool = False
        ):
        env_path = cls.resolve_path(pgs_env, ".env")
        secrets_path = cls.resolve_path(pgs_secrets, ".")
        pgurl = cls.get_pgurl(env_path, secrets_path, is_admin)
        return create_engine(pgurl, echo=True, future=True) 
    
    @staticmethod
    def resolve_path(path: Optional[str | Path], default: Optional[str] = None) -> str | None:
        return str(path) if path and Path(path).exists() else default