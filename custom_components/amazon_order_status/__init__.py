"""Amazon Order Status integration."""

import logging
from datetime import timedelta
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_DAYS,
    ATTR_ORDER_ID,
    DOMAIN,
    SERVICE_PURGE_ORDER,
    SERVICE_RESCAN,
)
from .coordinator import AmazonOrdersCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]
DEFAULT_UPDATE_INTERVAL = 5  # minutes
DEFAULT_RESCAN_DAYS = 14

PURGE_ORDER_SCHEMA = vol.Schema(
    {vol.Optional(ATTR_ORDER_ID, default=""): cv.string}
)

RESCAN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_DAYS, default=DEFAULT_RESCAN_DAYS): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=90)
        )
    }
)


async def _handle_purge_order(hass: HomeAssistant, call: ServiceCall) -> None:
    """Remove a specific order from tracking."""
    order_id = (call.data.get(ATTR_ORDER_ID) or "").strip()
    if not order_id:
        _LOGGER.warning(
            "purge_order called with empty order_id. "
            "If using a dashboard button, call script.purge_amazon_order instead so the order ID is read when you tap."
        )
        return
    domain_data = hass.data.get(DOMAIN) or {}
    removed = False
    for key, value in domain_data.items():
        if isinstance(value, AmazonOrdersCoordinator):
            if await value.async_purge_order(order_id):
                removed = True
    if not removed:
        _LOGGER.warning("Order %s not found or already purged", order_id)


def _make_purge_order_handler(hass: HomeAssistant):
    """Return an async service handler that closes over hass."""

    async def handler(call: ServiceCall) -> None:
        await _handle_purge_order(hass, call)

    return handler


async def _handle_rescan(hass: HomeAssistant, call: ServiceCall) -> None:
    """Re-parse recent Amazon email, ignoring the stored last-check timestamp."""
    days = call.data.get(ATTR_DAYS, DEFAULT_RESCAN_DAYS)
    domain_data = hass.data.get(DOMAIN) or {}
    seen: set[int] = set()
    for value in domain_data.values():
        if isinstance(value, AmazonOrdersCoordinator) and id(value) not in seen:
            seen.add(id(value))
            await value.async_rescan(days)


def _make_rescan_handler(hass: HomeAssistant):
    """Return an async service handler that closes over hass."""

    async def handler(call: ServiceCall) -> None:
        await _handle_rescan(hass, call)

    return handler


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amazon Order Status from a config entry."""
    # Create the coordinator
    coordinator = AmazonOrdersCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Ensure DOMAIN dict exists
    hass.data.setdefault(DOMAIN, {})

    # Store coordinator under a fixed key for options_flow
    hass.data[DOMAIN]["coordinator"] = coordinator

    # Also store by entry_id for platform setup
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register services (idempotent if multiple entries)
    if not hass.services.has_service(DOMAIN, SERVICE_PURGE_ORDER):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PURGE_ORDER,
            _make_purge_order_handler(hass),
            schema=PURGE_ORDER_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RESCAN):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESCAN,
            _make_rescan_handler(hass),
            schema=RESCAN_SCHEMA,
        )

    # Forward entry setups (sensors)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove coordinator references
    if DOMAIN in hass.data:
        if "coordinator" in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop("coordinator")
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

    return True
