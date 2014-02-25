import threading, sys
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
            filedata = json.dumps(self.data, sort_keys=True, indent=2, separators=(',', ': ')) + '\n'
            learnfile.write(filedata)
            learnfile.close()
        except Exception as e:
            print("ERROR with writing to file")
            print(e)

    def stop(self):
        self.timer.cancel()
        self.running = False

class NaiveEvents(object):
    def __init__(self, target, key, valbaseline, valthreshold, timethreshold):
        self.target = target
        self.key = key
        self.filename = key + '-data.json'
        self.baseline = valbaseline
        self.valthreshold = valthreshold
        self.timethreshold = timethreshold

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
        except Exception as e:
            print("ERROR with writing to file")
            print(e)

    def watchEvent(self, func):
        def wrapper(funcself, val):
            now = datetime.now()
            nowsec = now.second + \
                  now.minute * 60 + \
                  now.hour * 60 * 60 + \
                  now.weekday() * 24 * 60 * 60
            nowstr = now.strftime('%c')
            existing_event = False
            possible_event = False
            cleanup = []
            before = True
            for event in self.data['events']:
                # check if before existing event (push earlier/change temp)
                if 0 < event['seconds'] - nowsec < self.timethreshold:
                    if event['change']:
                        if event['change']['before']: # assume you want to push earlier and avg temp
                            Events._changeSecs(event, (event['seconds'] + event['change']['seconds'] + nowsec) / 3.0)
                            event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                            event['updated'] = nowstr
                        elif event['val'] - val > 0 and event['change']['val'] - val > 0 or \
                             val - event['val'] > 0 and val - event['change']['val'] > 0:
                            # change temperature
                            event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                            event['updated'] = nowstr
                        # else get rid of change because we've seen inconsitancies
                        # TODO: add time check since change was added and add this as a new change
                        event['change'] = {}
                    else: # add new change
                        event['change'] = {
                                'before': before,
                                'val': val,
                                'seconds': nowsec,
                                'updated': nowstr
                            }
                    existing_event = True
                    break
                # check if after existing event (change temp/remove)
                elif 0 <= nowsec - event['seconds'] < self.timethreshold:
                    if 'change' in event and event['change']:
                        if (now - datetime.strptime(event['change']['updated'], '%c')) > timedelta(seconds = self.timethreshold):
                            if abs(val - self.valbaseline) < self.valthreshold:
                                # cancel change
                                event['change'] = {}
                            else:
                                # just update change
                                event['change']['val'] = val
                                event['change']['updated'] = nowstr
                        else:
                            if abs(self.baseline - val) < self.valthreshold and abs(self.baseline - event['change']['val']) < self.valthreshold:
                                # assume you want to cancel event
                                cleanup.append(event)
                            elif abs(event['change']['val'] - val) < self.valthreshold:
                                # assume you want to change val
                                Events._changeSecs(event, (event['seconds'] + nowsec) / 2.0) # weight change less
                                event['val'] = (event['val'] + val + event['change']['val']) / 3.0
                                event['updated'] = nowstr
                            event['change'] = {}
                    else: # add new change
                        event['change'] = {
                                'before': before,
                                'val': val,
                                'seconds': nowsec,
                                'updated': nowstr
                            }
                    existing_event = True
                    break
            if not existing_event:
                # check similar possible event
                for event in self.data['possible_events']:
                    if abs(event['seconds'] - nowsec) < self.timethreshold:
                        if abs(val - event['val']) < self.valthreshold:
                            # add event
                            # print("Adding: ", val, event['val'], nowsec, event['seconds'])
                            self.data['events'].append({
                                    'seconds': (nowsec + event['seconds']) / 2.0,
                                    'val': (val + event['val']) / 2.0,
                                    'time': Events._secsToTimeStr((nowsec + event['seconds']) / 2.0),
                                    'updated': nowstr
                                })
                        # inconsistancies
                        cleanup.append(event)
                        event = True
                        break
                if not possible_event:
                    self.data['possible_events'].append({
                            'seconds': nowsec,
                            'val': val,
                            'updated': nowstr
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

    def findEventVal(self):
        now = datetime.now()
        nowsec = now.second + \
              now.minute * 60 + \
              now.hour * 60 * 60 + \
              now.weekday() * 24 * 60 * 60
        for event in self.data['events']:
            if abs(event['seconds'] - nowsec) < self.timethreshold / 2:
                if 'change' in event and event['change'] and \
                   (now - datetime.strptime(event['change']['updated'], '%c')) > timedelta(seconds = self.timethreshold):
                    pass
                else:
                    return float(event['val'])
        return None

    def applyEvent(self, func):
        def wrapper(funcself):
            now = datetime.now()
            nowsec = now.second + \
                  now.minute * 60 + \
                  now.hour * 60 * 60 + \
                  now.weekday() * 24 * 60 * 60
            val = self.findEventVal()
            if val:
                funcself.target_temp = val
                print("Found val: {}".format(val))
            return func(funcself)
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

class Events(object):
    def __init__(self, target, key, valbaseline, valthreshold, timethreshold):
        self.lock = threading.RLock()
        with self.lock:
            self.target = target
            self.key = key
            self.filename = key + '-data.json'
            self.baseline = valbaseline # TODO: Calculate based on lowest of events' vals?
            self.valthreshold = valthreshold
            self.timethreshold = timethreshold

            try:
                learnfile = open(self.filename, 'r')
                filedata = learnfile.read()
                self.data = sorted(json.loads(filedata), key=lambda e: datetime.strptime(e['time'], '%a %H:%M'))
                learnfile.close()
            except IOError:
                self.data = []

            if not self.data:
                now = datetime.now()
                self.data = [{
                    "certain": True,
                    "time": now.strftime('%a %H:%M'),
                    "updated": now.strftime('%c'),
                    "val": self.target.get_target()
                }]

            self.events = self._data()
            pe = None
            # populate data
            for event in self.data:
                c = None
                if 'change' in event and event['change']:
                    c = self._event(event['change']['time'], event['change']['updated'], event['change']['val'])
                t = self._event(event['time'], event['updated'], event['val'], pe, pe, c, True)
                self.events.addAfter(t)
            # find where we are
            self.events.sync()
            self.events.display()

            # schedule next event
            self.scheduled = None
            self.scheduleFollowingEvent(self.events.pos)

    class _data(object):
        def __init__(self, pos=None):
            self.pos = pos

        def sync(self):
            if self.pos:
                now = datetime.strptime(datetime.now().strftime('%a %H:%M'), '%a %H:%M')
                newpos = self.pos.n
                # make sure the current pos is the last event to happen
                while newpos.time < now and not newpos == self.pos.n:
                    newpos = newpos.n
                self.pos = newpos

        def addAfter(self, event, pos=None):
            if not self.pos:
                self.pos = event
                self.pos.n = self.pos
                self.pos.p = self.pos
            else:
                if not pos:
                    pos = self.pos
                t = pos.n
                event.p = pos
                pos.n = event
                event.n = t

        def remove(self, event):
            if event == event.n and event == event.p:
                self.pos = None
                del event
            else:
                event.n.p = event.p
                event.p.n = event.n
                del event

        def lastEvent(self):
            if self.pos:
                if self.pos == self.pos.p:
                    return self.pos
                p = self.pos
                while p.certain == False:
                    p = p.p
                return p
            return None

        def nextEvent(self):
            if self.pos:
                if self.pos == self.pos.n:
                    return self.pos
                n = self.pos.n
                while n.certain == False:
                    n = n.n
                return n
            return None

        def display(self):
            def _d(l, head):
                if l == head:
                    return
                print('    {} = {} ->'.format(l.time.strftime('%a %H:%M'), l.val))
                _d(l.n, head)
            if self.pos:
                print('|-> {} = {} ->'.format(self.pos.time.strftime('%a %H:%M'), self.pos.val))
                _d(self.pos.n, self.pos)
            else:
                print("Empty")

        def toDict(self):
            ret = []
            def _d(e, head):
                if e == head:
                    return
                ret.append(e.toObject())
                _d(e.n, head)
            if self.pos:
                ret.append(self.pos.toObject())
                _d(self.pos.n, self.pos)
            return ret

    class _event(object):
        def __init__(self, time, updated, val, n=None, p=None, change=None, certain=False):
            self.time = datetime.strptime(time, '%a %H:%M')
            self.updated = datetime.strptime(updated, '%c')
            self.val = float(val)
            self.certain = certain
            self.n = n
            if self.n:
                self.n.p = self
            self.p = p
            if self.p:
                self.p.n = self
            self.change = change

        def __del__(self):
            self.n = None
            self.p = None

        def toObject(self):
            ret = {
                    'time': self.time.strftime('%a %H:%M'),
                    'updated': self.updated.strftime('%c'),
                    'val': self.val,
                    'certain': self.certain
                }
            if self.change:
                ret['change'] = self.change.toObject()
            return ret

    def saveData(self):
        try:
            filedata = json.dumps(self.events.toDict(), sort_keys=True, indent=2, separators=(',', ': '))
            learnfile = open(self.filename, 'w')
            learnfile.write(filedata)
            learnfile.close()
        except Exception as e:
            print("ERROR with writing to file")
            print(e)

    def normTime(self, time):
        return datetime.strptime(time.strftime('%a %H:%M'), '%a %H:%M')

    def watchEvent(self, func):
        def wrapper(funcself, val):
            with self.lock:
                now = datetime.now()
                normTime = self.normTime(now)

                le = self.events.lastEvent() # last event
                ne = self.events.nextEvent() # next event
                if le and 0 <= (normTime - le.time).total_seconds() < self.timethreshold: # if close enough to last event
                    if le.change and 0 <= (normTime - le.change.updated).total_seconds() < self.timethreshold: # recently modified
                        # update change
                        le.change.val = val
                    else:
                        if not le == ne and abs(val - le.p.val) < self.valthreshold:
                            # prepare to cancel event
                            if le.change:
                                if abs(val - le.change.val) < self.valthreshold: # cancel event
                                    self.events.remove(le)
                                else: # update change
                                    le.change.val = (le.change.val + val) / 2.0
                                    le.change.time = le.change.time + (normTime - le.change.time) / 2
                                    le.change.updated = now
                            else:
                                le.change = self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val)
                        else:
                            # prepare to change event's val
                            if le.change:
                                le.val = (le.change.val + val + le.val) / 3.0 # update event
                                le.updated = now
                                del le.change
                                le.change = None
                            else:
                                le.change = self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val)
                elif ne and 0 <= (ne.time - normTime).total_seconds() < self.timethreshold: # if close enough to next event
                    if ne.change and 0 <= (ne.change.updated - normTime).total_seconds() < self.timethreshold: # recently modified
                        # update change
                        ne.change.val = val
                    else:
                        if abs(val - ne.val) < self.valthreshold:
                            # move next event earlier
                            if ne.change:
                                if abs(val - ne.change.val) < self.valthreshold: # move event
                                    ne.val = (ne.change.val + val + ne.val) / 3.0
                                    ne.time = ne.time + (((ne.change.time + (normTime - ne.change.time) / 2) - ne.time) / 2)
                                    ne.updated = now
                                    del ne.change
                                    ne.change = None
                                else: # update change
                                    ne.change.val = (ne.change.val + val) / 2.0
                                    ne.change.time = ne.change.time + (normTime - ne.change.time) / 2
                                    le.change.updated = now
                            else:
                                ne.change = self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val)
                        elif not ne == le and abs(val - ne.n.val) < self.valthreshold:
                            self.scheduled.cancel() # cancel next event
                            self.scheduleFollowingEvent(ne)
                            if ne.change:
                                if abs(val - ne.change.val) < self.valthreshold: # cancel event
                                    self.events.remove(ne)
                                else: # update change
                                    ne.change.val = (ne.change.val + val) / 2.0
                                    ne.change.time = ne.change.time + (normTime - ne.change.time) / 2
                                    ne.change.updated = now
                            else:
                                ne.change = self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val)
                    # TODO: cancel next event this time
                else: # new event
                    if le and ne:
                        if le.n == ne: # no uncertain events
                            self.events.addAfter(self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val))
                        else: # uncertain events have been seen
                            # check uncertain events to see if they match
                            walker = le.n
                            while walker.certain == False and abs(val - walker.val) > self.valthreshold and abs(time - walker.time).total_seconds() > self.timethreshold:
                                walker = walker.n
                            if walker == ne: # no uncertain events match
                                self.events.addAfter(self._event(now.strftime('%a %H:%M'), now.strftime('%c'), val))
                            else:
                                walker.certain = True

                # TODO: how can i move an events' time forward?
                self.saveData()

                return func(funcself, val)
        return wrapper

    def scheduleFollowingEvent(self, event):
        if self.scheduled:
            self.scheduled.cancel()
            self.scheduled = None
        if event:
            e = event.n
            while e.certain == False and not e == event:
                e = event.n
            secs = ((e.time - self.normTime(datetime.now())).total_seconds() - 1) % (7 * 24 * 60 * 60)
            self.scheduled = threading.Timer(secs, self.doEvent, [e])

    def doEvent(self, event):
        target.target_temp = event.val

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
