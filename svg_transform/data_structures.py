from typing import Dict, Annotated, List

from pydantic import BaseModel, Field, ConfigDict


class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class LoggerProps(Model):
    handlers: List[str]
    level: str
    propagate: bool


class HandlerProps(Model):
    level: str
    formatter: str
    clz: Annotated[str, Field(
        alias="class",
        serialization_alias="class",
    )]


class FormatterProps(Model):
    format: str
    datefmt: str


class Logging(Model):
    version: int
    disable_existing_loggers: bool
    loggers: Dict[str, LoggerProps]
    handlers: Dict[str, HandlerProps]
    formatters: Dict[str, FormatterProps]


class AppConfig(Model):
    logging: Logging
