import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import time
import tempfile
import logging
from pathlib import Path
import soundfile as sf
import sounddevice as sd

# Adjust sys.path to import your modules
import sys

scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

if scripts_path not in sys.path:
    sys.path.append(scripts_path)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'asr')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'llm')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.vad import has_speech, trim_silence
from asr.whisper_asr import transcribe_audio
from llm.ollama_client import query_ollama
from base_speech import generate_base_speech
from clone_voice import clone_voice

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"voice_assistant_{time.strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_and_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    latency = time.time() - start_time
    logger.info(f"{func.__name__} took {latency:.2f} seconds")
    return result, latency

def play_audio(file_path):
    try:
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        sd.wait()
    except Exception as e:
        st.warning(f"Audio playback failed: {e}")
        logger.error(f"Audio playback failed: {e}")

st.title("VoiceMate Agent")
debug_mode = st.checkbox("Enable Debug/Verbose Mode")

# Audio recorder widget
audio_bytes = audio_recorder("Click to record", pause_threshold=2.0)

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    # --- VAD check: Only proceed if speech is detected ---
    if not has_speech(audio_path):
        st.warning("No speech detected in the recording. Please try again.")
        os.unlink(audio_path)
    else:
        # (Optional) Trim silence for cleaner ASR input
        trimmed_audio_path = audio_path.replace(".wav", "_trimmed.wav")
        trimmed = trim_silence(audio_path, output_path=trimmed_audio_path)
        if trimmed:
            audio_for_asr = trimmed_audio_path
        else:
            audio_for_asr = audio_path  # fallback to original if trimming failed

        with st.spinner("Transcribing..."):
            transcription, latency_transcribe = log_and_time(transcribe_audio, audio_for_asr)
        with st.spinner("Generating response..."):
            response, latency_llm = log_and_time(query_ollama, transcription)
        logger.info(f"LLM response: {response}")
        with st.spinner("Synthesizing speech..."):
            base_audio = generate_base_speech(response, speed=0.85)
        if base_audio is None or not os.path.exists(base_audio):
            logger.error("Failed to generate base speech audio. Please check your TTS setup.")
            st.error("Failed to generate base speech audio. Please check your TTS setup.")
        else:
            logger.info("Base speech audio generated successfully.")

        with st.spinner("Cloning voice..."):
            cloned_audio, latency_tts = log_and_time(clone_voice, base_audio_path=base_audio)
        if cloned_audio is None or not os.path.exists(cloned_audio):
            logger.error("Voice cloning failed or output file not found.")
            st.error("Voice cloning failed or output file not found.")
        else:
            logger.info("Voice cloning succeeded.")

        st.subheader("Transcription")
        st.write(transcription)
        st.subheader("Response")
        st.write(response)
        if cloned_audio and os.path.exists(cloned_audio):
            st.audio(cloned_audio, format="audio/wav", autoplay=True)
            #play_audio(cloned_audio)

        if debug_mode:
            st.write("Transcription latency:", latency_transcribe)
            st.write("LLM latency:", latency_llm)
            st.write("TTS latency:", latency_tts)
            with open(log_file, "r") as f:
                logs = f.read()
            st.text_area("Logs", logs, height=200)

        # Clean up temp files
        os.unlink(audio_path)
        if trimmed and os.path.exists(trimmed_audio_path) and trimmed_audio_path != audio_path:
            os.unlink(trimmed_audio_path)
