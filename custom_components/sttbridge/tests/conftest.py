"""Common fixtures for the STT Bridge tests."""
from collections.abc import Generator
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.sttbridge.const import (
    CONF_HOST,
    CONF_IGNORE_CERT_ERRORS,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USE_HTTPS,
    DOMAIN,
)

MOCK_CONFIG = {
    CONF_HOST: "1.2.3.4",
    CONF_PORT: 8787,
    CONF_TOKEN: "test-token",
    CONF_USE_HTTPS: False,
    CONF_IGNORE_CERT_ERRORS: False,
}

@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Mock a config entry."""
    return ConfigEntry(
        version=1,
        domain=DOMAIN,
        title="STT Bridge",
        data=MOCK_CONFIG,
        source="user",
    )

@pytest.fixture
def mock_setup_entry() -> Generator[None, None, None]:
    """Mock setting up a config entry."""
    with patch(
        "custom_components.sttbridge.async_setup_entry", return_value=True
    ) as mock_setup:
        yield mock_setup
