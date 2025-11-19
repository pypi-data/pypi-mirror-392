from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="EXTAPI_",
        extra="ignore",
    )

    debug: bool = False
    ncae_base_url: str
    ncae_username: str
    ncae_password: str
    ncae_verify_tls: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
