from libs.ledDriver.ledDriver import RGBDriver, SingleLEDDriver
from libs.thermostat.temp_humid_sensor import Thermostat
import logging

applogger = logging.getLogger('Global')

targets = {
        'rgb1': {
            'name': "RGB Lights",
            'key': 'rgb1',
            'driver': RGBDriver(0, 1, 2),
            'type': "rgbdriver"
        },
        'led1': {
            'name': "LED Light strip",
            'key': 'led1',
            'driver': SingleLEDDriver(3),
            'type': "leddriver"
        },
        'therm': {
            'name': "Heat",
            'key': 'therm',
            'driver': Thermostat(18, 4, 55),
            'type': "thermostat"
        }
    }

