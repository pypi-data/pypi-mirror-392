import os
from datetime import timedelta

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class AppConfig(BaseModel):
    host: str
    port: int
    workers: int
    use_telemetry: bool = True


class OtelConfig(BaseModel):
    agent_url: str


class KongJsonConfig(BaseModel):
    pass


class StateConfig(BaseModel):
    ttl: timedelta


class ExtensionConfig(BaseModel):
    config: KongJsonConfig
    state: StateConfig


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


class SdkConfig(BaseSettings):
    app: AppConfig
    otel: OtelConfig
    extension: ExtensionConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KONG_SDK_",
        json_file=CONFIG_PATH,
        env_nested_delimiter="__",
        json_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


config = SdkConfig()
