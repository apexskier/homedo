import json, signal, sys, os
import bottle
from bottle import request, response, route, template, get, post, static_file, debug, view
from bottle.ext.websocket import GeventWebSocketServer, websocket
from beaker.middleware import SessionMiddleware
from cork import Cork
import datetime, colorsys
import private

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

app = bottle.app()
app = SessionMiddleware(app, private.session_opts)

aaa = Cork('conf')
authorize = aaa.make_auth_decorator(fail_redirect="/login", role="user")

def sig_handler(signal, frame):
    print
    for target in targets:
        targets[target]['driver'].off()
    print("Waiting for Thermostat to finish.")
    thermostat_thread.join()
    sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

def post_get(name, default=''):
    return request.POST.get(name, default).strip()

def postd():
    return request.forms

"""""""""
App Pages
"""""""""

@get('/')
@authorize()
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
    return template('views/therm', ctx=context)

@get('/rgb')
@authorize()
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
    return template('views/rgb', ctx=context)

@get('/control', apply=[websocket])
@authorize()
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

@route('/login')
@view('login')
def login_form():
    """Serve login form"""
    return {}

@post('/login')
def login():
    """Authenticate users"""
    username = post_get('username')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/', fail_redirect='/login')

@route('/logout')
def logout():
    aaa.logout(success_redirect='/login')


"""""
Admin
"""""
@route('/admin')
@authorize(role="admin", fail_redirect='/login')
@view('admin_page')
def admin():
    """Only admin users can see this"""
    aaa.require(role='admin', fail_redirect='/login')
    return dict(
            current_user = aaa.current_user,
            users = aaa.list_users(),
            roles = aaa.list_roles()
        )

@authorize(role="admin", fail_redirect='/login')
@post('/create_user')
def create_user():
    try:
        aaa.create_user(postd().username, postd().role, postd().password)
        return dict(ok=True, msg='')
    except Exception as e:
        return dict(ok=False, msg=e.message)

@post('/delete_user')
@authorize(role="admin", fail_redirect='/login')
def delete_user():
    try:
        aaa.delete_user(post_get('username'))
        return dict(ok=True, msg='')
    except Exception as e:
        print (repr(e))
        return dict(ok=False, msg=e.message)


"""
API
"""

@get('/api/<target>')
@get('/api/<target>/')
@authorize()
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
@authorize()
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
@authorize()
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
bottle.run(host='0.0.0.0', app=app, port=8080, server=GeventWebSocketServer)
