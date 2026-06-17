"""The STT Bridge integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_TOKEN, DOMAIN
from .helpers import aiohttp_ssl_kwargs, base_url_from_config, config_from_entry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.TTS, Platform.STT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up STT Bridge from a config entry."""
    config_data = config_from_entry(entry)
    
    session = async_get_clientsession(hass)
    base_url = base_url_from_config(config_data)
    ssl_kwargs = aiohttp_ssl_kwargs(config_data)
    token = config_data.get(CONF_TOKEN)

    async def async_update_data():
        """Fetch languages and voices from STT Bridge."""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            async with session.get(f"{base_url}/languages", headers=headers, **ssl_kwargs) as resp:
                resp.raise_for_status()
                languages = await resp.json()
            
            async with session.get(f"{base_url}/voices", headers=headers, **ssl_kwargs) as resp:
                resp.raise_for_status()
                voices_data = await resp.json()
                
            return {
                "languages": languages,
                "voices": voices_data
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sttbridge_languages",
        update_method=async_update_data,
        update_interval=timedelta(hours=1),
    )

    await coordinator.async_config_entry_first_refresh()
    config_data["coordinator"] = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = config_data
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
