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

- `sudo apt-get install git-core python-dev python-pip python-pyaudio libi2c-dev virtualenvwrapper`
- `sudo reboot`
- `git clone git@github.com:apexskier/homedo`
- `cd homedo`
- `mkvirtualenv homedo`
- `workon homedo`
- `pip install -r requirements.txt`
- `./install.sh # might require root`
- `sudo reboot`
- `python server.py`

### Todo

- Make it work reliably without sudo/session setup.
- Make it work on one page.
- Automatically generate pages for each target in system.
- Add logging.
- Add fancy graphs.
