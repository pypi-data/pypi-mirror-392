# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .task import Task
from .._models import BaseModel

__all__ = ["TaskListResponse", "TaskListResponseTag"]


class TaskListResponseTag(BaseModel):
    id: str
    """Unique identifier of the tag"""

    color: str
    """Hex color code for the tag"""

    name: str
    """Name of the tag"""


class TaskListResponse(Task):
    tags: List[TaskListResponseTag]
