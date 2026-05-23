"""Watchtower runtime settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from watchtower.config import PACKAGE_ROOT, PROJECT_ROOT

WatchtowerMode = Literal["learn", "run", "hybrid"]


class WatchtowerSettings(BaseSettings):
    """Application settings loaded from defaults, config file, and environment."""

    model_config = SettingsConfigDict(
        env_prefix="WATCHTOWER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_path: Path = Field(
        default=PROJECT_ROOT / "data" / "watchtower.db",
        description="SQLite database file path",
    )
    config_file: Path | None = Field(
        default=None,
        description="Optional YAML config file path",
    )
    default_tenant_slug: str = Field(default="default")
    default_mode: WatchtowerMode = Field(default="learn")
    audit_log_enabled: bool = Field(default=True)

    @property
    def migrations_dir(self) -> Path:
        return PACKAGE_ROOT / "storage" / "migrations" / "versions"


DEFAULT_SETTINGS = WatchtowerSettings()
