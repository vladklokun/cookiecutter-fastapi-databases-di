"""Application services.

Consumer-facing objects that provide methods to satisfy use cases of the
clients. Only services should be exposed to external ports and adapters, like
REST, GraphQL or other APIs.
"""

import {{cookiecutter.service_name}}._models as mdl
import {{cookiecutter.service_name}}._repositories as repos


class HealthService:
    """A service health service.

    An example on how to write a service. In concrete services, delete this
    class.
    """

    def __init__(self, repo: repos.IHealthCheckRepository) -> None:
        """Create a healthcheck service.

        Args:
            repo: A repository for healthchecks.
        """
        self._repo = repo

    async def get_healthcheck(self) -> mdl.HealthCheck:
        """Get a healthcheck.

        Returns:
            The performed healthcheck.
        """
        return await self._repo.create()
