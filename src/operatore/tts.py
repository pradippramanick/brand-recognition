import io

import numpy as np
import pygame # type: ignore
import scipy
from TTS.api import TTS
# python3 -m pip install TTS

class Text_to_speech:
    def __init__(self, lang_list):
        self.lang_list = lang_list
        pygame.mixer.init()
        self.lang_map = {
            "italiano": "it",
            "inglese": "en",
            "francese": "fr",
            "spagnolo": "es",
            "tedesco": "de"
        }
        self.lang2model = {
            'de': 'tts_models/de/thorsten/tacotron2-DDC',
            'it': 'tts_models/it/mai_female/glow-tts',
            'en': 'tts_models/en/ljspeech/tacotron2-DDC'
            # Fill this mapping with langauge-model pairs
        }
        self.tts = TTS(model_name=self.lang2model['it'])  # load the default model

        #preload the beep sound
        self.beep_player = pygame.mixer.Sound("audios/beep1.wav")

    def play_beep(self):
        """Play a beep sound to indicate an event."""
        self.beep_player.play() # Play the beep sound
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)

    def set_language(self,lang):
        if lang not in self.lang2model:
            print('Other languages are not implemented. Select from here')
            print(TTS().list_models())
        self.tts = TTS(model_name=self.lang2model[lang])

    def speak(self, text):
        # Initialize the langauge using set_language to avoid loading the model every time, making it faster
        # Genera l'audio con gTTS
        wav = np.array(self.tts.tts(text=text, speed=0.7))

        #todo Clip the audio to max 2seconds, sometimes EN modes halucinate and generates a long audio

        # Normalize and convert to 16-bit PCM
        wav_norm = wav * (32767 / max(0.01, np.max(np.abs(wav))))
        wav_int16 = wav_norm.astype(np.int16)

        # Write to a BytesIO buffer as WAV
        audio_buffer = io.BytesIO()
        scipy.io.wavfile.write(audio_buffer, self.tts.synthesizer.output_sample_rate, wav_int16)
        audio_buffer.seek(0)

        # Inizializza pygame per la riproduzione

        pygame.mixer.music.load(audio_buffer)  # WAV format works with buffer
        pygame.mixer.music.play()

        # Aspetta che l'audio finisca
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # todo set it to audio length + buffer 1 s
    
    def get_lang(self, text):
        for name in self.lang_list:
            if text in name:
                lang = name.get(text)
                return self.lang_map.get(lang)

        return "it"
