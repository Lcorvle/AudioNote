import sys
sys.path.append("/Users/louyk/miniconda2/lib/python2.7/site-packages")

import pyaudio
import wave


class Record:
    _chunk = 0
    _format = 0
    _channels = 0
    _rate = 0
    _record_seconds = 0
    p = None
    stream = None

    def __init__(self, chunk, f, channels, rate, record_seconds):
        self._chunk = chunk
        self._format = f
        self._channels = channels
        self._rate = rate
        self._record_seconds = record_seconds

    def prepare(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self._format,
                        channels=self._channels,
                        rate=self._rate,
                        input=True,
                        frames_per_buffer=self._chunk)

    def finish_record(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def exec_record(self):
        frames = []
        for i in range(0, int(self._rate / self._chunk * self._record_seconds)):
            data = self.stream.read(self._chunk, exception_on_overflow = False)
            frames.append(data)

        return frames, self.p.get_sample_size(self._format)
