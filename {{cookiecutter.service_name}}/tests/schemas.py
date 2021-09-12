"""Schemas for objects used in tests."""

import pydantic as pyd


class CreateUserRequest(pyd.BaseModel):
    """A valid request to create a user."""

    username: str
    preferred_name: str
