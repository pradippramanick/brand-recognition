from nemo.collections.asr.models import EncDecClassificationModel   # type: ignore
import torch                                                        # type: ignore
import numpy as np                                                  # type: ignore
from transformers import pipeline                                   # type: ignore
import pyaudio as pa
from decoder import Decoder
from tts import Text_to_speech

import time
import os
from scipy.io.wavfile import write  # type: ignore

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

        self._num = 0       # TEST
        self.folder = ""  # TEST

    def listen(self, operator_code):
        # TEST
        new_folder = f"log/{operator_code}"
        if self.folder != new_folder:
            self.folder = new_folder
            self._num = 0
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

        # TEST
        self.__write("START LISTEN")

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

                        # TEST
                        self.__save_audio(audio_array)
                        self.__write(f"SPEECH OVER - {int(time.time())}")

                        if not self.running:
                            break

                        if (active):
                            try:
                                start_time = time.perf_counter()
                                result = self.decoder.decode(audio_array)
                                result_corrected, cer = self.decoder.post_correction(result)
                                end_time = time.perf_counter()
                                elapsed_ms = (end_time - start_time) * 1000
                                print(f"Time taken for CTC decoder and post correction: {elapsed_ms:.2f} ms")

                                self.__write(f"DECODER: {result_corrected}, CER: {cer} - {int(time.time())}")    # TEST

                                if result == "stop":
                                    active = False
                                    self.__write(f"STOP - {int(time.time())}")    # TEST
                                elif cer < 0.5:
                                    self.__write(f"SEND START - {int(time.time())}")    # TEST
                                    self.listener.on_sent(result_corrected)
                                    self.tts.speak(result_corrected, self.tts.get_lang(result_corrected))

                                    self.controller.send(result_corrected)

                                    self.tts.speak("Inviato")
                                    self.__write(f"SEND END - {int(time.time())}")    # TEST
                                elif cer >= 0.5 and cer <= 0.7:
                                    self.__write(f"CONFIRM START - {int(time.time())}")    # TEST
                                    self.tts.speak(result_corrected, self.tts.get_lang(result_corrected))
                                    self.listener.on_asking_confirm()
                                    self.tts.speak("Dire 'conferma' o 'riprova'")

                                    confirm_mode = True
                                    active = False
                                    self.listener.on_listening_confirm()
                                elif cer > 0.7:
                                    self.tts.speak("Non sono sicuro, riprova")
                                    self.__write(f"TRY AGAIN - {int(time.time())}")    # TEST

                            except BaseException as e:
                                print(f"Error: {e}")
                                active = False
                        else:
                            transcription = self.__transcribe_chunks(audio_array)   # Decode the speech with Whisper
                            self.__write(f"WHISPER: {transcription} - {int(time.time())}")    # TEST

                            if not self.running:
                                break

                            if(confirm_mode):
                                if 'conf' in transcription.lower():
                                    self.__write(f"SEND START (after confirm) - {int(time.time())}")    # TEST
                                    # Communication with server
                                    self.listener.on_sent(result_corrected)
                                    self.controller.send(result_corrected)

                                    self.tts.speak("Inviato")
                                    self.__write(f"SEND END (after confirm) - {int(time.time())}")    # TEST
                                
                                active = True 
                                confirm_mode = False
                                self.__write(f"CONFIRM END - {int(time.time())}")    # TEST
                            elif ('attiva' in transcription.lower()):
                                active = True
                                self.__write(f"ACTIVE") # TEST

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
                self.__write(f"PAUSE - {int(time.time())}")    # TEST

    def __analyze_chunk(self):
        # Read chunk audio
        audio_data = np.frombuffer(self.stream.read(CHUNK_SIZE), dtype=np.int16).astype(np.float32) / 32768.0
        # Check if audio_data is empty or total silence
        max_val = np.max(np.abs(audio_data))
        if audio_data.size == 0 or max_val == 0:
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
        start_time = time.perf_counter()
        transcription = self.pipe(input_features, generate_kwargs={"language": "italian"})["text"]
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        print(f"Time taken for self.pipe(): {elapsed_ms:.2f} ms")
        print(transcription)

        return transcription
    
    def __save_audio(self, audio_array):    # TEST
        self._num += 1
        fileName = os.path.join(self.folder, f"audio_{self._num}.wav")
        write(fileName, SAMPLE_RATE, audio_array)  # Save NumPy array NumPy as file .wav

    def __write(self, text):                # TEST
        with open(f"{self.folder}/log.txt", "a") as file:
            file.write(f"{text}\n")
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.p.terminate()
        print("Terminated")
