"""Read-only event source connectors."""

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.factory import build_connector
from watchtower.connectors.mock import MockConnector

__all__ = [
    "BaseConnector",
    "ConnectorError",
    "MockConnector",
    "build_connector",
]
