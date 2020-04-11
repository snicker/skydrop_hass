"""Integration with the Skydrop sprinkler system controller."""
from datetime import timedelta
import logging

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    SwitchDevice
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import generate_entity_id

from .const import (
    DOMAIN_DATA,
    SIGNAL_SKYDROP_UPDATE
)

from .entity import SkydropDevice

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Skydrop switches."""
    entities = await hass.async_add_executor_job(_create_entities, hass, config_entry)
    async_add_entities(entities)
    _LOGGER.info("%d Skydrop switch(es) added", len(entities))


def _create_entities(hass, config_entry):
    entities = []
    data_client = hass.data[DOMAIN_DATA]["client"]
    for controller in data_client.client._controllers:
        entities.append(SkydropControllerEnabledSwitch(controller, hass))
        for zone in controller.zones:
            if zone.status == 'wired':
                entities.append(SkydropZoneEnabledSwitch(controller, zone, hass))
                entities.append(SkydropZoneWateringSwitch(controller, zone, hass))
    _LOGGER.debug("Added %s", entities)
    return entities


class SkydropSwitch(SkydropDevice, SwitchDevice):
    """Represent a Skydrop device that can be toggled."""
    def __init__(self, controller, hass):
        super().__init__(controller)
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self.unique_id, hass=hass)

    @property
    def name(self) -> str:
        """Get a name for this switch."""
        return f"Switch on {self._controller.name}"

    @property
    def is_on(self) -> bool:
        """Return whether the switch is currently on."""
        return self._state

    @callback
    def _async_handle_update(self, *args, **kwargs) -> None:
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_SKYDROP_UPDATE, self._async_handle_update
            )
        )

class SkydropControllerEnabledSwitch(SkydropSwitch):
    def __init__(self, controller, hass):
        super().__init__(controller, hass)
        self._update_state(False)

    @property
    def name(self) -> str:
        return f"{self._controller.name} Controller Enabled"

    @property
    def unique_id(self) -> str:
        return f"skydrop_{self._controller.short_id}_enabled"
        
    @property
    def icon(self) -> str:
        """Return the icon to display."""
        return "mdi:water" if self.is_on else "mdi:water-off"

    def _update_state(self, write_state = True):
        self._state = self._controller.enabled
        self._attributes.update(self._controller._controller_data)
        if write_state:
            self.async_write_ha_state()

    @callback
    def _async_handle_update(self, *args, **kwargs) -> None:
        self._update_state()

    async def async_turn_on(self, **kwargs):
        await self._controller.enable()
        self._update_state()

    async def async_turn_off(self, **kwargs):
        await self._controller.disable()
        self._update_state()

class SkydropZoneEnabledSwitch(SkydropSwitch):
    def __init__(self, controller, zone, hass):
        self._zone = zone
        super().__init__(controller, hass)
        self._update_state(False)

    @property
    def name(self) -> str:
        return f"{self._zone.name} Enabled"

    @property
    def unique_id(self) -> str:
        return f"skydrop_{self._controller.short_id}_zone_{self._zone.id}_enabled"
        
    @property
    def icon(self) -> str:
        """Return the icon to display."""
        return "mdi:water" if self.is_on else "mdi:water-off"

    def _update_state(self, write_state = True):
        self._state = self._zone.enabled
        self._attributes.update(self._zone._zone_data)
        self._attributes.update(self._zone._zone_state)
        if write_state:
            self.async_write_ha_state()

    @callback
    def _async_handle_update(self, *args, **kwargs) -> None:
        self._update_state()

    async def async_turn_on(self, **kwargs):
        await self._zone.enable()
        self._update_state()

    async def async_turn_off(self, **kwargs):
        await self._zone.disable()
        self._update_state()

class SkydropZoneWateringSwitch(SkydropSwitch):
    def __init__(self, controller, zone, hass):
        self._zone = zone
        super().__init__(controller, hass)
        self._update_state(False)

    @property
    def name(self) -> str:
        return f"{self._zone.name} Watering"

    @property
    def unique_id(self) -> str:
        return f"skydrop_{self._controller.short_id}_zone_{self._zone.id}_watering"
        
    @property
    def icon(self) -> str:
        """Return the icon to display."""
        return "mdi:sprinkler"

    def _update_state(self, write_state = True):
        self._state = self._zone.watering
        self._attributes.update(self._zone._zone_data)
        self._attributes.update(self._zone._zone_state)
        if write_state:
            self.async_write_ha_state()

    @callback
    def _async_handle_update(self, *args, **kwargs) -> None:
        self._update_state()

    async def async_turn_on(self, **kwargs):
        await self._zone.start_watering()
        self._update_state()

    async def async_turn_off(self, **kwargs):
        await self._zone.stop_watering()
        self._update_state()
