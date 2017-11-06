import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
sys.path.append("/Library/Python/2.7/site-packages")

from Tkinter import *

import essentia
import essentia.standard as es
from essentia.standard import *

import SpeakerRecognition
from SpeakerRecognition import *

from ctypes import *

ll = cdll.LoadLibrary
lib = ll('./libpycall.so')

class Handler:
    _KEY = "02261f80b2ce4e6fb164c2dba89ff6bd"
    _TEMP_FILE_NAME = "tempfile.wav"
    recognizer = None
    record = []
    last = '00000000-0000-0000-0000-000000000000'#-1
    num = 0

    count = 0
    parent = None

    def __init__(self, p):
        self.recognizer = SpeakerRecognitionClient(self._KEY)
	self.parent = p

    def add_profile(self, locale, file_path):
        pid = self.recognizer.create_profile(locale)
        self.recognizer.enroll_profile(pid, file_path)
        return pid

    def parser(self, path):
        audio = es.MonoLoader(filename=path, sampleRate=16000)()
        newaudio = []
        listaudio = audio.tolist()
        audio_list = []

        num = 0
        temprecord = []

        isLast = False
        i = 0

        for frame in es.FrameGenerator(audio):
            c = es.Loudness()(frame)
            #c = es.InstantPower()(frame)
            if c >= 0.00001:
            #if c >= 0.00001:
                flag = False
                if num <= 20 and len(temprecord) != 0:
                    if len(audio_list) != 0:
                        newaudio = newaudio + temprecord
                        flag = True

                if isLast or flag:
                    newaudio = newaudio + listaudio[(512 * i + 512):(512 * i + 1024)]
                else:
                    newaudio = newaudio + listaudio[(512 * i):(512 * i + 1024)]

                num = 0
                temprecord = []
                isLast = True
            else:
                num = num + 1

                temprecord = temprecord + listaudio[(512 * i + 512):(512 * i + 1024)]
                isLast = False

                if num == 21:
                    print(len(newaudio))
                    if len(newaudio) >= 16000:
                        audio_list.append(newaudio)
                    newaudio = []

            i = i + 1

        if len(newaudio) >= 16000:
            audio_list.append(newaudio)

        return audio_list

    def recognize(self, audio_list):
        print("len")
        print(len(audio_list))
        for audio in audio_list:
            #newaudio = es.Resample(outputSampleRate=16000)(audio)
            #es.MonoWriter(filename=self._TEMP_FILE_NAME, sampleRate=16000)(newaudio)
            es.MonoWriter(filename=self._TEMP_FILE_NAME, sampleRate=16000)(audio)
            #name = str(self.count) + "test.wav"
            #self.count = self.count + 1
            #es.MonoWriter(filename=name, sampleRate=16000)(audio)
            voice = open(self._TEMP_FILE_NAME, "rb")
            result = self.recognizer.identify_speaker(voice)

	    data = ""

            if result != self.last and len(self.record) > 0:
                #oname = str(self.num) + "rec.wav"
                #es.MonoWriter(filename = oname, sampleRate=16000)(self.record)
                #self.num = self.num + 1
                oname = "onlinetemp.wav"
                es.MonoWriter(filename=oname, sampleRate=16000)(self.record)

                c_pBuf = create_string_buffer('', 10000)

                #temp = c_char('')
                #pi = POINTER(c_char)(temp)
                #lib.process(oname, byrihh(pi))
                #data = pi.content

                lib.process(oname, c_pBuf)
                data = string_at(c_pBuf)

		if len(data) > 0:
		    print(data)
                    s = self.parent.parent.nameDict[result][:-4] + ": " + data
                    self.writeToOutput(s)

                    self.record = []
		    self.record = self.record + audio
		    self.last = result
	    else:
            	self.record = self.record + audio
		self.last = result
            
	    print result

    def clear_end(self):
        print('enter clear_end')
        if len(self.record) != 0:
            oname = "onlinetemp.wav"
            es.MonoWriter(filename=oname, sampleRate=16000)(self.record)

            c_pBuf = create_string_buffer('', 10000)

            # temp = c_char('')
            # pi = POINTER(c_char)(temp)
            # lib.process(oname, byref(pi))
            # data = pi.content

            lib.process(oname, c_pBuf)
            data = string_at(c_pBuf)
	    
	    if len(data) == 0:
		return

	    print(data)
            s = self.parent.parent.nameDict[self.last][:-4] + ": " + data
            self.writeToOutput(s)

            self.num = self.num + 1
            self.record = []

    def handle(self, path):
        audio_list = self.parser(path)
        self.recognize(audio_list)

    def writeToOutput(self, res):
        print('enter writeToOutput')
        self.parent.outputToWindow(res + '\n')



