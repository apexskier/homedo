all:
	make update-libs
	make static

static: static/libs
	(cd static && ./requirements.sh)

update-libs: libs/ledDriver libs/AM2302
	(cd libs/ledDriver && git pull)
	(cd libs/AM2302 && git pull && make)

libs/ledDriver:
	git clone git@github.com:apexskier/ledDriver libs/ledDriver

libs/AM2302:
	git clone git@github.com:apexskier/AM2302 libs/AM2302
	(cd libs/AM2302 && make)
