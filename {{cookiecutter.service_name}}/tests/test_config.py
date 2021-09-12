"""Tests for the configuration module."""
import collections.abc as col_abc
import pathlib
import typing as t

import pydantic as pyd
import pytest
import yaml

import {{cookiecutter.service_name}}.config as svc_cfg

APPLICATION_ENVIRONMENT_ENV_VAR_NAME: t.Final[str] = "APPLICATION_ENV"
APP_ENVIRONMENTS: t.Final[list[str]] = ["dev", "test", "staging", "production"]
DSNS: t.Final[list[str]] = [
    "postgres://user:password@localhost:5432/svar_service_achievements_dev"
]


def _render_config_file_name(environment_name: str) -> str:
    """Return the rendered config filename.

    Args:
        environment_name: The name of the environment in which the
            application is running.

    Returns:
        The rendered filename of the config that matches the environment.
    """
    return f"{environment_name}.yaml"


class IMakeTmpConfigFile(t.Protocol):
    """Interface for temporary configuration file maker.

    Used to annotate a fixture.
    """

    def __call__(self, filename: str, contents: col_abc.Mapping) -> pathlib.Path:
        """Create a temporary configuration file and return its name.

        Args:
            filename: Name of the config file to create.
            contents: The contents of the config file to create.

        Returns:  # noqa: DAR202, callback protocols dont provide implementation
            The path to the created file.
        """
        ...


@pytest.fixture
def make_tmp_config_file(
    tmp_path: pathlib.Path,
) -> t.Generator[IMakeTmpConfigFile, None, None]:
    """Yield callable that creates a temporary config file.

    The file is deleted on cleanup.

    Args:
        tmp_path: A temporary path where the config will be created.

    Yields:
        A callable that creates a temporary config file.
    """
    created_files: list[pathlib.Path] = []

    def create_config_file(
        filename: str,
        contents: col_abc.Mapping[str, t.Any],
        *,
        created_files: list[pathlib.Path] = created_files,
    ) -> pathlib.Path:
        file_path = tmp_path / filename
        with open(file_path, "w") as file:
            yaml.dump(contents, file)

        created_files.append(file_path)

        return file_path

    yield create_config_file

    # Remove created files
    for f in created_files:
        f.unlink()


@pytest.fixture(params=APP_ENVIRONMENTS)
def application_environment_name(request: pytest.FixtureRequest) -> str:
    """Return the name of the environment in which the application is running.

    Args:
        request: The current fixture usage request.

    Returns:
        The name of the environment in which the application is running.
    """
    # Pytest cannot hint that the FixtureRequest will have a param
    return request.param  # type: ignore[attr-defined]


@pytest.fixture(params=DSNS)
def dsn(request: pytest.FixtureRequest) -> str:
    """Return a data source name.

    Args:
        request: The current fixture usage request.

    Returns:
        A data source name.
    """
    # Pytest cannot hint that the FixtureRequest will have a param
    return request.param  # type: ignore[attr-defined]


@pytest.fixture
def valid_config_mapping(
    application_environment_name: str, dsn: str
) -> col_abc.Mapping:
    """Return a valid configuration mapping.

    Args:
        application_environment_name: The name of the environment in which the
            application will run.
        dsn: The data source name.

    Returns:
        A configuration mapping that matches a mapping from a valid config
        object.
    """
    cfg = {
        "name": application_environment_name,
        "database_dsn": dsn,
    }
    return cfg


class TestConfig:
    """Tests for the config class."""

    @pytest.fixture(autouse=True)
    def unset_application_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ensure that the application environment env variable is cleared in
        the config test suite.

        Args:
            monkeypatch: The monkeypatcher.
        """
        monkeypatch.delenv("APPLICATION_ENV", raising=False)

    def test_valid_config_mapping_creates_config_successfully(
        self, valid_config_mapping: col_abc.Mapping
    ) -> None:
        """For a valid configuration mapping, the object should be created
        successfully.

        Given:
            - A configuration mapping.
            - And the mapping has all the neccessary fields.
        When:
            - Initializing a config with the mapping.
        Then:
            - The config object should be created successfully.
            - And the config object should match the mapping.

        Args:
            valid_config_mapping: a valid config mapping.
        """
        config = svc_cfg.Config(**valid_config_mapping)
        assert config.dict() == valid_config_mapping

    def test_loaded_yaml_app_configs_by_kwargs_creates_object_successfully(
        self, app_config_path: pathlib.Path
    ) -> None:
        """For mappings created from valid application configs, the object
        should be created successfully.

        Given:
            - A valid application configuration file.
        When:
            - Creating a config from a mapping made from the config file.
        Then:
            - The object is successfully created.

        Args:
            app_config_path: path to a valid application config.
        """
        with open(app_config_path) as config_file:
            config_mapping = yaml.safe_load(config_file)

        config = svc_cfg.Config(**config_mapping)
        assert config

    def test_valid_config_with_unknown_field_raises_validation_error(
        self, valid_config_mapping: col_abc.Mapping
    ) -> None:
        """For a valid config mapping that contains an unknown field, the
        constructor should raise a validation error.

        Given:
            - A valid configuration mapping that contains an unknown field.
        When:
            - Attempting to initialize the object.
        Then:
            - The constructor should raise a validation error.

        Args:
            valid_config_mapping: a valid configuration mapping.
        """
        unknown_field = {"unknown_field_to_a_config": "some_value"}
        config_with_unknown_field = valid_config_mapping | unknown_field

        with pytest.raises(pyd.ValidationError):
            _ = svc_cfg.Config(**config_with_unknown_field)

    def test_env_var_set_should_load_config_from_matching_yaml(
        self,
        monkeypatch: pytest.MonkeyPatch,
        application_environment_name: str,
        make_tmp_config_file: IMakeTmpConfigFile,
        valid_config_mapping: col_abc.Mapping[str, t.Any],
    ) -> None:
        """Should load a config from matching YAML file.

        Args:
            monkeypatch: The monkeypatcher.
            application_environment_name: The name of the environment the
                application is running in.
            make_tmp_config_file: A callable that makes temporary config files.
            valid_config_mapping: A valid config mapping — config file
                contents.

        Given:
            - An application environment env var is set.
            - And the YAML config for the environment exists in the expected
              directory.
        When:
            - Instantiating the Config object with no params.
        Then:
            - The config object's contents match the contents of the YAML file.
        """
        monkeypatch.setenv(
            APPLICATION_ENVIRONMENT_ENV_VAR_NAME, application_environment_name
        )

        tmp_config_filename = _render_config_file_name(application_environment_name)
        tmp_config_contents = valid_config_mapping
        tmp_config_path = make_tmp_config_file(tmp_config_filename, tmp_config_contents)

        # Monkeypatch the config object to use temporary configs dir
        monkeypatch.setattr(
            svc_cfg.Config.__config__, "configs_dir", tmp_config_path.parent
        )
        config = svc_cfg.Config()

        assert config.dict() == tmp_config_contents
