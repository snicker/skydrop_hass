"""Adds config flow for Skydrop."""
from collections import OrderedDict

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_CLIENT_KEY,
    CONF_CLIENT_SECRET
)

@config_entries.HANDLERS.register(DOMAIN)
class SkydropFlowHandler(config_entries.ConfigFlow):
    """Config flow for Skydrop."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._title = ""

    async def async_step_user(
        self, user_input=None
    ):  # pylint: disable=dangerous-default-value
        """Handle a flow initialized by the user."""
        self._errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")
        if user_input is not None:
            if user_input[CONF_CLIENT_KEY] and user_input[CONF_CLIENT_SECRET]:
                return self.async_create_entry(title=self._title, data=user_input)
            return await self._show_config_form(user_input)
        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to enter API keys."""

        # Defaults
        client_key = ""
        client_secret = ""

        if user_input is not None:
            if CONF_CLIENT_KEY in user_input:
                client_key = user_input[CONF_CLIENT_KEY]
            if CONF_CLIENT_SECRET in user_input:
                client_secret = user_input[CONF_CLIENT_SECRET]

        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_CLIENT_KEY, default=client_key)] = str
        data_schema[vol.Required(CONF_CLIENT_SECRET, default=client_secret)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):
        """Handle import."""
        self._title = "configuration.yaml"
        return await self.async_step_user(user_input)
