#asr_to_llm
import os
import sys

# Adjust sys.path to import from your app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vocomate_app', 'asr')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vocomate_app', 'llm')))
from whisper_asr import transcribe_audio
from ollama_client import query_ollama

# Path to your audio file
audio_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'vocomate_app', 'assets', 'audio_inputs', 'my_voic.wav')
)

# Step 1: Transcribe audio
text = transcribe_audio(audio_path, language="en")
print("Transcribed:", text)

# Step 2: Send to LLM
response = query_ollama(text)
print("LLM Response:", response)
