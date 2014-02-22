import signal, sys, os, threading
from settings import *
import server
from learner import Learner

thermostat = targets['therm']['driver']
thermostat_thread = thermostat.run()
thermostat_thread.start()

def sig_handler(signal, frame):
    print
    for target in targets:
        targets[target]['driver'].off()
    print("Waiting for Thermostat to finish.")
    thermostat_thread.join()
    thermLearning.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

thermLearner = Learner(targets['therm'], learning=True, debug=True)
server.runServer(True)
