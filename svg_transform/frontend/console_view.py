import asyncio
import queue

import streamlit as st
from pydantic import validate_call, ConfigDict


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
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
