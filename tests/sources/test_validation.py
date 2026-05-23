"""Source onboarding config validation."""

from __future__ import annotations

import pytest

from watchtower.sources.onboarding import SourceOnboardingService
from watchtower.sources.validation import validate_connector_config


def test_invalid_file_jsonl_rejected():
    with pytest.raises(ValueError, match="file_path"):
        validate_connector_config("file_jsonl", {})


def test_invalid_elasticsearch_rejected():
    with pytest.raises(ValueError, match="base_url"):
        validate_connector_config("elasticsearch", {"base_url": "not-a-url"})


def test_invalid_wazuh_missing_auth():
    with pytest.raises(ValueError, match="token or username"):
        validate_connector_config(
            "wazuh",
            {"api_url": "https://wazuh.corp:55000"},
        )


def test_onboarding_register_rejects_invalid_config(app, tenant_id):
    with app.session() as session:
        onboard = SourceOnboardingService(session.sources)
        with pytest.raises(ValueError):
            onboard.register(tenant_id, "file_jsonl", "bad", {})
