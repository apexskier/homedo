# Homedo

## Home automation

Internet connected thermostat and lights.

## Learning

Learns based on events. "Set 65 at this time, set 58 at this time..."

Events chain off of one another in a doubly linked list. So, the thermostat
only needs to know what the last event was. It can then schedule the next one,
know what event needs changing with manual user input, etc. This also lends
itself to a thermostat. If I make a manual change, the target doesn't get reset
until the next event.

## Setup

- `sudo apt-get install python-dev libi2c-dev`
- Install this - http://www.airspayce.com/mikem/bcm2835/bcm2835-1.36.tar.gz
- Install this - http://wiringpi.com/download-and-install/
- Install this - https://github.com/Gadgetoid/WiringPi2-Python
- `make`
- `pip install -r requirements.txt`
- NOT IN VIRTUALENV
- Unblacklist i2c - http://www.raspberrypi.org/phpBB3/viewtopic.php?f=33&t=31717
- Enable i2c - http://www.instructables.com/id/Raspberry-Pi-I2C-Python/step3/Enable-kernel-I2C-Module/
- `sudo adduser $USER i2c`
- `sudo apt-get install python-pyaudio`
- http://learn.adafruit.com/usb-audio-cards-with-a-raspberry-pi/instructions
- `python setup_admin.py` and follow directions
- `python server.py`

### Todo

- Make it work reliably without sudo/session setup.
- Make it work on one page.
- Automatically generate pages for each target in system.
- Add logging.
- Add fancy graphs.
