#!/bin/bash

mkdir -p libs
cd libs

# bootstrap
if [ ! -d bootstrap ]; then
    wget https://github.com/twbs/bootstrap/releases/download/v3.1.0/bootstrap-3.1.0-dist.zip
    unzip bootstrap-3.1.0-dist.zip
    mv dist bootstrap
    rm bootstrap-3.1.0-dist.zip
fi

# color-conversion-algorithms.js
if [ ! -f color-conversion-algorithms.js ]; then
    wget https://gist.github.com/mjijackson/5311256/raw/12a6fefb5719b355ca4e7e15196616d0ff717c89/color-conversion-algorithms.js
fi

# draggabilly
if [ ! -f draggabilly.pkgd.min.js ]; then
    wget http://draggabilly.desandro.com/draggabilly.pkgd.min.js
fi

# d3
if [ ! -f d3.v3.min.js ]; then
    wget http://d3js.org/d3.v3.min.js
fi

cd ..
