import os
from functools import partial

from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    host: str = Field(alias="DB_HOST", default="localhost")
    port: int = Field(alias="DB_PORT", default=5432)
    username: str = Field(alias="DB_USER", default="bot_user")
    password: str = Field(alias="DB_PASS", default="bot_db_password")
    database: str = Field(alias="DB_NAME", default="database")


class Config(BaseModel):
    token: str = Field(
        default_factory=partial(os.getenv, "TOKEN")
    )
    wkhtmltoimage_path: str = Field(
        default_factory=partial(os.getenv, "WKHTMLTOIMAGE_BIN")
    )
    postgres: PostgresConfig = Field(
        default_factory=lambda: PostgresConfig(**os.environ)
    )
