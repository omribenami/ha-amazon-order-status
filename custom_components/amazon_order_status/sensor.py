"""Amazon Orders sensors."""

import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from .coordinator import AmazonOrdersCoordinator
from homeassistant.util.dt import as_local

_LOGGER = logging.getLogger(__name__)

STATUSES = [
    "Ordered",
    "Shipped",
    "Out for delivery",
    "Delivered",
    "Cancelled",
]

STATUS_ICONS = {
    "Cancelled": "mdi:package-variant-closed-remove",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    """Set up Amazon Order Status sensors."""
    coordinator: AmazonOrdersCoordinator = hass.data["amazon_order_status"][entry.entry_id]

    sensors = [
        AmazonOrderStatusSensor(coordinator, status)
        for status in STATUSES
    ]
    sensors.append(AmazonOrdersLastUpdatedSensor(coordinator))

    async_add_entities(sensors)


class AmazonOrderStatusSensor(CoordinatorEntity, Entity):
    """Sensor representing Amazon orders in a specific status."""

    def __init__(self, coordinator: AmazonOrdersCoordinator, status: str):
        super().__init__(coordinator)
        self.status = status
        self._attr_unique_id = f"amazon_order_status_{status.lower().replace(' ', '_')}"
        self._attr_name = f"Amazon Orders {status}"
        self._attr_icon = STATUS_ICONS.get(status, "mdi:package-variant")

    @property
    def state(self) -> int:
        """Return number of orders in this status."""
        return len(self._orders_for_status())

    @property
    def extra_state_attributes(self):
        """Return order details for this status."""
        orders = self._orders_for_status()
        return {
            "order_count": len(orders),
            "orders": orders,
        }

    def _orders_for_status(self) -> list[dict]:
        """Return orders matching this sensor's status."""
        if not self.coordinator.data:
            return []

        return [
            {
                "order_id": data.get("order_id"),
                "subject": data.get("subject"),
                "updated": data.get("updated"),
                "tracking_url": data.get("tracking_url"),
            }
            for data in self.coordinator.data
            if data.get("status") == self.status
        ]


class AmazonOrdersLastUpdatedSensor(CoordinatorEntity, Entity):
    """Sensor showing when Amazon orders were last updated."""

    def __init__(self, coordinator: AmazonOrdersCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = "amazon_order_status_last_updated"
        self._attr_name = "Amazon Orders Last Updated"
        self._attr_icon = "mdi:clock-check-outline"

    @property
    def state(self):
        """Return ISO timestamp of last successful update."""
        if not getattr(self.coordinator, "last_check", None):
            return None
        return self.coordinator.last_check.isoformat()
