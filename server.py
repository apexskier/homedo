import json, signal, sys, os
from bottle import redirect, request, route, run, template, get, post, static_file, debug, response
from bottle.ext.websocket import GeventWebSocketServer
from bottle.ext.websocket import websocket
import colorsys

from libs.ledDriver.ledDriver import RGBDriver, SingleLEDDriver
from libs.thermostat.temp_humid_sensor import Thermostat

targets = {
        'rgb1': {
            'name': "RGB Lights",
            'key': 'rgb1',
            'driver': RGBDriver(0, 1, 2),
            'type': "rgbdriver"
        },
        'led1': {
            'name': "LED Light strip",
            'key': 'led1',
            'driver': SingleLEDDriver(3),
            'type': "leddriver"
        },
        'therm': {
            'name': "Heat",
            'key': 'therm',
            'driver': Thermostat(18, 4, 55),
            'type': "thermostat"
        }
    }

thermostat = targets['therm']['driver']
thermostat_thread = thermostat.run()
thermostat_thread.start()

def sig_handler(signal, frame):
    print
    for target in targets:
        targets[target]['driver'].off()
    print("Waiting for Thermostat to finish.")
    thermostat_thread.join()
    sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

@get('/')
def index():
    context = targets
    for key, item in context.items():
        driver_type = type(item['driver'])
        item['val'] = item['driver'].get()
        if driver_type == Thermostat:
            item['time'] = item['driver'].get_last_time()
            item['target'] = item['driver'].get_target()
        elif driver_type == RGBDriver:
            item['hsv'] = colorsys.rgb_to_hsv(
                    item['val'][0] / 255,
                    item['val'][1] / 255,
                    item['val'][2] / 255
                )
    return template('templates/therm', ctx=context)

@get('/rgb')
def rgb():
    context = targets
    for key, item in context.items():
        driver_type = type(item['driver'])
        item['val'] = item['driver'].get()
        if driver_type == Thermostat:
            item['time'] = item['driver'].get_last_time()
            item['target'] = item['driver'].get_target()
        elif driver_type == RGBDriver:
            item['hsv'] = colorsys.rgb_to_hsv(
                    item['val'][0] / 255,
                    item['val'][1] / 255,
                    item['val'][2] / 255
                )
    return template('templates/rgb', ctx=context)

@get('/control', apply=[websocket])
def control(ws):
    while True:
        message = ws.receive()
        if message:
            print "Recieved message: " + message
            data = json.loads(message)
            driver = None
            if u'target' in data:
                driver = targets[str(data[u'target'])]['driver']
                driver_type = type(driver)
                action = data[u'action']
                if action == 'set':
                    if driver_type == RGBDriver:
                        f = str(data[u'format'])
                        c = [0, 0, 0]
                        if f == 'hls':
                            c = colorsys.hls_to_rgb(
                                    data[u'val'][0],
                                    data[u'val'][1],
                                    data[u'val'][2]
                                )
                        elif f == 'hsl':
                            c = colorsys.hls_to_rgb(
                                    data[u'val'][0],
                                    data[u'val'][2],
                                    data[u'val'][1]
                                )
                        elif f == 'hsv':
                            c = colorsys.hsv_to_rgb(
                                    data[u'val'][0],
                                    data[u'val'][1],
                                    data[u'val'][2]
                                )
                        elif f == 'rgb':
                            c = data[u'val']
                        driver.set_rgb(c)
                    else:
                        driver.set(data[u'val'])
                elif action == 'get':
                    ret = {}
                    ret['action'] = 'get'
                    if driver_type == RGBDriver:
                        f = str(data[u'format'])
                        c = driver.get()
                        if f == 'hsl':
                            ret['val'] = colorsys.rgb_to_hsl(
                                    c[0],
                                    c[1],
                                    c[2]
                                )
                        elif f == 'hsv':
                            ret['val'] = colorsys.rgb_to_hsv(
                                    c[0],
                                    c[1],
                                    c[2]
                                )
                        elif f == 'rgb':
                            ret['val'] = c
                        ret['format'] = f
                    else:
                        ret['val'] = driver.get()
                    ws.send(json.dumps(ret))
                    print("Sent message: " + json.dumps(ret))
                elif action == 'off':
                    driver.off()
        else:
            break

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')


"""
API
"""

@get('/api/<target>')
@get('/api/<target>/')
def get_current(target):
    ret = {}
    if target in targets:
        driver = targets[target]['driver']
        response.content_type = 'application/json'
        ret['val'] = driver.get()
        driver_type = type(driver)
        if driver_type == Thermostat:
            ret['time'] = driver.get_last_time()
    else:
        response.status = 404

    return json.dumps(ret)

@get('/api/<target>/target')
@get('/api/<target>/target/')
def get_target(target):
    ret = {}
    if target in targets:
        driver = targets[target]['driver']
        response.content_type = 'application/json'
        driver_type = type(driver)
        if driver_type == Thermostat:
            ret['val'] = driver.get_target()
        else:
            response.status = 404
    else:
        response.status = 404

    return json.dumps(ret)

@post('/api/<target>')
@post('/api/<target>/')
def set_target(target):
    ret = {}
    if target in targets:
        driver = targets[target]['driver']
        response.content_type = 'application/json'
        data = json.loads(request.body.read())
        val = data[u'val']
        driver.set(val)
        ret['status'] = 'ok'
    else:
        ret['status'] = 'fail'
        response.status = 404

    return json.dumps(ret)

debug(True)
run(host='0.0.0.0', port=8080, server=GeventWebSocketServer)
