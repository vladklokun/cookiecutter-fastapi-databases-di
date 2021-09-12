"""Dependency injection containers."""
import databases
import dependency_injector.containers as di_containers
import dependency_injector.providers as di_providers

import {{cookiecutter.service_name}}._repositories as repos
import {{cookiecutter.service_name}}._services as svc


class Container(di_containers.DeclarativeContainer):
    """A dependency injection container.

    Stores dependencies for consumers.
    """

    config = di_providers.Configuration()

    db = di_providers.Singleton(databases.Database, config.database_dsn)
    healthcheck_repo = di_providers.Factory(repos.HealthCheckRepository, db=db)
    healthcheck_svc = di_providers.Factory(svc.HealthService, repo=healthcheck_repo)
