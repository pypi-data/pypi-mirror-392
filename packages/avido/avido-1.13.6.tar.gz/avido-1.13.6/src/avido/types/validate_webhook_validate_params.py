# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ValidateWebhookValidateParams", "Body"]


class ValidateWebhookValidateParams(TypedDict, total=False):
    body: Required[Body]
    """Payload sent to the configured webhook whenever a task test is triggered."""

    signature: Required[str]
    """HMAC signature for the request body."""

    timestamp: Required[int]
    """Timestamp (in milliseconds) for the request."""


class Body(TypedDict, total=False):
    prompt: Required[Union[str, Dict[str, object]]]
    """The user prompt that triggered the test run."""

    test_id: Required[Annotated[str, PropertyInfo(alias="testId")]]
    """The unique identifier for the test run."""

    metadata: Dict[str, object]
    """Metadata from the originating task. Only included when metadata is available."""
