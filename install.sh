#!/bin/bash

mkdir -p tmp && cd tmp

echo "Testing for Raspberry Pi C library."
if [ ! -e "/usr/local/include/bcm2835.h" ]; then
    echo "Installing Raspberry Pi C libraries..."

    if [ ! -f bcm2835-1.36.tar.gz ]; then
        wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.36.tar.gz
    fi
    tar -xzf bcm2835-1.36.tar.gz
    rm bcm2835-1.36.tar.gz

    cd bcm2835-1.36

    ./configure > /dev/null
    make > /dev/null
    sudo make install > /dev/null

    cd ..
    rm -r bcm2835-1.36
fi
echo "Installed!"

echo "Testing for wiringpi library."
if [ ! -e "/usr/local/include/wiringPi.h" ]; then
    echo "Installing wiringpi2..."
    git clone git://git.drogon.net/wiringPi
    cd wiringPi
    sudo ./build
    cd ..
    rm -rf wiringPi
fi
echo "Installed!"

echo "Testing for wiringpi2 python library."
if [ ! -d "/usr/local/lib/python2.7/dist-packages/wiringpi2-1.0.10-py2.7-linux-armv6l.egg/" ]; then
    echo "Installing WiringPi2-Python..."
    git clone https://github.com/Gadgetoid/WiringPi2-Python.git
    cd WiringPi2-Python
    sudo python setup.py install
    cd ..
    sudo rm -rf WiringPi2-Python
fi
echo "Installing!"

echo "Enabling i2c."
sudo sed -i 's/^\(blacklist i2c-bcm2708\)/#\1/' /etc/modprobe.d/raspi-blacklist.conf
if ! grep i2c-dev /etc/modules >/dev/null; then
    sudo sed -i 's/^\(snd-bcm2835\)/\1\ni2c-dev/' /etc/modules
fi

echo "Adding user to i2c group."
if ! groups $USER | grep i2c >/dev/null; then
    sudo adduser $USER i2c >/dev/null
fi

cd ..

mkdir -p app
mkdir -p data
mkdir -p logs
mkdir -p conf

if [ ! -f conf/users.json ]; then
    echo "Setting up temp admin."
    python setup_admin.py
fi

if [ ! -f am2302 ]; then
    echo "Making temperature sensor."
    make ths
fi

echo "Getting static (frontend) libraries."
cd static
./requirements.sh
cd ..

# kill $(ps aux | grep server.py | grep -v grep | cut -c 10-15) && fg
