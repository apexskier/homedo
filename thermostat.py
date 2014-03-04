from threading import Timer, RLock
from datetime import datetime
import wiringpi2 as wiringpi
from am2302_rpi import Sensor
import learner
import jsonlog

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
        self.bounds = [55, 66, 80]
        self.learner = learner.Events(self, 'therm', 55, 5, 5 * 60)
        self.set_lock = RLock()

        wiringpi.digitalWrite(self.THERM, 0)

        # give some time to read an initial temperature
        self.timer = Timer(15, self.tick)
        self.timer.start()
        self.temp_log_timer = Timer(5 * 60, self.logTemp)
        self.temp_log_timer.start()
        self.temp_logger = jsonlog.jsonLog('data/real-therm-data')

    def tick(self):
        def _tick(self):
            self.timer.cancel()
            self.timer = Timer(10, self.tick)
            self.timer.start()

            t = self.sensor.get()
            if t:
                self.current_temp = (9.0 / 5.0) * float(t) + 32
                if self.current_temp < self.target_temp - 2 and not self.heat_on:
                    self.heat_on = True
                    wiringpi.digitalWrite(self.THERM, 1)
                elif self.current_temp >= self.target_temp and self.heat_on:
                    self.heat_on = False
                    wiringpi.digitalWrite(self.THERM, 0)
        _tick(self)

    def logTemp(self):
        if self.current_temp:
            self.temp_logger.log({
                    'time': datetime.now().strftime("%c"),
                    'val': self.get(),
                    'on': self.heat_on
                })
        self.temp_log_timer = Timer(5 * 60, self.logTemp)
        self.temp_log_timer.start()

    def set(self, target_temp):
        with self.set_lock:
            @self.learner.watchEvent
            def _set(self, target_temp):
                self.target_temp = float(target_temp)
                if self.current_temp and self.current_temp < self.target_temp and not self.heat_on:
                    self.heat_on = True
                    wiringpi.digitalWrite(self.THERM, 1)
                elif self.current_temp > self.target_temp and self.heat_on:
                    self.heat_on = False
                    wiringpi.digitalWrite(self.THERM, 0)
            if self.bounds[0] <= float(target_temp) <= self.bounds[-1]:
                _set(self, target_temp)

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

    def get_scheduled(self):
        return self.learner.getScheduled()

    def set_scheduled(self, val, time):
        self.learner.setScheduled(val, time)

    def up(self):
        self.set(self.bounds[1])

    def down(self):
        self.set(self.bounds[0])

    def off(self):
        if self.timer:
            self.timer.cancel()
        if self.temp_log_timer:
            self.temp_log_timer.cancel()
        self.sensor.off()
        self.learner.off()
        wiringpi.digitalWrite(self.THERM, 0)

if __name__ == '__main__':
    import signal, sys

    def sig_handler(signal, frame):
        print("Stopping")
        thermostat.off()
    signal.signal(signal.SIGINT, sig_handler)

    print("Setting up thermostat.")
    thermostat = Thermostat(18, 4, 55)

    import time
    print("Waiting for reading.")
    for i in range(0, 15):
        print(i)
        time.sleep(1)
    print("Trying a set.")
    thermostat.set(60)
    print thermostat.get()
    thermostat.off()
