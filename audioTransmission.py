import asyncio
import json
import io
from websockets import serve
from websockets.sync.server import serve
import wave
import uuid
import base64
from event import Event

DEFAULT_PORT = 3001
DEFAULT_URI = "0.0.0.0"

class AudioReceiver:
    CLIENTS = set()
    CAPTURED_SETTINGS = {}

    def __init__(self, uri=DEFAULT_URI, port=DEFAULT_PORT):
        self.on_audio_built = Event()
        self.uri = uri
        self.port = port
        # self.thread = None

    def save_audio_frames_to_buffer(self, frames, channels: int, sample_width: int, frame_rate: float) -> io.BytesIO:
        # Join all frames into a bytes object
        audio_data = b''.join(frames)

        # write the data to an audio buffer
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(frame_rate)
            wf.writeframes(audio_data)
        
        # return to the start of the buffer
        audio_buffer.seek(0)

        return audio_buffer

    def handle_audio_transmission(self, websocket):
        try:
            # Add connection
            self.CLIENTS.add(websocket)

            for message in websocket:
                event = json.loads(message)

                if event["action"] == "start":
                    # Generate a unique id for storing audio information for the new transcription instance
                    id = str(uuid.uuid4())
                    
                    # Get audio information
                    channels = event["channels"]
                    sample_width = event["samplewidth"]
                    frame_rate = event["framerate"]

                    # Create an instance which tracks all data to be used in the transcription
                    self.CAPTURED_SETTINGS[id] = { "frames": [], "channels": channels, "samplewidth": sample_width, "framerate": frame_rate }                
                    

                    # Respond with the instance id so the client can send audio frames
                    websocket.send(json.dumps({
                            "action": "accepted",
                            "id": id
                            }))
                    
                    print("Transmission Started")
                    
                elif event["action"] == "end":
                    # Get the instance id
                    id = event["id"]

                    # Get all saved frame information
                    audio_details = self.CAPTURED_SETTINGS[id]
                    found_frames = audio_details["frames"]
                    channels = audio_details["channels"]
                    sample_width = audio_details["samplewidth"]
                    frame_rate = audio_details["framerate"]
                    
                    audio_buffer = self.save_audio_frames_to_buffer(frames=found_frames, channels=channels, sample_width=sample_width, frame_rate=frame_rate)
                    
                    self.on_audio_built(audio_buffer)

                    # Remove this instance once completed everything
                    self.CAPTURED_SETTINGS.pop(id)
                    print("Transmission ended")

                elif event["action"] == "update":
                    # Get all details from the event
                    found_frames = event["frames"]
                    id = event["id"] 

                    # Decode frames sent
                    decoded_frames = base64.b64decode(found_frames)

                    # Retrieve current settings
                    settings = self.CAPTURED_SETTINGS[id]
                    saved_frames = settings["frames"]
                    

                    # Add to the current frames and store the new ones
                    saved_frames.append(decoded_frames)
                    settings["frames"] = saved_frames
                    self.CAPTURED_SETTINGS[id] = settings
                    print("Transmission updated")
        finally:
            # Remove connection
            self.CLIENTS.remove(websocket)

    def run(self):
        with serve(self.handle_audio_transmission, self.uri, self.port, open_timeout=None, close_timeout=None) as server:
            server.serve_forever()

if __name__ == "__main__":
    AudioReceiver().run()