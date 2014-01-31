import json, signal, sys
from bottle import redirect, request, route, run, template, get, post, static_file
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket

sys.path.append('libs')

from rgbDriver import RGBDriver, SingleLEDDriver
from temp_humid_sensor import Thermostat

targets = {
        'rgb1': RGBDriver(0, 1, 2),
        'led1': SingleLEDDriver(3),
        'thermostat': Thermostat(17, 55)
    }

thermostat = targets['thermostat']
thermostat_thread = thermostat.run()
thermostat_thread.start()

def sig_handler(signal, frame):
    print
    for target in targets:
        targets[target].to_off()
    print("Waiting for Thermostat to finish.")
    thermostat_thread.join()
    sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

@get('/')
def index():
    return template('index',
            current_temp=thermostat.get_temp(),
            last_time=thermostat.get_last_time(),
            target_temp=thermostat.get_target())

@get('/control', apply=[websocket])
def control(ws):
    while True:
        message = ws.receive()
        if message:
            print "Recieved message: " + message
            data = json.loads(message)
            driver = None
            if u'target' in data:
                driver = targets[str(data[u'target'])]
                driver_type = type(driver)
                action = data[u'action']
                if action == 'set':
                    if driver_type == RGBDriver:
                        driver.set_hex_color(data[u'value'])
                    elif driver_type == SingleLEDDriver:
                        driver.set_(data[u'value'])
                    elif driver_type == Thermostat:
                        driver.set_(data[u'value'])
                if action == 'off':
                    driver.to_off()
        else:
            break

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

run(host='0.0.0.0', port=8080, server=GeventWebSocketServer)
