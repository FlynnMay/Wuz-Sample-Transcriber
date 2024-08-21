import io
from audioTranscriber import AudioTranscriber
import requests

class App:
    def __init__(self):
        self.transcriber = AudioTranscriber()

    def audio_built(self, audio_buffer: io.BytesIO):
        # transcribe the data for sending to wuz
        segments, info = self.transcriber.transcribe(audio_data=audio_buffer)
        transcription = ''.join(segment.text for segment in segments)
    
        # Send the data to Wuz
        requests.post('http://localhost:3000/api/message', json={ 'message': transcription })
