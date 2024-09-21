import queue
from typing import Optional, Annotated, List, Set

from pydantic import Field, BaseModel

from svg_transform.backend.configs import validation_configs


class ViewBox(BaseModel):
    model_config = validation_configs()
    """
    Container for mutable (besides the queue) view variables
    """
    st_queue: queue.Queue
    filename: Optional[str] = None
    current_file: Optional[str] = None
    msgs: List[str] = list()
    colors: List[str] = list()
