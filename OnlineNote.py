import sys
sys.path.append("/Users/louyk/miniconda2/lib/python2.7/site-packages")

from Record import *
from Handler import *
import threading
from time import ctime, sleep
import wave
import pyaudio

class OnlineNote:
    _CHUNK = 8192
    _FORMAT = pyaudio.paInt16
    _CHANNELS = 1
    _RATE = 16000
    _RECORD_SECONDS = 5
    _OUTPUT_FILENAME = "output.wav"

    threads = []
    recorder = None
    handler = None
    frames = []
    sample_sizes = []
    isOn = False

    lock = threading.Lock()
    parent = None

    def __init__(self, p):
        self.recorder = Record(self._CHUNK, self._FORMAT, self._CHANNELS, self._RATE, self._RECORD_SECONDS)
        self.parent = p
        self.handler = Handler(self)

    def outputToWindow(self, s):
        print('enter outputToWindow')
        self.parent.outputText.insert(END, s)
        print('leave outputToWindow')

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

    def recording(self):
        self.recorder.prepare()

        while self.isOn:
            print "recording......"
            f, sz = self.recorder.exec_record()

            self.lock.acquire()

            self.frames.append(f)
            self.sample_sizes.append(sz)

            self.lock.release()

        self.recorder.finish_record()

    def handling(self):
        while True:
            if len(self.frames) == 0:
                sleep(2)
		
	    	if (not self.isOn) and (len(self.frames) == 0):
               	    break
            	continue

            print "handling......"

            f = self.frames[0]
            ss = self.sample_sizes[0]

            self.lock.acquire()

            self.frames = self.frames[1:]
            self.sample_sizes = self.sample_sizes[1:]

            self.lock.release()

            self.write_wave_file(f, ss, self._OUTPUT_FILENAME)
            self.handler.handle(self._OUTPUT_FILENAME)

            if (not self.isOn) and (len(self.frames) == 0):
                break
        
        self.handler.clear_end()
        self.parent.changeModeButton.config(state=NORMAL)
        self.parent.exportButton.config(state=NORMAL)
        self.parent.filePathEntry.config(state=NORMAL)
        self.parent.fileChooseButton.config(state=NORMAL)
        self.parent.speakerNumberBox.config(state=NORMAL)
        self.parent.addSpeakerButton.config(state=NORMAL)
        self.parent.deleteSpeakerButton.config(state=NORMAL)
        self.parent.runButton.config(state=NORMAL)
        self.parent.runButton.config(text='run')

    def start_note(self):
        recordThread = threading.Thread(target=self.recording)
        self.threads.append(recordThread)

        handleThread = threading.Thread(target=self.handling)
        self.threads.append(handleThread)

        for t in self.threads:
            #t.setDaemon(True)
            t.start()

        #self.threads[0].join()
        #self.threads[1].join()

    def end_note(self):
        self.isOn = False
