import signal, sys, os, threading
from settings import *
import server
from learner import Learner

thermostat = targets['therm']['driver']

def Shutdown(signal, frame):
    for target in targets:
        targets[target]['driver'].off()
    thermLearner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, Shutdown)

thermLearner = Learner(targets['therm'], debug=True)
server.runServer(True)
