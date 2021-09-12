"""Handlers for the FastAPI events."""
import databases
import dependency_injector.wiring as di_wiring

import {{cookiecutter.service_name}}._containers as svc_containers


@di_wiring.inject
async def connect_database(
    db: databases.Database = di_wiring.Provide[svc_containers.Container.db],
) -> None:
    """Connect to the database instance, given the `db` object.

    Args:
        db: The database object that abstracts the database connection.
    """
    await db.connect()


@di_wiring.inject
async def disconnect_database(
    db: databases.Database = di_wiring.Provide[svc_containers.Container.db],
) -> None:
    """Disconnect from the database instance, given the `db` object.

    Args:
        db: The database object that abstracts the database connection.
    """
    await db.disconnect()
