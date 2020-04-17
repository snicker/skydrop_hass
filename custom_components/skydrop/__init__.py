"""
Component to integrate with Skydrop sprinkler controller
"""
import os
from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery, storage
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_call_later
from homeassistant.util import Throttle

import skydroppy

from .const import (
    CONF_BINARY_SENSOR,
    CONF_ENABLED,
    CONF_NAME,
    CONF_SENSOR,
    CONF_SWITCH,
    CONF_CLIENT_KEY,
    CONF_CLIENT_SECRET,
    DEFAULT_NAME,
    DOMAIN_DATA,
    DOMAIN_STORAGE,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    SIGNAL_SKYDROP_UPDATE,
    STARTUP_MESSAGE,
    SUPPORTED_DOMAINS,
    VERSION,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_CLIENT_KEY): cv.string,
                vol.Optional(CONF_CLIENT_SECRET): cv.string
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SCAN_INTERVAL = 30 #[todo] add this to configuration i guess


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Skydrop component from YAML."""

    conf = config.get(DOMAIN)
    hass.data.setdefault(DOMAIN_DATA, {})

    if not conf:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data=conf
        )
    )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    conf = hass.data.get(DOMAIN_DATA)
    if config_entry.source == config_entries.SOURCE_IMPORT:
        if conf is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
            return False

    _LOGGER.info(
        STARTUP_MESSAGE.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    config = config_entry.data

    skydrop_store = storage.Store(hass, VERSION, DOMAIN_STORAGE)

    tokens = await skydrop_store.async_load()

    hass.data[DOMAIN_DATA] = {
        "client": None, 
        "configurator": [],
        "storage": skydrop_store
    }

    client_key = config.get(CONF_CLIENT_KEY)
    client_secret = config.get(CONF_CLIENT_SECRET)

    client = skydroppy.SkydropClient(client_key, client_secret)
    if tokens:
        client.load_token_data(tokens)

    hass.data[DOMAIN_DATA]["client"] = SkydropData(hass, client)

    await test_login_status(hass, config_entry, setup_platform_callback)
    return True

async def test_login_status(hass, config_entry, setup_platform_callback):
    data_client = hass.data[DOMAIN_DATA]["client"]
    if data_client.are_tokens_good():
        await hass.async_add_job(setup_skydrop, hass, config_entry)
        return
    else:
        await hass.async_add_job(
            request_configuration, hass, config_entry, 
            setup_platform_callback
        )

async def request_configuration(hass, config_entry, setup_platform_callback):
    """Request configuration steps from the user using the configurator."""

    async def configuration_callback(callback_data):
        """Handle the submitted configuration."""
        await hass.async_add_job(
            setup_platform_callback, hass, config_entry, callback_data
        )
        
    configurator = hass.components.configurator

    data_client = hass.data[DOMAIN_DATA]["client"]
    config_id = None
    if not data_client.are_tokens_good():
        config_id = configurator.async_request_config(
            "Skydrop - Enter Grant Code",
            configuration_callback,
            description=(
                "Please enter your grant code from the Skydrop authentication flow."
            ),
            submit_caption="Save",
            fields=[{"id": "client_code", "name": "Client Code"}],
        )
    if config_id:
        hass.data[DOMAIN_DATA]["configurator"].append(config_id)
    if len(hass.data[DOMAIN_DATA]["configurator"]) > 1:
        configurator.async_request_done(
            (hass.data[DOMAIN_DATA]["configurator"]).pop(0)
        )

async def setup_platform_callback(hass, config_entry, callback_data):
    data_client = hass.data[DOMAIN_DATA]["client"]
    code = callback_data.get('client_code')
    success = await data_client.get_access_token(code)
    if success:
        await test_login_status(hass, config_entry, setup_platform_callback)
    else:
        await hass.async_add_job(
            request_configuration, hass, config_entry, 
            setup_platform_callback
        )

async def clear_configurator(hass):
    """Clear open configurators"""
    for config_id in hass.data[DOMAIN_DATA]["configurator"]:
        configurator = hass.components.configurator
        configurator.async_request_done(config_id)
    hass.data[DOMAIN_DATA]["configurator"] = []

async def setup_skydrop(hass, config_entry):
    data_client = hass.data[DOMAIN_DATA]["client"]

    await clear_configurator(hass)

    async def update_data(now):
        await data_client.update_data()
        dispatcher_send(hass, SIGNAL_SKYDROP_UPDATE)
        
        async_call_later(
            hass,
            SCAN_INTERVAL,
            update_data
        )

    await update_data(None)
    for component in SUPPORTED_DOMAINS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )


class SkydropData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, client):
        """Initialize the class."""
        self.hass = hass
        self.client = client

    def are_tokens_good(self):
        tokens = self.client._tokens
        if tokens.get('access') and tokens.get('refresh'):
            return True
        return False

    async def get_access_token(self, code):
        data_store = self.hass.data[DOMAIN_DATA]["storage"]
        try:
            result = await self.client.get_access_token(code)
            await data_store.async_save(self.client._tokens)
            return True
        except Exception as error:
            _LOGGER.error("Could not get Skydrop access token - %s", error)
        return False

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""
        try:
            if self.client.is_token_expired():
                await self.client.refresh_access_token()
                data_store = self.hass.data[DOMAIN_DATA]["storage"]
                await data_store.async_save(self.client._tokens)
            await self.client.update_controllers()
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Could not update data - %s", error)
