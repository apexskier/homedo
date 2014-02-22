import threading
from datetime import datetime, timedelta
from settings import *
import json

class Learner(object):
    def __init__(self, target, learning=False, debug=False):
        self.target = target
        self.learning = learning
        self.stop = False
        try:
            learnfile = open(target['key'] + '-data.json', 'r')
            filedata = learnfile.read()
            self.data = json.loads(filedata)
            learnfile.close()
        except IOError:
            self.data = {}

        self.tick()

    def tick(self):
        if not self.stop:
            threading.Timer(60 * 5, self.tick).start()

        now = datetime.now()
        fivemin = now - timedelta(minutes = now.minute % 5,
                                  seconds = now.second,
                                  microseconds = now.microsecond)

        indx = ((fivemin.day * 24 * 60) +
                (fivemin.hour * 60) +
                fivemin.minute) / 5
        target = float(self.target['driver'].get_target())

        if self.learning or indx not in self.data:
            self.data[str(indx)] = {
                    'target': target,
                    'time': fivemin.strftime("%a %H:%M")
                }
            self.saveData()
        elif float(self.data[str(indx)]['target']) != target:
            self.data[str(indx)] = {
                    'target': target * .3 + float(self.data[str(indx)]['target']) * .7,
                    'time': fivemin.strftime("%a %H:%M")
                }
            self.saveData()
        else:
            target['driver'].set(float(self.data[str(indx)]['target']))
        print fivemin

    def saveData(self):
        try:
            learnfile = open(self.target['key'] + '-data.json', 'w')
            filedata = json.dumps(self.data, sort_keys=True, indent=2, separators=(',', ': '))
            learnfile.write(filedata)
            learnfile.close()
        except:
            print("ERROR with writing to file")

    def stop(self):
        self.stop = True

if __name__ == '__main__':
    from libs.thermostat.temp_humid_sensor import Thermostat

    thing = {'driver': Thermostat(18, 4, 55), 'key': 'test'}
    thermostat = thing['driver']
    thermostat_thread = thermostat.run()
    thermostat_thread.start()

    l = Learner(thing, True)
