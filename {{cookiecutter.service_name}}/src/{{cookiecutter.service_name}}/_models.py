"""Domain models.

Domain models contain business logic.
"""
import typing as t

import pydantic as pyd


class HealthCheck(pyd.BaseModel):
    """A health check."""

    id: pyd.UUID4
    status: t.Literal["ok"]
