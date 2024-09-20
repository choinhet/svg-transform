import asyncio
import atexit
import importlib.resources as importlib_resources
import logging
import logging.config
import queue
import tomllib
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from typing import cast

import aiofiles
import streamlit as st
from pydantic import TypeAdapter, validate_call, ConfigDict
from streamlit.runtime.uploaded_file_manager import UploadedFile

import resources
from custom_log_handlers.streamlit_log_handler import StreamlitLogHandler
from svg_transform.data_structures import AppConfig

st.set_page_config("Svg Transform", "🖼️")
log = logging.getLogger("svg-transform")


async def init_configs():
    if "init" in st.session_state:
        return
    configs = await read_configs()
    dumped_logging = configs.logging.model_dump(by_alias=True)
    logging.config.dictConfig(
        dumped_logging
    )
    streamlit_queue = queue.Queue()
    await set_logging_configs(streamlit_queue)
    st.session_state["init"] = True
    st.session_state["st_queue"] = streamlit_queue


@st.cache_resource
def validation_configs() -> ConfigDict:
    return ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
        revalidate_instances="never",
        validate_default=False
    )


@validate_call(config=validation_configs())
async def read_configs(filename: str = "app.toml") -> AppConfig:
    toml_file = await read_resource(filename)
    app_configs_json = tomllib.loads(toml_file)
    type_adapter = TypeAdapter(AppConfig)
    return type_adapter.validate_python(app_configs_json)


@validate_call(config=validation_configs())
async def set_logging_configs(streamlit_queue: queue.Queue):
    """
    :param streamlit_queue: A queue to communicate between the
         streamlit handler and the actual display
    """
    st_handler = StreamlitLogHandler(streamlit_queue)
    q = queue.Queue()
    queue_handler = QueueHandler(q)
    root_logger = logging.getLogger()
    all_handlers = root_logger.handlers
    all_handlers.append(st_handler)
    queue_listener = QueueListener(
        q,
        *all_handlers,
        respect_handler_level=True
    )
    root_logger.handlers = [queue_handler]
    queue_listener.start()
    atexit.register(queue_listener.stop)


@validate_call(config=validation_configs())
async def read_resource(filename: str) -> str:
    resources_path = Path(str(importlib_resources.files(resources)))
    filepath = resources_path / filename
    async with aiofiles.open(filepath) as f:
        return await f.read()


def render_file(text: str):
    st.markdown(text, unsafe_allow_html=True)


@validate_call(config=validation_configs())
async def console_view(st_queue: queue.Queue):
    if st.button("Clear"):
        st.session_state["msgs"] = []
    msgs = st.session_state.get("msgs", [])
    while True:
        try:
            await asyncio.sleep(0.15)
            msg = st_queue.get_nowait()
            msgs.append(msg)
            st.session_state["msgs"] = msgs
        except queue.Empty:
            st.code("\n".join(msgs), language="log")
            break


@validate_call(config=validation_configs())
async def load_file(file: UploadedFile):
    svg_text = file.read().decode()
    template_html = await read_resource("svg_display.html")
    template = template_html.replace("%SVG%", svg_text)
    st.session_state["last_file"] = template
    log.info("Updated last file in session state")
    st.session_state["file_changed"] = False


def update_file_change_var():
    st.session_state["file_changed"] = True
    log.info("Updated file changed variable")


async def main():
    await init_configs()

    tab1, tab2 = st.tabs(["Handler", "Console"])
    with tab1:
        file = st.file_uploader(
            "Input your '.svg' file",
            accept_multiple_files=False,
            on_change=update_file_change_var
        )
        log.info(f"File changed: {st.session_state.get("file_changed")}")
        log.info(f"Current file: {file}")

        if st.session_state.get("file_changed") and file is not None:
            log.info("File changed")
            await load_file(file)
        log.info(f"Last file: {st.session_state.get("last_file")}")

        if (last_file := st.session_state.get("last_file")) is not None:
            log.info("Rendering last file")
            render_file(last_file)

    with tab2:
        q = cast(queue.Queue, st.session_state.get("st_queue"))
        await console_view(q)


if __name__ == "__main__":
    asyncio.run(main())
