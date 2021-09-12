"""Response schemas.

Data transfer objects that would be sent via external adapters, like APIs.
"""
import typing as t

import pydantic as pyd


class HealthCheckDTO(pyd.BaseModel):
    """A DTO for healthchecks."""

    id: pyd.UUID4
    status: t.Literal["ok"]
