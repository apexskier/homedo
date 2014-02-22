import threading
from datetime import datetime, timedelta
import json

class Learner(object):
    def __init__(self, target, learning=False, debug=False):
        self.target = target
        self.learning = learning
        self.running = True
        try:
            learnfile = open(target['key'] + '-data.json', 'r')
            filedata = learnfile.read()
            self.data = json.loads(filedata)
            learnfile.close()
        except IOError:
            self.data = {}

        self.timer = threading.Timer(1, self.tick)
        self.timer.start()

    def tick(self):
        if not self.running:
            self.timer.cancel()
            self.timer = threading.Timer(60 * 5, self.tick)
            self.timer.start()

        now = datetime.now()
        fivemin = now - timedelta(minutes = now.minute % 5,
                                  seconds = now.second,
                                  microseconds = now.microsecond)

        indx = ((fivemin.day * 24 * 60) +
                (fivemin.hour * 60) +
                fivemin.minute) / 5
        target = float(self.target['driver'].get_target())

        self.data[str(indx)] = {
                'target': target,
                'time': fivemin.strftime("%a %H:%M")
            }
        if self.learning or indx not in self.data:
            self.data[str(indx)]['confidence'] = 1
        elif float(self.data[str(indx)]['target']) == target:
            if 'confidence' in self.data[str(indx)]:
                self.data[str(indx)]['confidence'] = float(self.data[str(indx)]['confidence']) + 1
            else:
                self.data[str(indx)]['confidence'] = 1
        else:
            self.data[str(indx)]['confidence'] -= abs(target - float(self.data[str(indx)]['target'])) / 2
            c = float(self.data[str(indx)]['confidence']) / (1 + float(self.data[str(indx)]['confidence']))
            self.data[str(indx)]['target'] = c * float(self.data[str(indx)]['target']) + (1 - c) * target
        self.saveData()
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
        self.timer.cancel()
        self.running = False

if __name__ == '__main__':
    from libs.thermostat.temp_humid_sensor import Thermostat
    import signal

    def sig_handler(signal, frame):
        print("Stopping")
        l.stop()
        thermostat.off()
    signal.signal(signal.SIGINT, sig_handler)

    thing = {'driver': Thermostat(18, 4, 55), 'key': 'test'}
    thermostat = thing['driver']

    print "making learner"
    l = Learner(thing, True)
    print "made learner"
