"""An entry point to the application."""
import fastapi as fa

import {{cookiecutter.service_name}}._containers as svc_containers
import {{cookiecutter.service_name}}._endpoints as svc_endpoints
import {{cookiecutter.service_name}}._events as svc_events
import {{cookiecutter.service_name}}.config as svc_cfg


class Application(fa.FastAPI):
    """The web application object.

    Attributes:
        container: A dependency injection container.
    """

    container: svc_containers.Container


def _setup_container() -> svc_containers.Container:
    """Setup a dependency injection container.

    Returns:
        A ready to use dependency injection container.
    """
    container = svc_containers.Container()

    app_config = svc_cfg.Config()
    container.config.from_pydantic(app_config)

    container.wire(modules=[svc_endpoints, svc_events])

    return container


def _create_app() -> Application:
    """Create the application.

    Returns:
        The created FastAPI application.
    """
    container = _setup_container()

    app = Application(
        on_startup=[svc_events.connect_database],
        on_shutdown=[svc_events.disconnect_database],
    )
    app.container = container
    app.include_router(svc_endpoints.api_router)

    return app


app = _create_app()
