import os
from distutils.core import setup

setup(
        name = "homedo",
        version = "0.0.1",
        author = "Cameron Little",
        author_email = "cameron@camlittle.com",
        description = "Python based home automation",
        url = "http://github.com/apexskier/homedo",
        packages = ["bottle-cork", "wiringpi2"]
    )
