from nemo.collections.asr.models import EncDecClassificationModel   # type: ignore
import torch                                                        # type: ignore
import numpy as np                                                  # type: ignore
from transformers import pipeline                                   # type: ignore
import pyaudio as pa
from decoder import Decoder
from tts import Text_to_speech
import time

# Audio parameters
SAMPLE_RATE         =   16000                   # Frequenza di campionamento
STEP                =   0.5                     # Durata del chunk in secondi
CHUNK_SIZE          =   int(SAMPLE_RATE * STEP) # Dimensione del chunk
CHANNELS            =   1                       # Canali
SILENCE_TOLERANCE   =   2                       # Numero massimo di chunk consecuitivi di silenzio in una frase
THRESHOLD           =   0.85                    # Soglia per individuare il parlato (probabilità)

class Vad:
    def __init__(self, listener, controller, brand_lang_list):
        brand_list = [list(brand.keys())[0] for brand in brand_lang_list]
        self.decoder = Decoder(brand_list)          # Per lo speech to text dei brand
        self.tts = Text_to_speech(brand_lang_list)  # Per il text to speech
        self.listener = listener                    # Per aggiornare lo stato della GUI
        self.controller = controller                # Per comunicare con il server

        # Load pretrained model from NeMo library in inference mode (not training mode)
        self.vad = EncDecClassificationModel.from_pretrained(model_name="vad_multilingual_marblenet")
        self.vad.eval()

        # Whisper
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-small",
            chunk_length_s=int(SAMPLE_RATE * STEP),
            device=device,
        )

        # PyAudio
        self.p = pa.PyAudio()

        self.stream = self.p.open(
            format=pa.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )

        self.running = True
        self.pause = False

    def listen(self):
        self.running = True
        self.pause = False
        self.stream.start_stream() 
        print('Listening')
        self.listener.on_waiting_keyword()

        is_talking      =   False   # Initialize boolean var to know if in the current chunk there's voice activity
        chunks          =   []      # Initialize array for collecting chunks
        silence_counter =   0       # Initialize conunter for consecutive silence chunck
        active          =   False   # Initialize boolean var to know if the activatation keyword was pronunced
        confirm_mode    =   False   # Initialize boolean var to know if the word spoken is a confirm or refuse word 

        try:
            while self.running:
                chunk = self.__analyze_chunk()
                
                was_talking = is_talking

                if not self.running:
                    break

                # Decide if there's voice activity
                if chunk["probabilities"][0, 1] > THRESHOLD:    # Compare the probability of voice (1) in the fisrt batch (0) with a threshold (soglia)
                    is_talking = True                           # Boolean var to know if there's voice activity
                    chunks.append(chunk["audio_data"])          # Append chunk to the list only if there's a speech
                    silence_counter = 0                         # Reset silence counter
                else:
                    silence_counter += 1                        # Increment silence counter
                    if silence_counter >= SILENCE_TOLERANCE:    # We consider the end of a phrase if there's more than silence tolerance chunks of silence
                        is_talking = False                      # Boolean var to know if there's voice activity

                if not self.running:
                    break
                
                # If there was a speech and now is over, decode the speech
                if ((not is_talking) & (was_talking)):
                    print('Speech is over')
                    if (len(chunks)>=2):
                        self.stream.stop_stream()
                        print("Stopped listening; I'm processing...")
                        self.listener.on_processing()

                        audio_array = np.array(np.concatenate(chunks) * 32767, dtype=np.int16)  # Join chunks into a NumPy array

                        if not self.running:
                            break

                        if (active):
                            try:
                                result = self.decoder.decode(audio_array)
                                result_corrected, cer = self.decoder.post_correction(result)

                                if result == "stop":
                                    active = False
                                elif cer < 0.5:
                                    self.listener.on_sent(result_corrected)
                                    self.tts.speak(result_corrected, self.tts.get_lang(result_corrected))

                                    self.controller.send(result_corrected)

                                    self.tts.speak("Inviato")
                                elif cer >= 0.5 and cer <= 0.7:
                                    self.tts.speak(result_corrected, self.tts.get_lang(result_corrected))
                                    print(int(time.time()))
                                    self.listener.on_asking_confirm()
                                    self.tts.speak("Dire 'conferma' o 'riprova'")

                                    confirm_mode = True
                                    active = False
                                    self.listener.on_listening_confirm()
                                elif cer > 0.7:
                                    self.tts.speak("Non sono sicuro, riprova")
                            except BaseException:
                                print("Eccezione")
                                active = False
                        else:
                            transcription = self.__transcribe_chunks(audio_array)   # Decode the speech with Whisper

                            if not self.running:
                                break

                            if(confirm_mode):
                                if 'conf' in transcription.lower():
                                    # Communication with server
                                    self.listener.on_sent(result_corrected)
                                    self.controller.send(result_corrected)

                                    self.tts.speak("Inviato")
                                
                                active = True 
                                confirm_mode = False
                            elif ('attiva' in transcription.lower()):
                                active = True

                        if not self.running:
                            break

                        self.stream.start_stream()
                        print('Listening...')

                        if not active and not confirm_mode:
                            self.listener.on_waiting_keyword()
                        elif active:
                            self.listener.on_listening()
                
                    # Reset chunks list
                    chunks = []
        
        except BaseException as e:
            print(f"Error: {e}")
        finally:
            if not self.pause:
                self.close()
            else:
                self.stream.stop_stream()
                print("Non in ascolto")

    def __analyze_chunk(self):
        # Read chunk audio
        audio_data = np.frombuffer(self.stream.read(CHUNK_SIZE), dtype=np.int16).astype(np.float32) / 32768.0
        # Check if audio_data is empty or total silence
        max_val = np.max(np.abs(audio_data))
        if audio_data.size == 0 or max_val == 0:
            print("come immaginavo")
            return {"probabilities": np.array([[1.0, 0.0]]), "audio_data": audio_data}  # Default: silence
        # Normalization
        audio_data = audio_data / max_val
        # Convert in PyTorch Tensor
        audio_tensor = torch.tensor(audio_data).unsqueeze(0).to(torch.float32)
        audio_length = torch.tensor([len(audio_data)], dtype=torch.int64)
        # Send chunck to VAD model
        logits = self.vad.forward(input_signal=audio_tensor, input_signal_length=audio_length)   # Get logits (raw prediction)
        # Convert logits into probabilities as bidimentional array
        # (row: batch; columns: the first class is the probability of silence and the second one is the probability of voice)
        probabilities = logits.softmax(dim=-1).detach().cpu().numpy()                       
        return {"probabilities": probabilities, "audio_data": audio_data}

    def __transcribe_chunks(self, audio_array):
        # Normalize audio_array
        audio_array_normalized = audio_array.astype(np.float32) / 32767
        # Create a dict with audio metadata
        input_features = {"array": audio_array_normalized, "sampling_rate": 16000}
        # Transcription with Whisper
        transcription = self.pipe(input_features, generate_kwargs={"language": "italian"})["text"]
        print(transcription)
        return transcription
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.p.terminate()
        print("Terminated")