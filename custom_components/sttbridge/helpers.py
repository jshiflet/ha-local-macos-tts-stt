"""Connection helpers for STT Bridge."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_HOST,
    CONF_IGNORE_CERT_ERRORS,
    CONF_PORT,
    CONF_USE_HTTPS,
)


def config_from_entry(entry: ConfigEntry) -> dict[str, Any]:
    """Return config entry data with options applied."""
    return {**entry.data, **entry.options}


def base_url_from_config(config: dict[str, Any]) -> str:
    """Return the HTTP(S) base URL for the bridge."""
    scheme = "https" if config.get(CONF_USE_HTTPS, False) else "http"
    return f"{scheme}://{config[CONF_HOST]}:{config[CONF_PORT]}"


def websocket_url_from_config(config: dict[str, Any]) -> str:
    """Return the WS(S) streaming URL for the bridge."""
    scheme = "wss" if config.get(CONF_USE_HTTPS, False) else "ws"
    return f"{scheme}://{config[CONF_HOST]}:{config[CONF_PORT]}/stt/stream"


def aiohttp_ssl(config: dict[str, Any]) -> bool | None:
    """Return per-request aiohttp SSL behavior for this bridge config."""
    if config.get(CONF_USE_HTTPS, False) and config.get(
        CONF_IGNORE_CERT_ERRORS, False
    ):
        return False
    return None


def aiohttp_ssl_kwargs(config: dict[str, Any]) -> dict[str, bool]:
    """Return aiohttp kwargs for requests that need custom SSL behavior."""
    ssl = aiohttp_ssl(config)
    return {"ssl": ssl} if ssl is not None else {}
