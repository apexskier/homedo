import pyaudio
from array import array
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
MAX_RECORD_SECONDS = 10
RUNNING = True
DEBUG = True
API = 'http://10.0.1.201:8080/api'
WIT_KEY = '7GGCVISTK6EGJMNKE2KC7MPVNLANXSLI'

p = pyaudio.PyAudio()

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
    m = 0

    while True:
        try:
            data = stream.read(CHUNK)
        except IOError:
            break
        print(max((array('h', data))))

    if DEBUG: print("* processing")
    else: print("----")

    stream.stop_stream()
    stream.close()

p.terminate()

