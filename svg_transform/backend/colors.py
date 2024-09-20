import re
from typing import Set

from pydantic import validate_call

from backend.configs import validation_configs


@validate_call(config=validation_configs())
async def load_colors(file: str) -> Set[str]:
    found = re.findall(r"#\w{6}", file)
    unique_colors: Set[str] = set()
    for color in found:
        if color not in unique_colors and isinstance(color, str):
            unique_colors.add(color)
    return unique_colors
