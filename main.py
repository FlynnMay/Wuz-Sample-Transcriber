from audioTransmission import AudioReceiver
from app import App
from websockets import serve

if __name__ == "__main__":
    app = App()
    receiver = AudioReceiver()
    receiver.on_audio_built += app.audio_built 
    receiver.run()
    

# Ideal app structure
# main.py 
#   |- Handle CLI
#   |   |- Update default values for the websocket and transcriber if any exist
#   |
#   |- Initiate App
#   |   |- Initiate Transcriber
#   |
#   |- Initiate Websocket  
# 
#  Websocket -> collect data and provide it to the app once completed
#  App 
#   |- wait for audio data (or get it from file) 
#   |- provide data to the transcriber
#   |- provide transcriptions to Wuz
#

# Define a standard way for sending audio through the websocket.
# process:
#
# Client -> Server:
# { 
#   "action": "start", 
#   "channels": 2,
#   "samplewidth": 2,
#   "framerate": 16000         
# }
#
# Server -> Client:
# { 
#   "action": "accepted"
#   "id": id_for_frame_transfer   
# }
#
# Client ->* Server:
# {
#   "action": "update",
#   "id": id_for_frame_transfer,
#   "frames": byte_array_of_frames
# }
# 
# Client -> Server:
# {
#   "action": "end"
#   "id": id_for_frame_transfer
# }
# 
# Server -> Client:
# {
#   "action": "completed"
#   "id": id_for_frame_transfer
# }