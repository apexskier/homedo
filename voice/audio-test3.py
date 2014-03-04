import pyaudio
from array import array
import wave
import requests
import json

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
MAX_RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"
RUNNING = True
DEBUG = True
API = 'http://10.0.1.201:8080/api'
WIT_KEY = '7GGCVISTK6EGJMNKE2KC7MPVNLANXSLI'

p = pyaudio.PyAudio()
s = requests.Session()
s.post(
        API + '/login',
        allow_redirects=False,
        data={'username': 'cameron', 'password': 'kayak2010'}
    )

while RUNNING:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    if DEBUG: print("* listening")

    frames = []
    recording = False
    silent_time = 0

    for i in range(0, int(RATE / CHUNK * MAX_RECORD_SECONDS)):
        try:
            data = stream.read(CHUNK)
        except IOError:
            break
        if max((array('h', data))) > 1000:
            if not recording:
                if DEBUG: print("* recording")
                else: print("****")
            recording = True
            silent = 0
        elif recording:
            silent += 1
            if DEBUG: print('silent: ' + str(silent))
            if silent > 30:
                if DEBUG: print("* done recording")
                break
        if recording:
            if DEBUG: print(max((array('h', data))))
            frames.append(data)

    if DEBUG: print("* processing")
    else: print("----")

    stream.stop_stream()
    stream.close()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    rf = open(WAVE_OUTPUT_FILENAME, 'rb')
    d = rf.read()
    rf.close()

    r = requests.post('https://api.wit.ai/speech',
            data=d,
            headers={
                'content-type': 'audio/wave',
                'authorization': 'Bearer ' + WIT_KEY
            }
        )

    if r.status_code == 200:
        res = r.json()
        if float(str(res['outcome']['confidence'])) < 0.5:
            print("I may have heard: " + res['msg_body'])
        else:
            print("I heard: " + res['msg_body'])
            if res['outcome']['intent'] == 'quit':
                RUNNING = False
            elif res['outcome']['intent'] == 'get_temperature':
                nr = s.get(API + '/therm', allow_redirects=False)
                print("The temperature is " + str(nr.json()['val']) + " F.")
            elif res['outcome']['intent'] == 'set_temperature':
                if 'datetime' in res['outcome']['entities']:
                    print("I can't schedule yet.")
                elif 'temperature' in res['outcome']['entities']:
                    nr = s.post(
                            API + '/therm',
                            data=json.dumps({'val': res['outcome']['entities']['temperature']['value']['temperature']}),
                            headers={
                                'content-type': 'application/json'
                            },
                            allow_redirects=False
                        )
                    if nr.status_code == 202:
                        print("I've set the temperature to " + nr.json()['val'])
                    else:
                        if nr.status_code == "200":
                            print("You're not logged in.")
                        else:
                            print("Something went wrong.")
            elif res['outcome']['intent'] == 'turn_on':
                target = None
                if res['outcome']['entities']['target']['value'] == 'heat':
                    target = 'therm'
                if target:
                    nr = s.post(
                            API + '/' + target + '/up',
                            allow_redirects=False
                        )
                    if nr.status_code == 202:
                        print("I've turned the " + res['outcome']['entities']['target']['value'] + " on.")
                    else:
                        if nr.status_code == "200":
                            print("You're not logged in.")
                        else:
                            print("Something went wrong.")
            elif res['outcome']['intent'] == 'turn_off':
                target = None
                if res['outcome']['entities']['target']['value'] == 'heat':
                    target = 'therm'
                if target:
                    nr = s.post(
                            API + '/' + target + '/down',
                            allow_redirects=False
                        )
                    if nr.status_code == 202:
                        print("I've turned the " + res['outcome']['entities']['target']['value'] + " off.")
                    else:
                        if nr.status_code == "200":
                            print("You're not logged in.")
                        else:
                            print("Something went wrong.")

    elif DEBUG:
        print("Error: " + r.text)

p.terminate()
