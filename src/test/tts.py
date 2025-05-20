import io
import pygame # type: ignore
from gtts import gTTS # type: ignore

class Text_to_speech:
    def __init__(self, lang_list):
        self.lang_list = lang_list
        self.lang_map = {
            "italiano": "it",
            "inglese": "en",
            "francese": "fr",
            "spagnolo": "es",
            "tedesco": "de"
        }

    def speak(self, text, lang="it"):
        # Genera l'audio con gTTS
        tts = gTTS(text=text, lang=lang)
        
        # Salva il file in un buffer di memoria
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)  # Riporta il cursore all'inizio

        # Inizializza pygame per la riproduzione
        pygame.mixer.init()
        pygame.mixer.music.load(audio_buffer, "mp3")  # Carica il buffer come mp3
        pygame.mixer.music.play()

        # Aspetta che l'audio finisca
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
    def get_lang(self, text):
        for name in self.lang_list:
            if text in name:
                lang = name.get(text)
                return self.lang_map.get(lang)

        return "it"
