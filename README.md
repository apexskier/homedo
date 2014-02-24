# Homedo

## Home automation

Internet connected thermostat and lights.

![Picture of my setup. Sketttcchhh.](https://photos-5.dropbox.com/t/0/AAATmIlvcY2K2Xv1fFao9tQm0HkWQJJK1ttFRmVds2WUaw/12/5821804/jpeg/1024x768/3/1393012800/0/2/2014-02-14%2019.06.17.jpg/2uZPzay2LqMvYsvbfiaZ9AgHwN_kC9h1LzyYebcbu4E)

## Learning

Learns based on events. "Set 65 at this time, set 58 at this time..."

This could use a lot of work.
- Events should chain.
- Changes to events should be applied immediately if they are close to existing events.
- Changes should be applied after reccurrence if they are sort of close to existing events.

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
- `python setup_admin.py` and follow directions
- `python server.py`

### Todo

- Learner should be a list of events, one following another.
  This makes more sense, as changes happen from one to another (on to off to on).
- Make it work reliably without sudo/session setup.
- Make it work on one page.
- Automatically generate pages for each target in system.
- Add logging.
- Add fancy graphs.
