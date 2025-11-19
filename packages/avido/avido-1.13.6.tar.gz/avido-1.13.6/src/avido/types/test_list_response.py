# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .task import Task
from .test import Test

__all__ = ["TestListResponse"]


class TestListResponse(Test):
    __test__ = False
    task: Task
    """
    A task that represents a specific job-to-be-done by the LLM in the user
    application.
    """
