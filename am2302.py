from subprocess import Popen, PIPE, call
import threading, datetime, os
import wiringpi2 as wiringpi

wiringpi.wiringPiSetupSys()

class Sensor(object):
    def __init__(self, pin):
        self.current_temp = None
        self.temp = None
        self.humid = None
        self.last_time = None
        self.INPUT = pin

        call(["gpio", "export", str(self.INPUT), "in"])

        self.timer = threading.Timer(0, self.tick)
        self.timer.start()

    def tick(self):
        self.timer = threading.Timer(10, self.tick)
        self.timer.start()

        try:
            th_cmd = Popen(["sudo", "./am2302", str(self.INPUT)], stdout=PIPE)
            th_out, th_err = th_cmd.communicate()

            if th_out and th_out != "err":
                self.last_time = datetime.datetime.now()
                temp, humid = th_out.split(',')
                self.temp = temp
                self.humid = humid
                # self.current_temp = (9.0 / 5.0) * float(temp) + 32
        except:
            print("Error reading from sensor.")

    def get(self):
        return self.temp

    def get_last_time(self):
        return self.last_time

    def off(self):
        self.timer.cancel()
