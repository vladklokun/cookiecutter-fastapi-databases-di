"""Global fixtures available for all tests in the project."""

import collections.abc as col_abc
import pathlib
import typing as t

import databases
import fastapi.testclient as fa_tc
import pytest

import {{cookiecutter.service_name}}.config as svc_cfg
import {{cookiecutter.service_name}}.main as svc_main


APP_CONFIGS_DIRECTORY_NAME: t.Final[str] = "configs"
APP_CONFIG_NAMES: t.Final[list[str]] = ["dev.yaml"]


def _get_test_database(config: svc_cfg.Config) -> databases.Database:
    """Return a specially configured test database instance.

    A test database isolates operations on itself between test runs by rolling
    back all applied operations on disconnect.

    Args:
        config: The application configuration object.

    Returns:
        A database object that represents a database to run tests against.
    """
    database_uri = config.database_dsn
    return databases.Database(database_uri, force_rollback=True)


@pytest.fixture
def test_client() -> col_abc.Generator[fa_tc.TestClient, None, None]:
    """Return a test client.

    Yields:
        A test client.
    """
    app = svc_main._create_app()
    app_config = svc_cfg.Config()

    # Tests should use a specially configured database instance
    test_database = _get_test_database(app_config)
    with app.container.db.override(test_database):
        with fa_tc.TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def app_configs_path() -> pathlib.Path:
    """Return a path to application configs.

    Returns:
        A path to a directory that stores valid application configs.
    """
    current_file = pathlib.Path(__name__)
    current_dir = current_file.parent

    # Configs are stored at the same level as the tests directory
    config_dir = current_dir.parent / APP_CONFIGS_DIRECTORY_NAME
    return config_dir


@pytest.fixture(params=APP_CONFIG_NAMES)
def app_config_path(request: t.Any, app_configs_path: pathlib.Path) -> pathlib.Path:
    """Return a path to a real application config.

    Args:
        request: a `pytest` request.
        app_configs_path: path to a directory that stores application configs.

    Returns:
        A path to a single valid application config used for some environment
        (dev, test, prod etc).
    """
    config_file_name = request.param
    return app_configs_path / config_file_name
