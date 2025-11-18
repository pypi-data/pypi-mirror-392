from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class ProjectConfig(BaseSettings):
    name: str
    version: str = "0.1.0"
    description: str = ""
    authors: list[str] = []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "poetry"), extra="ignore"
    )

    @property
    def title(self) -> str:
        return self.name.replace("-", " ").title()


class ProjectConfig2(BaseSettings):
    name: str
    version: str = "0.1.0"
    description: str = ""
    authors: list[dict] = []

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("project",), extra="ignore"
    )

    @property
    def title(self) -> str:
        return self.name.replace("-", " ").title()
