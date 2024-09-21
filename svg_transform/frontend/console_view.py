import asyncio
import queue
from typing import List

import streamlit as st
from pydantic import validate_call, ConfigDict

from svg_transform.backend.data_structure import ViewBox


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
async def console_view(view_box: ViewBox) -> ViewBox:
    msgs = view_box.msgs.copy()
    while True:
        try:
            await asyncio.sleep(0.15)
            msg = view_box.st_queue.get_nowait()
            msgs.append(msg)
        except queue.Empty:
            st.code("\n".join(msgs), language="log")
            return view_box.model_copy(update=dict(msgs=msgs))
