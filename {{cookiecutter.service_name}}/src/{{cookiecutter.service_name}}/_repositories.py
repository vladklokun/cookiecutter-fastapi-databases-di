"""Repositores.

Repositories interact with the data access layer.
"""
import collections.abc as col_abc
import typing as t

import databases

import {{cookiecutter.service_name}}._models as mdl
import {{cookiecutter.service_name}}._tables as tbl


class IHealthCheckRepository(t.Protocol):
    """A protocol for healthcheck repositories."""

    async def create(self) -> mdl.HealthCheck:
        """Create the healthcheck."""


class HealthCheckRepository:
    """A concreate healthcheck repository.

    Uses an RDBMS as a storage engine.
    """

    def __init__(self, db: databases.Database, *, table=tbl.healthchecks) -> None:
        """Create a healthcheck repository.

        Args:
            db: The database the repo will interact with.
            table: The SQL table that defines the healthcheck data.
        """
        self._db = db
        self._table = table

    async def create(self) -> mdl.HealthCheck:
        """Create the healthcheck.

        Returns:
            The created healthcheck.
        """
        insert_query = self._table.insert().values(status="ok").returning(self._table)
        created_healthcheck = await self._db.fetch_one(insert_query)

        # After a successful insert, the row is guaranteed to exist
        created_healthcheck = t.cast(col_abc.Mapping[str, t.Any], created_healthcheck)

        return mdl.HealthCheck(**created_healthcheck)
