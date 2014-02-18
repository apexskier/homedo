all:
	make update-libs
	make static

static: static/libs
	(cd static && ./requirements.sh)

update-libs: libs/ledDriver libs/thermostat
	(cd libs/ledDriver && git pull)
	(cd libs/thermostat && git pull && make)

libs/ledDriver:
	git clone git@github.com:apexskier/ledDriver libs/ledDriver

libs/thermostat:
	git clone git@github.com:apexskier/thermostat libs/thermostat
	(cd libs/thermostat && make)
