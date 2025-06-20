# ui/web_interface_gradio.py
import gradio as gr
import os
import sys

# Adjust sys.path to import your modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vocomate_app', 'asr')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vocomate_app', 'llm')))
from whisper_asr import transcribe_audio
from ollama_client import query_ollama
from scripts.llm_to_cloned_to_voice import generate_base_speech, clone_voice, play_audio

def process_audio(audio_path):
    # 1. Transcribe
    text = transcribe_audio(audio_path, language="en")
    # 2. LLM
    response = query_ollama(text)
    # 3. MeloTTS + OpenVoice
    base_audio = generate_base_speech(response)
    cloned_audio = clone_voice(base_audio_path=base_audio)
    # 4. Return (transcription, response, audio path for playback)
    return text, response, cloned_audio

iface = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(source="microphone", type="filepath"),
    outputs=["text", "text", "audio"],
    live=True,
    title="VoiceMate Agent"
)
iface.launch()
