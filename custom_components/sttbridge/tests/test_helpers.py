"""Test STT Bridge connection helpers."""

from custom_components.sttbridge.const import (
    CONF_HOST,
    CONF_IGNORE_CERT_ERRORS,
    CONF_PORT,
    CONF_USE_HTTPS,
)
from custom_components.sttbridge.helpers import (
    aiohttp_ssl_kwargs,
    base_url_from_config,
    websocket_url_from_config,
)

MOCK_CONFIG = {
    CONF_HOST: "1.2.3.4",
    CONF_PORT: 8787,
}


def test_urls_default_to_plain_http() -> None:
    """Test plain HTTP and WebSocket URLs."""
    assert base_url_from_config(MOCK_CONFIG) == "http://1.2.3.4:8787"
    assert websocket_url_from_config(MOCK_CONFIG) == "ws://1.2.3.4:8787/stt/stream"
    assert aiohttp_ssl_kwargs(MOCK_CONFIG) == {}


def test_urls_use_https_when_enabled() -> None:
    """Test secure HTTP and WebSocket URLs."""
    config = {
        **MOCK_CONFIG,
        CONF_USE_HTTPS: True,
    }

    assert base_url_from_config(config) == "https://1.2.3.4:8787"
    assert websocket_url_from_config(config) == "wss://1.2.3.4:8787/stt/stream"
    assert aiohttp_ssl_kwargs(config) == {}


def test_https_can_ignore_certificate_errors() -> None:
    """Test disabling SSL verification for HTTPS."""
    config = {
        **MOCK_CONFIG,
        CONF_USE_HTTPS: True,
        CONF_IGNORE_CERT_ERRORS: True,
    }

    assert aiohttp_ssl_kwargs(config) == {"ssl": False}
