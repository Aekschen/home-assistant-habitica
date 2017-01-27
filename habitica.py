import logging
from datetime import timedelta
import json

import voluptuous as vol
import requests

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

AVATAR_URL = 'https://habitica.com/export/avatar-'
RESOURCE_URL = 'https://habitica.com/api/v3/user'
SENSOR_PREFIX = 'habitica_'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

OPTION_TYPES = {
    'name': ['Name', '', ''],
    'hp': ['HP', 'mdi:heart', 'HP'],
    'maxHealth': ['max HP', 'mdi:heart', 'HP'],
    'mp': ['Mana', 'mdi:auto-fix', 'MP'],
    'maxMP': ['max Mana', 'mdi:auto-fix', 'MP'],
    'exp': ['EXP', 'mdi:star', 'EXP'],
    'toNextLevel': ['Next Lvl', 'mdi:star', 'EXP'],
    'lvl': ['Lvl', 'mdi:arrow-up-bold-circle-outline', 'Lvl'],
    'gp': ['Gold', 'mdi:coin', 'Gold'],
    'class': ['Class', 'mdi:sword', '']
}

CONF_API_USER = "api_user"
CONF_API_KEY = "api_key"
CONF_NAME = "name"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_USER): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the RESTful sensor."""
    api_user = str( config.get(CONF_API_USER) )
    api_key = str( config.get(CONF_API_KEY) )
    playername = str( config.get(CONF_NAME) )
    headers = {'x-api-key': api_key, 'x-api-user': api_user}
    resource = RESOURCE_URL
    method = 'GET'
    payload = ''

    rest = HabiticaData(method, resource, headers, payload)
    rest.update()

    if rest.data is None:
        _LOGGER.error('Unable to fetch REST data from Habitica')
        return False

    playerStats = []
    for sensor in OPTION_TYPES:
        playerStats.append(HabiticaSensor(rest, sensor, playername))
    add_devices(playerStats)


class HabiticaSensor(Entity):
    """Implementation of a REST sensor."""

    def __init__(self, rest, option_type, playername):
        """Initialize the REST sensor."""
        self.rest = rest
        self.type = option_type # the option from the list
        self._name = OPTION_TYPES[option_type][0]
        self._unit_of_measurement = OPTION_TYPES[option_type][2]
        self.sensorname = SENSOR_PREFIX + playername + '_'
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensorname + self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def entity_picture(self):
        """Return the entity picture."""
        if self.rest.data:
            value = self.rest.data
            jsonDict = json.loads(value)
            if self.type == 'name':
                url = AVATAR_URL + str(jsonDict["data"]["_id"]) + ".png"
                return url

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.type != 'name':
            return OPTION_TYPES[self.type][1]

    def update(self):
        """Get the latest data from REST API and update the state."""
        self.rest.update()
        value = self.rest.data
        jsonDict = json.loads(value)

        if self.type == 'name':
            self._state = jsonDict["data"]["profile"]["name"]
        elif self.type == 'hp':
            self._state = jsonDict["data"]["stats"]["hp"]
        elif self.type == 'maxHealth':
            self._state = jsonDict["data"]["stats"]["maxHealth"]
        elif self.type == 'mp':
            self._state = jsonDict["data"]["stats"]["mp"]
        elif self.type == 'maxMP':
            self._state = jsonDict["data"]["stats"]["maxMP"]
        elif self.type == 'exp':
            self._state = jsonDict["data"]["stats"]["exp"]
        elif self.type == 'toNextLevel':
            self._state = jsonDict["data"]["stats"]["toNextLevel"]
        elif self.type == 'lvl':
            self._state = jsonDict["data"]["stats"]["lvl"]
        elif self.type == 'gp':
            self._state = '{0:.0f}'.format(jsonDict["data"]["stats"]["gp"])
        elif self.type == 'class':
            self._state = jsonDict["data"]["stats"]["class"]


class HabiticaData(object):
    """Class for handling the data retrieval."""

    def __init__(self, method, resource, headers, data):
        """Initialize the data object."""
        self._request = requests.Request(
            method, resource, headers=headers, data=data).prepare()
        self._verify_ssl = True
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from REST service with provided method."""
        try:
            with requests.Session() as sess:
                response = sess.send(
                    self._request, timeout=10, verify=self._verify_ssl)

            self.data = response.text

        except requests.exceptions.RequestException:
            _LOGGER.error("Error fetching data from Habitica: %s", self._request)
            self.data = None
