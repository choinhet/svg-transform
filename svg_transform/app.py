import asyncio
import logging.config
import queue
from copy import copy
from typing import cast

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
def load_file(file: UploadedFile, view_box: ViewBox) -> ViewBox:
    svg_text = file.read().decode()
    template_html = read_resource("svg_display.html")
    template = template_html.replace("%SVG%", svg_text)
    log.info("Updated last file in view_box")
    return view_box.copy(update=dict(filename=file.name, current_file=template))


@st.cache_resource
def default_view_box() -> ViewBox:
    configs = read_app_toml()
    streamlit_queue = queue.Queue()
    set_logging_configs(configs, streamlit_queue)
    return ViewBox(
        st_queue=streamlit_queue,
        current_file=None,
        filename=None,
    )


async def main():
    if "view_box" not in st.session_state:
        st.session_state["view_box"] = default_view_box()

    view_box = copy(st.session_state["view_box"])

    tab1, tab2 = st.tabs(["Handler", "Console"])

    with tab1:
        new_file = st.file_uploader("Upload Image", type=["svg"])
        if new_file is not None:
            view_box = load_file(new_file, view_box)

        if view_box.current_file is not None:
            st.download_button(
                label="Download current",
                data=view_box.current_file or "",
                file_name=view_box.filename,
                disabled=view_box.current_file is None,
                use_container_width=True
            )
            view_box = await load_colors(view_box)
            num_cols = 5
            new_colors = copy(view_box.colors)
            num_rows = num_cols + 1 - (len(view_box.colors) % num_cols)
            for i in range(num_rows):
                cols = st.columns(num_cols)
                for j, col in enumerate(cols):
                    current_idx = j + (i * (num_cols - 1))
                    val = view_box.colors[current_idx]
                    val = col.color_picker(label=val, value=val, key=f"color,{i},{j}")
                    if val:
                        new_colors[current_idx] = val

            if new_colors != view_box.colors:
                st.session_state["prev_view_box"] = copy(st.session_state["view_box"])
                for new_color, old_color in zip(new_colors, view_box.colors):
                    if new_color == old_color:
                        continue
                    current_file = cast(str, view_box.current_file)
                    log.info(f"Old color: '{old_color}' - New color: '{new_color}'")
                    new_file = copy(current_file.replace(old_color, new_color))
                view_box = view_box.copy(update=dict(colors=new_colors, current_file=new_file))
            st.markdown(view_box.current_file, unsafe_allow_html=True)

    with tab2:
        view_box = await console_view(view_box)

    st.session_state["view_box"] = view_box

if __name__ == "__main__":
    asyncio.run(main())
