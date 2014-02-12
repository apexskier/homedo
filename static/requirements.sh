#!/bin/bash

mkdir libs
cd libs

# bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v3.1.0/bootstrap-3.1.0-dist.zip
unzip bootstrap-3.1.0-dist.zip
rm bootstrap-3.1.0-dist.zip

# color-conversion-algorithms.js
wget https://gist.github.com/mjijackson/5311256/raw/12a6fefb5719b355ca4e7e15196616d0ff717c89/color-conversion-algorithms.js

# draggabilly
wget http://draggabilly.desandro.com/draggabilly.pkgd.min.js

# jquery
wget http://code.jquery.com/jquery-2.1.0.min.js

# jquery.stayInWebApp.min.js
wget https://raw2.github.com/mrmoses/jQuery.stayInWebApp/master/jquery.stayInWebApp.min.js

cd ..
