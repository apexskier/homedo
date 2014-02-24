import threading
from datetime import datetime, timedelta
import json

class Predicting(object):
    def __init__(self, target, key, learning=False, debug=False):
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

class Events(object):
    def __init__(self, target, key, baseline, threshold):
        self.target = target
        self.key = key
        self.filename = key + '-data.json'
        self.baseline = baseline
        self.threshold = threshold

        try:
            learnfile = open(self.filename, 'r')
            filedata = learnfile.read()
            self.data = json.loads(filedata)
            learnfile.close()
        except IOError:
            self.data = {
                    'events': [],
                    'possible_events': []
                }

    def saveData(self):
        try:
            filedata = json.dumps(self.data, sort_keys=True, indent=2, separators=(',', ': '))
            learnfile = open(self.filename, 'w')
            learnfile.write(filedata)
            learnfile.close()
        except:
            print("ERROR with writing to file")
        pass

    def watchEvent(self, func):
        def wrapper(funcself, val):
            now = datetime.now()
            nowsec = now.second + \
                  now.minute * 60 + \
                  now.hour * 60 * 60 + \
                  now.weekday() * 24 * 60 * 60
            existing_event = False
            possible_event = False
            cleanup = []
            before = True
            for event in self.data['events']:
                # check if before existing event (push earlier/change temp)
                if 0 < event['seconds'] - nowsec < 5 * 60:
                    if event['change']:
                        if event['change']['before']: # assume you want to push earlier and avg temp
                            Events._changeSecs(event, (event['seconds'] + event['change']['seconds'] + nowsec) / 3.0)
                            event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                        elif event['val'] - val > 0 and event['change']['val'] - val > 0 or \
                           val - event['val'] > 0 and val - event['change']['val'] > 0:
                            # change temperature
                            event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                        # else get rid of change because we've seen inconsitancies
                        # TODO: add time check since change was added and add this as a new change
                        event['change'] = {}
                    else: # add new change
                        event['change'] = {
                                'before': before,
                                'val': val,
                                'seconds': nowsec
                            }
                    existing_event = True
                    break
                # check if after existing event (change temp/remove)
                elif 0 < nowsec - event['seconds'] < 5 * 60:
                    if 'change' in event and event['change']:
                        if abs(self.baseline - val) < self.threshold and abs(self.baseline - event['change']['val']) < self.threshold:
                            # assume you want to cancel event
                            cleanup.append(event)
                        elif abs(event['change']['val'] - val) < self.threshold:
                            # assume you want to change val
                            Events._changeSecs(event, (event['seconds'] + nowsec) / 2.0) # weight change less
                            event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                        event['change'] = {}
                    else: # add new change
                        event['change'] = {
                                'before': before,
                                'val': val,
                                'seconds': nowsec
                            }
                    existing_event = True
                    break
            if not existing_event:
                # check similar possible event
                for event in self.data['possible_events']:
                    if abs(event['seconds'] - nowsec) < 7.5 * 60:
                        if abs(val - event['val']) < self.threshold:
                            # add event
                            # print("Adding: ", val, event['val'], nowsec, event['seconds'])
                            self.data['events'].append({
                                    'seconds': (nowsec + event['seconds']) / 2.0,
                                    'val': (val + event['val']) / 2.0,
                                    'time': Events._secsToTimeStr((nowsec + event['seconds']) / 2.0)
                                })
                        # inconsistancies
                        cleanup.append(event)
                        event = True
                        break
                if not possible_event:
                    self.data['possible_events'].append({
                            'seconds': nowsec,
                            'val': val
                        })

            for event in cleanup:
                try:
                    self.data['possible_events'].remove(event)
                except:
                    try:
                        self.data['events'].remove(event)
                    except:
                        pass
            self.saveData()

            return func(funcself, val)
        return wrapper

    @staticmethod
    def _changeSecs(e, s):
        e['seconds'] = s
        e['time'] = Events._secsToTimeStr(s)

    @staticmethod
    def _secsToTimeStr(seconds):
        weekday = seconds / (24 * 60 * 60)
        seconds = seconds % (24 * 60 * 60)
        hour = seconds / (60 * 60)
        seconds = seconds % (60 * 60)
        minute = seconds / 60
        second = seconds % 60
        # 2001 starts on a monday, so it makes the week system work
        return datetime(year=2001, month=1, day=1 + int(weekday), second=int(second), minute=int(minute), hour=int(hour)).strftime('%a %H:%M')
