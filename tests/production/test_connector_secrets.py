"""Connector secret masking in audit and onboarding preview."""

from __future__ import annotations

from watchtower.security.masking import mask_mapping
from watchtower.sources.onboarding import SourceOnboardingService


def test_connector_config_secrets_masked():
    config = {
        "api_url": "https://wazuh:55000",
        "token": "wazuh-token-secret",
        "password": "pw",
        "ca_cert_path": "/etc/ssl/ca.pem",
    }
    masked = mask_mapping(config)
    preview = SourceOnboardingService.config_preview(config)
    assert "wazuh-token-secret" not in preview
    assert masked["token"] == "***REDACTED***"
    assert masked["password"] == "***REDACTED***"
