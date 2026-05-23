"""Watchtower runtime settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from watchtower.config.paths import PACKAGE_ROOT, PROJECT_ROOT

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
    server_stack_logs_root: Path = Field(
        default=PROJECT_ROOT / "server-stack" / "logs",
        description="Default server-stack logs directory for ingestion",
    )
    ingest_default_limit: int = Field(default=500, ge=1, le=10_000)
    elasticsearch_url: str | None = Field(default=None)
    wazuh_api_url: str | None = Field(default=None)
    baseline_learning_window_days: int = Field(default=45, ge=1, le=365)
    baseline_min_user_samples: int = Field(default=5, ge=1)
    baseline_run_transition_confidence_threshold: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
    )
    llm_provider_chain: str = Field(
        default="openai,anthropic,gemini,ollama,custom_openai_compatible",
        description="Comma-separated provider fallback order",
    )
    llm_max_retries: int = Field(default=2, ge=0, le=2)
    openai_api_key: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    gemini_api_key: str | None = Field(default=None)
    gemini_model: str = Field(default="gemini-2.0-flash")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434/v1")
    ollama_model: str = Field(default="llama3.2")
    custom_openai_base_url: str | None = Field(default=None)
    custom_openai_api_key: str | None = Field(default=None)
    custom_openai_model: str = Field(default="default")
    llm_test_provider: str | None = Field(default=None)

    @property
    def migrations_dir(self) -> Path:
        return PACKAGE_ROOT / "storage" / "migrations" / "versions"


DEFAULT_SETTINGS = WatchtowerSettings()
