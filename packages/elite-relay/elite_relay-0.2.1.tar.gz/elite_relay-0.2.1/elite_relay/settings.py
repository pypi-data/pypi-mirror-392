import logging
import re
import typing as t
from functools import cached_property, lru_cache
from pathlib import Path

from pydantic import BaseModel, DirectoryPath, computed_field, field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

__all__ = ['Settings', 'PluginConfig', 'EntryFilter']


class EntryFilter(BaseModel):
    key: str
    eq: str
    regex: bool = False

    @computed_field
    @cached_property
    def re_pattern(self) -> re.Pattern:
        return re.compile(self.eq)

    def compare(self, value: str) -> bool:
        if self.regex:
            return bool(self.re_pattern.search(value))
        return self.eq == value


class PluginConfig(BaseModel):
    plugin: str
    action: str
    filters: list[EntryFilter] = []
    options: dict
    enabled: bool = True

    def __str__(self):
        return f'{self.plugin}.{self.action}'

    @field_validator('plugin', 'action', mode='after')
    @classmethod
    def lower_strip(cls, value: str) -> str:
        return value.lower().strip()


class Settings(BaseSettings):
    # _last_update is not a Pydantic field
    _last_update: t.ClassVar[float] = 0.0

    logs_dir: DirectoryPath = (
        Path.home() / 'Saved Games' / 'Frontier Developments' / 'Elite Dangerous'
    )
    plugins: list[PluginConfig] = []
    event_interval: int | float = 0.5
    poll_interval: int | float = 1
    log_level: int = logging.INFO

    model_config = SettingsConfigDict(yaml_file=Path.home() / '.edr' / 'config.yaml')

    @field_validator('log_level', mode='before')
    @classmethod
    def validate_log_level(cls, value: t.Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return logging.getLevelNamesMapping()[value.upper().strip()]
            except KeyError:
                pass
        raise ValueError(f'Invalid log level "{value}"')

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        if not isinstance(yaml_file := cls.model_config.get('yaml_file'), Path):
            return super().settings_customise_sources(
                settings_cls,
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
        if not yaml_file.is_file():
            yaml_file.parent.mkdir(exist_ok=True)
            yaml_file.touch(exist_ok=True)
        return (YamlConfigSettingsSource(settings_cls),)

    @classmethod
    @lru_cache(maxsize=1)
    def _read(cls) -> "Settings":
        return cls()

    @classmethod
    def read(cls) -> "Settings":
        settings = cls._read()
        yaml_file = Settings.model_config.get('yaml_file')
        if not isinstance(yaml_file, (Path, str)):
            return settings
        if (st_mtime := Path(yaml_file).stat().st_mtime) != cls._last_update:
            settings.__init__()
            cls._last_update = st_mtime
        return settings
