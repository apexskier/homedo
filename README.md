# Homedo

## Home automation

Internet connected thermostat and lights.

## Setup

- `sudo apt-get install python-dev libi2c-dev`
- Install this - http://www.airspayce.com/mikem/bcm2835/bcm2835-1.36.tar.gz
- Install this - http://wiringpi.com/download-and-install/
- Intsall this - https://github.com/Gadgetoid/WiringPi2-Python
- `make`
- `pip install -r requirements.txt`
- NOT IN VIRTUALENV
- Unblacklist i2c - http://www.raspberrypi.org/phpBB3/viewtopic.php?f=33&t=31717
- Enable i2c - http://www.instructables.com/id/Raspberry-Pi-I2C-Python/step3/Enable-kernel-I2C-Module/
- `sudo adduser $USER i2c`
- `python server.py`

### Todo

- Make it work reliably without sudo/session setup.
- Add scheduling.
- Make it work on one page.
- Automatically generate pages for each target in system.
- Add logging.
- Add fancy graphs (of logs).
