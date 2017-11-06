import sys
sys.path.append("/Users/louyk/miniconda2/lib/python2.7/site-packages")

from Record import *
from Handler import *
import threading
from time import ctime, sleep
import wave
import pyaudio

class PreRecorder:
    _CHUNK = 8192
    _FORMAT = pyaudio.paInt16
    _CHANNELS = 1
    _RATE = 16000
    _RECORD_SECONDS = 1
    _OUTPUT_FILENAME = "output.wav"

    threads = []
    recorder = None
    handler = None
    frames = []
    sample_sizes = []
    isOn = True

    def __init__(self):
        self.recorder = Record(self._CHUNK, self._FORMAT, self._CHANNELS, self._RATE, self._RECORD_SECONDS)

    def pre_record(self):
        self.recorder.prepare()
        frs = []
        samp = 0

        while self.isOn:
            f, sz = self.recorder.exec_record()
            samp = sz
            frs = frs + f

        self.recorder.finish_record()
        return frs, samp

    def write_wave_file(self, frame, samplesize, filepath):
        wavfile = wave.open(filepath, 'wb')
        wavfile.setnchannels(self._CHANNELS)
        wavfile.setsampwidth(samplesize)
        wavfile.setframerate(self._RATE)
        wavfile.writeframes(b''.join(frame))
        wavfile.close()
