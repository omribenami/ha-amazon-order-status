"""Options flow for Amazon Order Status integration."""

from homeassistant import config_entries
import voluptuous as vol
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CANCELLED_RETENTION_DAYS,
    CONF_IMAP_FOLDER,
    DEFAULT_CANCELLED_RETENTION_DAYS,
    DOMAIN,
)


class AmazonOrderStatusOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Amazon Order Status."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the initial step of the options flow."""
        if user_input is not None:
            # Merge new options with existing ones
            new_options = dict(self._config_entry.options)
            new_options.update(user_input)

            # Update the config entry
            self.hass.config_entries.async_update_entry(
                self._config_entry, options=new_options
            )

            # Apply updates to the coordinator if it exists
            coordinator = self.hass.data.get(DOMAIN, {}).get("coordinator")
            if coordinator:
                if "delivered_retention_days" in user_input:
                    coordinator.async_set_retention_days(
                        user_input["delivered_retention_days"]
                    )
                if CONF_CANCELLED_RETENTION_DAYS in user_input:
                    coordinator.async_set_cancelled_retention_days(
                        user_input[CONF_CANCELLED_RETENTION_DAYS]
                    )
                if "update_interval" in user_input:
                    coordinator.async_update_interval(
                        user_input["update_interval"]
                    )
                if "mark_as_read" in user_input:
                    coordinator.async_set_mark_as_read(
                        user_input["mark_as_read"]
                    )
                if CONF_IMAP_FOLDER in user_input:
                    coordinator.async_set_imap_folder(
                        user_input[CONF_IMAP_FOLDER]
                    )

            return self.async_create_entry(title="", data=user_input)

        # Current options to use as defaults
        options = self._config_entry.options

        # Standard vol.Schema
        schema = vol.Schema(
            {
                vol.Required(
                    "delivered_retention_days",
                    default=options.get("delivered_retention_days", 30),
                ): cv.positive_int,
                vol.Required(
                    CONF_CANCELLED_RETENTION_DAYS,
                    default=options.get(
                        CONF_CANCELLED_RETENTION_DAYS,
                        DEFAULT_CANCELLED_RETENTION_DAYS,
                    ),
                ): cv.positive_int,
                vol.Required(
                    "update_interval",
                    default=options.get("update_interval", 5),
                ): cv.positive_int,
                vol.Required(
                    "mark_as_read",
                    default=options.get("mark_as_read", True),
                ): cv.boolean,
                vol.Optional(
                    CONF_IMAP_FOLDER,
                    default=options.get(CONF_IMAP_FOLDER, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
