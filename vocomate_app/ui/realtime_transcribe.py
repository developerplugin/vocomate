import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np

st.set_page_config(page_title="Real-Time Speech-to-Text", page_icon="🎤")
st.title("🎤 Real-Time Speech-to-Text Demo")

st.markdown("""
This demo streams your microphone audio to the backend and displays a running transcript.
- Click **Start** to begin.
- Speak into your microphone.
- The transcript will update in real time.
""")

# --- Dummy ASR function (replace with your real ASR engine) ---
def dummy_asr(audio_chunk: np.ndarray) -> str:
    # For demonstration: just return a placeholder string.
    # Replace this with your ASR model (e.g., Whisper, DeepSpeech, AssemblyAI, etc.)
    return "[transcribed text]"

# --- Audio Processor for streamlit-webrtc ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.transcript = ""

    def recv(self, frame):
        # frame.to_ndarray() gives you the audio data as a numpy array
        audio = frame.to_ndarray()
        # Process audio chunk with your ASR
        text = dummy_asr(audio)
        self.transcript += f" {text}"
        return frame

    def get_transcript(self):
        return self.transcript.strip()

# --- Streamlit WebRTC streamer ---
ctx = webrtc_streamer(
    key="stt",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# --- Display the transcript in real time ---
if ctx.audio_processor:
    st.markdown("### Live Transcription")
    st.write(ctx.audio_processor.get_transcript())
