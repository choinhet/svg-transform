import re
from typing import Set

from pydantic import validate_call

from svg_transform.backend.configs import validation_configs
from svg_transform.backend.data_structure import ViewBox


@validate_call(config=validation_configs())
async def load_colors(view_box: ViewBox) -> ViewBox:
    if not view_box.current_file:
        return view_box
    found = re.findall(r"#[A-F|\d]{6}", view_box.current_file)
    unique_colors: Set[str] = set()
    for color in found:
        if color not in unique_colors and isinstance(color, str):
            unique_colors.add(color)
    return view_box.copy(update=dict(colors=list(unique_colors)))
