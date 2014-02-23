import threading, datetime
import wiringpi2 as wiringpi
from libs.AM2302.temp_humid_sensor import Sensor

class Thermostat(object):
    def __init__(self, therm_pin, sensor_pin, target_temp=55):
        self.target_temp = target_temp
        self.THERM = therm_pin
        self.sensor = Sensor(sensor_pin)
        self.running = True
        self.heat_on = False
        self.current_temp = None
        self.OUT = 1
        self.IN = 0
        self.PWM = 0

        wiringpi.digitalWrite(self.THERM, 0)

        # give some time to read an initial temperature
        self.timer = threading.Timer(15, self.tick)
        self.timer.start()

    def tick(self):
        self.timer.cancel()
        self.timer = threading.Timer(10, self.tick)
        self.timer.start()

        self.current_temp = (9.0 / 5.0) * float(self.sensor.get()) + 32
        if self.current_temp < self.target_temp - 2 and not self.heat_on:
            self.heat_on = True
            wiringpi.digitalWrite(self.THERM, 1)
        elif self.current_temp >= self.target_temp and self.heat_on:
            self.heat_on = False
            wiringpi.digitalWrite(self.THERM, 0)

    def set(self, target_temp):
        self.target_temp = float(target_temp)
        if self.current_temp and self.current_temp < self.target_temp and not self.heat_on:
            self.heat_on = True
            wiringpi.digitalWrite(self.THERM, 1)
        elif self.current_temp > self.target_temp and self.heat_on:
            self.heat_on = False
            wiringpi.digitalWrite(self.THERM, 0)

    def get(self):
        try:
            self.current_temp = (9.0 / 5.0) * float(self.sensor.get()) + 32
        except:
            pass
        return self.current_temp

    def get_last_time(self):
        return self.sensor.get_last_time()

    def get_target(self):
        return self.target_temp

    def get_status(self):
        return self.heat_on

    def off(self):
        self.timer.cancel()
        self.sensor.off()
        wiringpi.digitalWrite(self.THERM, 0)
