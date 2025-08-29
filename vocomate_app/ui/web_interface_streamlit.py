import streamlit as st
from streamlit_realtime_audio_recorder import audio_recorder
import os
import sys
import time
import tempfile
import logging
from pathlib import Path
import threading
import soundfile as sf
import sounddevice as sd

# Adjust sys.path to import your modules
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
if scripts_path not in sys.path:
    sys.path.append(scripts_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.vad import has_speech, trim_silence
from asr.whisper_asr import transcribe_audio
from llm.ollama_client import query_ollama
from base_speech import generate_base_speech
from clone_voice import clone_voice

# --- TTSPlayer class for threaded playback ---
class TTSPlayer:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = None

    def play(self, file_path):
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._play_audio, args=(file_path,))
        self.thread.start()

    def _play_audio(self, file_path):
        data, samplerate = sf.read(file_path)
        sd.play(data, samplerate)
        while sd.get_stream().active:
            if self.stop_event.is_set():
                sd.stop()
                break

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()

# --- Logging setup ---
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"voice_assistant_{time.strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Session state initialization ---
if 'state' not in st.session_state:
    st.session_state['state'] = "waiting"
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'tts_player' not in st.session_state:
    st.session_state['tts_player'] = TTSPlayer()
if 'tts_playing' not in st.session_state:
    st.session_state['tts_playing'] = False

debug_mode = st.checkbox("Enable Debug/Verbose Mode")

def add_turn(role, text):
    st.session_state['history'].append({"role": role, "text": text})

def log_and_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    latency = time.time() - start_time
    logger.info(f"{func.__name__} took {latency:.2f} seconds")
    return result, latency

# --- State Machine ---

# 1. WAITING: Show listening message and record audio with auto-stop on silence
if st.session_state['state'] == "waiting":
    st.markdown("🎤 **Click the button to start recording. Recording will auto-stop after a long pause (no double-tap needed).**")
    st.info("Recording will stop automatically after 1.8 seconds of silence, or you can click 'Stop'.")

    audio = audio_recorder(
        pause_threshold=2.0,    # seconds of silence to auto-stop
        sample_rate=16000,
        icon_size="2x",
        neutral_color="#6c757d",
        recording_color="#e63946",
        bg_color="#f1faee",
        text_color="#000000",
        icon_name="microphone",
        key="recorder_waiting"
    )

    if audio and audio['audio']:
        st.session_state['audio_bytes'] = audio['audio']
        st.session_state['tts_playing'] = False
        if 'cloned_audio' in st.session_state:
            del st.session_state['cloned_audio']
        st.session_state['state'] = "processing"
        st.rerun()

# 2. PROCESSING: Handle ASR, LLM, TTS, etc.
elif st.session_state['state'] == "processing" and st.session_state.get('audio_bytes'):
    st.markdown("⏳ **Processing your input...**")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(st.session_state['audio_bytes'])
        audio_path = tmp.name

    # --- VAD check: Only proceed if speech is detected ---
    if not has_speech(audio_path):
        st.warning("No speech detected in the recording. Please try again.")
        os.unlink(audio_path)
        st.session_state['audio_bytes'] = None
        st.session_state['state'] = "waiting"
        st.rerun()
    else:
        # (Optional) Trim silence for cleaner ASR input
        trimmed_audio_path = audio_path.replace(".wav", "_trimmed.wav")
        trimmed = trim_silence(audio_path, output_path=trimmed_audio_path)
        if trimmed:
            audio_for_asr = trimmed_audio_path
        else:
            audio_for_asr = audio_path  # fallback to original if trimming failed

        # --- Transcribe ---
        with st.spinner("Transcribing..."):
            transcription, latency_transcribe = log_and_time(transcribe_audio, audio_for_asr)
        add_turn("user", transcription)

        # --- Generate LLM Response ---
        with st.spinner("Generating response..."):
            prompt = "You are a helpful assistant. Answer all parts of the user's question.\n\n"
            for turn in st.session_state['history']:
                prompt += f"{turn['role'].capitalize()}: {turn['text']}\n"
            prompt += "Assistant:"
            response, latency_llm = log_and_time(query_ollama, prompt)
        add_turn("assistant", response)
        logger.info(f"LLM response: {response}")

        # --- Synthesize Speech ---
        with st.spinner("Synthesizing speech..."):
            base_audio = generate_base_speech(response, speed=0.85)
        if base_audio is None or not os.path.exists(base_audio):
            logger.error("Failed to generate base speech audio. Please check your TTS setup.")
            st.error("Failed to generate base speech audio. Please check your TTS setup.")
            st.session_state['state'] = "waiting"
            st.rerun()
        else:
            logger.info("Base speech audio generated successfully.")
            # --- Clone Voice ---
            with st.spinner("Cloning voice..."):
                cloned_audio, latency_tts = log_and_time(clone_voice, base_audio_path=base_audio)
            if cloned_audio is None or not os.path.exists(cloned_audio):
                logger.error("Voice cloning failed or output file not found.")
                st.error("Voice cloning failed or output file not found.")
                st.session_state['state'] = "waiting"
                st.rerun()
            else:
                logger.info("Voice cloning succeeded.")
                st.session_state['cloned_audio'] = cloned_audio
                st.session_state['latency_transcribe'] = latency_transcribe
                st.session_state['latency_llm'] = latency_llm
                st.session_state['latency_tts'] = latency_tts
                st.session_state['state'] = "speaking"
                st.rerun()

        # Clean up temp files
        os.unlink(audio_path)
        if trimmed and os.path.exists(trimmed_audio_path) and trimmed_audio_path != audio_path:
            os.unlink(trimmed_audio_path)
        st.session_state['audio_bytes'] = None

# 3. SPEAKING: Play TTS, allow interruption, then return to waiting
elif st.session_state['state'] == "speaking" and 'cloned_audio' in st.session_state:
    st.subheader("Conversation History")
    for turn in st.session_state['history']:
        st.markdown(f"**{turn['role'].capitalize()}:** {turn['text']}")

    st.subheader("Latest Response")
    st.write(st.session_state['history'][-1]["text"])

    st.markdown("🎤 **Click the button to interrupt and ask a new question.**")
    st.info("Recording will stop automatically after 1.8 seconds of silence, or you can click 'Stop'.")

    # Start threaded TTS playback only if not already playing
    if not st.session_state.get('tts_playing', False):
        st.session_state['tts_player'].play(st.session_state['cloned_audio'])
        st.session_state['tts_playing'] = True

    # Recorder for interruption
    audio = audio_recorder(
        pause_threshold=2.0,
        sample_rate=16000,
        icon_size="2x",
        neutral_color="#6c757d",
        recording_color="#e63946",
        bg_color="#f1faee",
        text_color="#000000",
        icon_name="microphone",
        key="recorder_speaking"
    )
    if audio and audio['audio']:
        # User interrupted: stop TTS, process new input
        st.session_state['tts_player'].stop()
        st.session_state['tts_playing'] = False
        st.session_state['audio_bytes'] = audio['audio']
        st.session_state['state'] = "processing"
        if 'cloned_audio' in st.session_state:
            del st.session_state['cloned_audio']
        st.rerun()
    else:
        # If playback finished naturally, reset for next turn
        if not st.session_state['tts_player'].thread.is_alive():
            st.session_state['tts_playing'] = False
            st.session_state['state'] = "waiting"
            if 'cloned_audio' in st.session_state:
                del st.session_state['cloned_audio']
            st.rerun()

    # Debug info (optional)
    if debug_mode:
        st.write("Transcription latency:", st.session_state.get('latency_transcribe', None))
        st.write("LLM latency:", st.session_state.get('latency_llm', None))
        st.write("TTS latency:", st.session_state.get('latency_tts', None))
        with open(log_file, "r") as f:
            logs = f.read()
        st.text_area("Logs", logs, height=200)

    # Optionally, clear latencies if you want (after leaving speaking state)
    if st.session_state['state'] != "speaking":
        st.session_state['latency_transcribe'] = None
        st.session_state['latency_llm'] = None
        st.session_state['latency_tts'] = None
