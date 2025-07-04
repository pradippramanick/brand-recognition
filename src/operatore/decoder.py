import torch

from my_pyctcdecode import build_ctcdecoder
import nemo.collections.asr as nemo_asr     # type: ignore
from jiwer import cer                       # type: ignore

class Decoder:
    def __init__(self, hotwords=[]):
        # Load pretrained model
        self.device = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")
        self.asr_model = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="stt_it_quartznet15x5",map_location=self.device)

        # Hotwords
        self.hotwords_weight = 15.0
        self.hotwords = hotwords
    
    def decode(self, file_audio):
        self.asr_model.sample_rate = 16000
            
        # Transcription: returns an Hypotesis objects
        hypotheses = self.asr_model.transcribe([file_audio.to(self.device)], return_hypotheses=True, batch_size=1)

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
            beam_prune_logp=-45,
            token_min_logp=-40
        )

        return result
    
    def post_correction(self, word):
        for hotword in self.hotwords:
            if word == hotword:
                return (word, 0.0)
        
        result = ""
        min = 10.0
        # Calculate CER for each hotword
        for hotword in self.hotwords:
            error = cer(word, hotword)
            if (error < min):
                min = error
                result = hotword
        # Return the hotword with the lower CER
        if (result == ""):
            result = word
        return (result, min)