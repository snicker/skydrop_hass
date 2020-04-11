"""Entity to represent a Skydrop device component."""

from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import Entity

from .const import DEFAULT_NAME, DOMAIN


class SkydropDevice(Entity):
    """Base class for Skydrop devices."""

    def __init__(self, controller):
        """Initialize a Skydrop device."""
        super().__init__()
        self._controller = controller
        self._attributes = {}

    @property
    def should_poll(self) -> bool:
        """Declare that this entity pushes its state to HA."""
        return False

    @property
    def device_state_attributes(self):
        return self._attributes

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._controller.id,)},
            "name": self._controller.name,
            "manufacturer": DEFAULT_NAME,
        }