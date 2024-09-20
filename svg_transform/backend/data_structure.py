import queue
from typing import Optional, Annotated

from pydantic import Field, BaseModel

from backend.configs import validation_configs


class ViewBox(BaseModel):
    model_config = validation_configs(frozen=False)
    """
    Container for mutable (besides the queue) view variables
    """
    filename: str
    st_queue: Annotated[queue.Queue, Field(frozen=True)]
    current_file: Optional[str] = None
