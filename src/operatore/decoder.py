import time

import torch
from scipy.io import wavfile

from my_pyctcdecode import build_ctcdecoder
import nemo.collections.asr as nemo_asr     # type: ignore
from jiwer import cer                       # type: ignore

class Decoder:
    def __init__(self, hotwords=[]):
        # Load pretrained model
        self.device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
        self.asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_it_quartznet15x5",map_location=self.device)

        # Hotwords
        self.hotwords_weight = 20.0
        self.brands = hotwords
        self.hotwords = []
        for brand in self.brands:
            self.hotwords.extend(brand.split(" "))
        print("Decoder hotwords:", self.hotwords)
        self.c = time.time()
    
    def decode(self, file_audio):
        self.asr_model.sample_rate = 16000

        #save file_audio to an wav file


        # Transcription: returns a Hypothesis objects
        hypotheses = self.asr_model.transcribe([file_audio], return_hypotheses=True, batch_size=1)

        # Estract logits from the first Hypothesis; Note: `alignments` contains logits [time, vocab_size]
        logits = hypotheses[0].alignments.cpu().numpy()  # Converts in NumPy array

        # Decoder building
        decoder = build_ctcdecoder(self.asr_model.decoder.vocabulary)

        # Decode whit hotwords
        result = decoder.decode(
            logits,
            hotwords=self.hotwords,
            hotword_weight=self.hotwords_weight,
            beam_width=150,
            beam_prune_logp=-40,
            token_min_logp=-14
        )
        wavfile.write('log' + result + str(self.c) + '.wav', 16000, file_audio)
        return result
    
    def post_correction(self, word):
        for brand in self.brands:
            if word == brand:
                return (word, 0.0)
        
        result = ""
        min_e = 10.0
        # Calculate CER for each brand
        for brand in self.brands:
            try:
                error = cer(word, brand)
            except Exception:
                print('Empty string')
                error = 1.0
            if error < min_e:
                min_e = error
                result = brand
        # Return the brand with the lower CER
        if result == "":
            result = word


        return result, min_e