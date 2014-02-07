
update-libs: libs/rgbLED libs/thermostat
	(cd libs/rgbLED && git pull)
	(cd libs/thermostat && git pull && make)

libs/rgbLED:
	git clone git@github.com:apexskier/rgbLED libs/rgbLED

libs/thermostat:
	git clone git@github.com:apexskier/thermostat libs/thermostat
	(cd libs/thermostat && make)
