from faster_whisper import WhisperModel, BatchedInferencePipeline

class AudioTranscriber:

    def __init__(self, model_size = "large-v3", device="cuda", compute_type="float16"):
        self.model_size = "large-v3"
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        self.batched_model = BatchedInferencePipeline(model=self.model)

    def transcribe(self, audio_data, beam_size=5):
        return self.batched_model.transcribe(audio_data, beam_size=beam_size)
    