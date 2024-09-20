import atexit
import importlib.resources as importlib_resources
import logging
import logging.config
import queue
import tomllib
from functools import lru_cache
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path

from pydantic import ConfigDict, validate_call, TypeAdapter

import resources
from backend.custom_log_handlers.streamlit_log_handler import \
    StreamlitLogHandler
from data_structures import AppConfig

log = logging.getLogger("svg-transform")


@lru_cache
def validation_configs(frozen=True):
    return ConfigDict(
        arbitrary_types_allowed=True,
        frozen=frozen,
        from_attributes=True,
        revalidate_instances="never",
        use_enum_values=True,
    )


@validate_call(config=validation_configs())
def read_app_toml(filename: str = "app.toml") -> AppConfig:
    toml_file = read_resource(filename)
    app_configs_json = tomllib.loads(toml_file)
    type_adapter = TypeAdapter(AppConfig)
    return type_adapter.validate_python(app_configs_json)


@validate_call(config=validation_configs())
def set_logging_configs(configs: AppConfig, streamlit_queue: queue.Queue):
    """
    :param configs: AppConfig object - mapped from toml file
    :param streamlit_queue: A queue to communicate between the
         streamlit handler and the actual display
    """
    dumped_logging = configs.logging.model_dump(by_alias=True)
    logging.config.dictConfig(dumped_logging)
    st_handler = StreamlitLogHandler(streamlit_queue)

    root_logger = logging.getLogger()
    all_handlers = root_logger.handlers
    all_handlers.append(st_handler)

    q = queue.Queue()
    queue_handler = QueueHandler(q)
    queue_listener = QueueListener(q, *all_handlers, respect_handler_level=True)
    root_logger.handlers = [queue_handler]
    queue_listener.start()
    atexit.register(queue_listener.stop)


@validate_call(config=validation_configs())
def read_resource(filename: str) -> str:
    resources_path = Path(str(importlib_resources.files(resources)))
    filepath = resources_path / filename
    with open(filepath) as f:
        return f.read()
