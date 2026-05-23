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
    backup_dir: Path = Field(
        default=PROJECT_ROOT / "backups",
        description="Directory for SQLite backup files",
    )
    retention_raw_events_days: int = Field(default=90, ge=0, le=3650)
    retention_normalized_events_days: int = Field(default=180, ge=0, le=3650)
    retention_audit_days: int = Field(default=365, ge=0, le=3650)
    retention_llm_audit_days: int = Field(default=90, ge=0, le=3650)
    daemon_ingest_interval_seconds: int = Field(default=60, ge=5, le=3600)
    graph_checkpoint_enabled: bool = Field(
        default=True,
        description="Persist LangGraph checkpoints to SQLite (production default)",
    )
    graph_checkpoint_use_memory: bool = Field(
        default=False,
        description="Force in-process MemorySaver (tests/dev only)",
    )
    graph_checkpoint_path: Path = Field(
        default=PROJECT_ROOT / "data" / "graph_checkpoints.db",
        description="Separate SQLite file for LangGraph checkpoints",
    )
    graph_checkpoint_retention_days: int = Field(
        default=30,
        ge=0,
        le=3650,
        description="Days to keep checkpoint blobs for completed runs (0=disable prune)",
    )
    health_listen_host: str = Field(default="127.0.0.1")
    health_listen_port: int = Field(default=8080, ge=1, le=65535)

    @property
    def migrations_dir(self) -> Path:
        return PACKAGE_ROOT / "storage" / "migrations" / "versions"


DEFAULT_SETTINGS = WatchtowerSettings()
