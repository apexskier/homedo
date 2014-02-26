import threading, sys
from datetime import datetime, timedelta
import json

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
                self.data = sorted(
                        json.loads(filedata),
                        key=lambda e:
                            datetime.strptime(e['time'], '%a %H:%M:%S') + \
                            timedelta(
                                    days={'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}[e['time'][:3]]
                                )
                    )
                learnfile.close()
            except IOError:
                self.data = []

            if not self.data:
                now = datetime.now()
                self.data = [{
                    "certain": True,
                    "time": now.strftime('%a %H:%M:%S'),
                    "updated": now.strftime('%c'),
                    "val": self.target.get_target()
                }]

            self.events = self._data()
            pe = None
            # populate data
            for event in self.data:
                print(event['time'])
                c = None
                if 'change' in event and event['change']:
                    c = self._event(event['change']['time'], event['change']['updated'], event['change']['val'])
                t = self._event(event['time'], event['updated'], event['val'], change=c, certain=event['certain'])
                self.events.addAfter(t)

            # schedule next event
            self.scheduled = None
            self.scheduleFollowingEvent(self.events.findLast())
            self.events.display()
            self.wait = None

    class _data(object):
        def __init__(self, pos=None):
            self.pos = pos

        def findLast(self):
            if self.pos and self.pos.n != self.pos:
                now = Events.normTime(datetime.now())
                print('\nnow: ' + now.strftime('%a %H:%M:%S'))
                # make sure the current pos is the last event to happen
                while not (self.pos.time < now and self.pos.n.time > now):
                    self.pos = self.pos.n
                    if self.pos.time > self.pos.n.time:
                        return self.pos
                return self.pos

        def addAfter(self, event, pos=None):
            print("Adding After")
            if not self.pos:
                self.pos = event
                self.pos.n = self.pos
                self.pos.p = self.pos
            else:
                if not pos:
                    pos = self.pos
                event.n = pos.n
                event.p = pos
                pos.n = event
                self.pos = self.pos.n

        def addBefore(self, event, pos=None):
            if not self.pos:
                self.pos = event
                self.pos.n = self.pos
                self.pos.p = self.pos
            else:
                if not pos:
                    pos = self.pos
                event.n = pos
                event.p = pos.p
                pos.p = event
                self.pos = self.pos.p

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
                print('    {} = {} ->'.format(l.time.strftime('%a %H:%M:%S'), l.val))
                _d(l.n, head)
            if self.pos:
                print('|-> {} = {} ->'.format(self.pos.time.strftime('%a %H:%M:%S'), self.pos.val))
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
            self.time = datetime.strptime(time, '%a %H:%M:%S')
            self.time += timedelta(days={'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}[time[:3]])
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
                    'time': self.time.strftime('%a %H:%M:%S'),
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

    @staticmethod
    def normTime(time):
        t = time.strftime('%a %H:%M:%S')
        return datetime.strptime(t, '%a %H:%M:%S') + \
            timedelta(
                    days={'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}[t[:3]]
                )

    def watchEvent(self, func):
        def wrapper(funcself, val):
            with self.lock:
                if self.wait:
                    self.wait.cancel()
                self.wait = threading.Timer(10, self.watchEventInner, [val, datetime.now()])
                self.wait.start()
                return func(funcself, val)
        return wrapper

    def watchEventInner(self, val, now):
        with self.lock:
            normTime = Events.normTime(now)

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
                            le.change = self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val)
                    else:
                        # prepare to change event's val
                        if le.change:
                            le.val = (le.change.val + val + le.val) / 3.0 # update event
                            le.updated = now
                            del le.change
                            le.change = None
                        else:
                            le.change = self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val)
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
                            ne.change = self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val)
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
                            ne.change = self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val)
                # TODO: cancel next event this time
            else: # new event
                if le and ne:
                    if le.n == ne: # no uncertain events
                        self.events.addAfter(self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val))
                    else: # uncertain events have been seen
                        # check uncertain events to see if they match
                        walker = le.n
                        while walker.certain == False and abs(val - walker.val) > self.valthreshold and abs(normTime - walker.time).total_seconds() > self.timethreshold:
                            walker = walker.n
                        if walker == ne: # no uncertain events match
                            self.events.addAfter(self._event(now.strftime('%a %H:%M:%S'), now.strftime('%c'), val))
                        else:
                            walker.certain = True

            # TODO: how can i move an events' time forward?
            self.saveData()

    def scheduleFollowingEvent(self, event):
        if self.scheduled:
            self.scheduled.cancel()
            self.scheduled = None
        if event:
            e = event.n
            while e.certain == False and not e == event:
                e = event.n
            secs = ((e.time - Events.normTime(datetime.now())).total_seconds() - 1) % (7 * 24 * 60 * 60)
            self.scheduled = threading.Timer(secs, self.doEvent, [e])
            self.scheduled.start()
            self.events.pos = self.events.pos.n
            print("Scheduled {}, {} in {} seconds.".format(e.time.strftime('%a %H:%M:%S'), e.val, secs))

    def doEvent(self, event):
        print("Setting target to {}".format(event.val))
        self.target.target_temp = event.val
        self.scheduleFollowingEvent(event)

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
        return datetime(year=2001, month=1, day=1 + int(weekday), second=int(second), minute=int(minute), hour=int(hour)).strftime('%a %H:%M:%S')

    def off(self):
        if self.scheduled:
            self.scheduled.cancel()
        if self.wait:
            self.wait.cancel()
