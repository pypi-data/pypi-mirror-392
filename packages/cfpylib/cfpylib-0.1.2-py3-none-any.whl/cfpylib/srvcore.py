from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["SrvCore"]

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