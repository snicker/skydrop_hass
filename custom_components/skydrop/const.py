"""Constants for Skydrop."""
# Base component constants
DOMAIN = "skydrop"
DOMAIN_DATA = f"{DOMAIN}"
DOMAIN_STORAGE = f"{DOMAIN_DATA}_store"
VERSION = "1.0.3"
PLATFORMS = ["switch"]
REQUIRED_FILES = [
    "translations/en.json",
    "binary_sensor.py",
    "const.py",
    "config_flow.py",
    "manifest.json",
    "sensor.py",
    "switch.py",
]
ISSUE_URL = "https://github.com/snicker/skydrop_hass/issues"
ATTRIBUTION = "Data from this integration is provided by Skydrop."
SIGNAL_SKYDROP_UPDATE = "skydrop_api_update"
STARTUP_MESSAGE = "{name} {version} {issue_link} starting..."
SUPPORTED_DOMAINS = ["switch"]

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Configuration
CONF_BINARY_SENSOR = "binary_sensor"
CONF_SENSOR = "sensor"
CONF_SWITCH = "switch"
CONF_ENABLED = "enabled"
CONF_NAME = "name"
CONF_CLIENT_KEY = "client_key"
CONF_CLIENT_SECRET = "client_secret"
CONF_CLIENT_CODE = "client_code"

# Defaults
DEFAULT_NAME = DOMAIN
