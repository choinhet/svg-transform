import asyncio
import logging.config
import queue

import streamlit as st
from pydantic import validate_call
from streamlit.runtime.uploaded_file_manager import UploadedFile

from backend.colors import load_colors
from backend.configs import read_app_toml, set_logging_configs, \
    read_resource, validation_configs
from backend.data_structure import ViewBox
from frontend.console_view import console_view

st.set_page_config("Svg Transform", "🖼️")
log = logging.getLogger("svg-transform")


@validate_call(config=validation_configs())
def load_file(file: UploadedFile, view_box: ViewBox):
    svg_text = file.read().decode()
    template_html = read_resource("svg_display.html")
    template = template_html.replace("%SVG%", svg_text)
    view_box.current_file = template
    log.info("Updated last file in view_box")


@st.cache_resource
def init_configs() -> ViewBox:
    configs = read_app_toml()
    streamlit_queue = queue.Queue()
    set_logging_configs(configs, streamlit_queue)
    return ViewBox(
        st_queue=streamlit_queue,
        current_file=None,
        filename="null.txt"
    )


async def main():
    view_box = init_configs()

    tab1, tab2 = st.tabs(["Handler", "Console"])

    with tab1:
        new_file = st.file_uploader("Upload Image", type=["svg"])
        st.download_button(
            label="Download current",
            data=view_box.current_file or "",
            file_name=view_box.filename,
            disabled=view_box.current_file is None,
            use_container_width=True
        )

        if new_file is not None:
            view_box.filename = new_file.name
            load_file(new_file, view_box)

        if view_box.current_file is not None:
            colors = await load_colors(view_box.current_file)
            st.write("Distinct colors identified")
            st.write(", ".join(colors))
            st.markdown(view_box.current_file, unsafe_allow_html=True)

    with tab2:
        await console_view(view_box.st_queue)


if __name__ == "__main__":
    asyncio.run(main())
