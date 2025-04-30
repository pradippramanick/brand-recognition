import sounddevice as sd    # type: ignore

class MicKeepAlive:
    def __init__(self, samplerate=16000, channels=1):
        self.stream = sd.InputStream(
            samplerate=samplerate,
            channels=channels,
            callback=self._callback,
        )
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        pass  # non fa nulla, solo per tenerlo attivo

    def stop(self):
        self.stream.stop()
        self.stream.close()
