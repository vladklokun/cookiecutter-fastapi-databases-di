"""Application configuration."""
import os
import pathlib
import typing as t

import pydantic as pyd
import yaml

CURRENT_DIR: t.Final = pathlib.Path.cwd()
CONFIGS_DIR_NAME: t.Final[str] = "configs"
DEFAULT_CONFIGS_DIR = CURRENT_DIR / CONFIGS_DIR_NAME
DEFAULT_APPLICATION_ENV_VAR_NAME: t.Final[str] = "APPLICATION_ENV"


class AppEnvironmentNotSetError(KeyError):
    """An application environment error was not set."""


def _get_app_environment() -> str:
    """Return the name of the environment in which the application is running.

    Returns:
        The name of the environment in which the application is running.

    Raises:
        AppEnvironmentNotSetError: if the environment variable that holds the
            name of application's current environment is not set.
    """
    try:
        return os.environ[DEFAULT_APPLICATION_ENV_VAR_NAME]
    except KeyError:
        raise AppEnvironmentNotSetError


def _render_app_config_filename(app_environment_name: str) -> str:
    """Return a name of the app configuration file based on the environment.

    Returns:
        The filename of the application configuration that should be used in
        the environment, in which the application is running.

    Args:
        app_environment_name: Name of the environment in which the application
            runs.
    """
    return f"{app_environment_name}.yaml"


def env_aware_yaml_configuration_settings_source(
    settings: pyd.BaseSettings,
) -> dict[str, t.Any]:
    """A source for the environment-aware YAML config file.

    Args:
        settings: The settings for which the config file will be read.

    Returns:
        The contents of the matching configuration file.
    """
    try:
        application_environment_name = _get_app_environment()
    except AppEnvironmentNotSetError:
        # When the name of an application's environment is not set, configs
        # cannot be loaded from appropriate YAML files
        return {}

    # The __config__ attribute is dynamically set on the model config class, so
    # the type annotations should be ignored
    config_file_dir: pathlib.Path = settings.__config__.configs_dir  # type: ignore

    config_file_name = _render_app_config_filename(application_environment_name)
    config_path = config_file_dir / config_file_name

    with open(config_path) as config_fp:
        config_contents = yaml.safe_load(config_fp)
    return config_contents


class Config(pyd.BaseSettings):
    """Application configuration."""

    name: str
    database_dsn: pyd.PostgresDsn

    class Config:
        """Configuration for the config Pydantic model."""

        configs_dir = DEFAULT_CONFIGS_DIR

        # To prevent accidental misspellings and potentially unused fields,
        # forbid fields that are not defined in the schema
        extra = pyd.Extra.forbid

        @classmethod
        def customise_sources(
            cls,
            init_settings: t.Callable,
            env_settings: t.Callable,
            file_secret_settings: t.Callable,
        ) -> tuple[t.Callable, ...]:
            """Customise config sources for the config object.

            Args:
                init_settings: Settings from the init method.
                env_settings: Settings from the environment.
                file_secret_settings: Settings from file secrets.

            Returns:
                A tuple of all found settings.
            """
            return (
                init_settings,
                env_settings,
                env_aware_yaml_configuration_settings_source,
                file_secret_settings,
            )
