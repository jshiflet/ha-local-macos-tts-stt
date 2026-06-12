"""Config flow for STT Bridge."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_HOST,
    CONF_IGNORE_CERT_ERRORS,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USE_HTTPS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
)
from .helpers import aiohttp_ssl_kwargs, base_url_from_config

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_TOKEN): str,
        vol.Optional(CONF_USE_HTTPS, default=False): bool,
        vol.Optional(CONF_IGNORE_CERT_ERRORS, default=False): bool,
    }
)


def options_schema(config: dict[str, Any]) -> vol.Schema:
    """Return the options form schema."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_USE_HTTPS,
                default=config.get(CONF_USE_HTTPS, False),
            ): bool,
            vol.Optional(
                CONF_IGNORE_CERT_ERRORS,
                default=config.get(CONF_IGNORE_CERT_ERRORS, False),
            ): bool,
        }
    )


async def validate_input(hass, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    base_url = base_url_from_config(data)
    session = aiohttp_client.async_get_clientsession(hass)
    try:
        async with session.get(
            f"{base_url}/healthz", **aiohttp_ssl_kwargs(data)
        ) as resp:
            if resp.status == 200:
                return {"title": "STT Bridge"}
            return {"base": "cannot_connect"}
    except Exception:
        _LOGGER.exception("Could not connect to STT Bridge")
        return {"base": "cannot_connect"}


class STTBridgeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STT Bridge."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return STTBridgeOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            info, errors = await self._validate_and_create(user_input)
            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _validate_and_create(self, data):
        """Validate the user input and create the entry."""
        errors = {}
        info = await validate_input(self.hass, data)
        if "base" in info:
            errors["base"] = info["base"]

        return info, errors


class STTBridgeOptionsFlow(OptionsFlow):
    """Handle STT Bridge options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage STT Bridge options."""
        config = {**self._config_entry.data, **self._config_entry.options}
        errors = {}

        if user_input is not None:
            updated_config = {**config, **user_input}
            info = await validate_input(self.hass, updated_config)
            if "base" not in info:
                return self.async_create_entry(title="", data=user_input)
            errors["base"] = info["base"]

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema(config),
            errors=errors,
        )
