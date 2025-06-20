#llm_to_cloned_to_voice
import os
import sys
import sounddevice as sd
import soundfile as sf

# --- Adjust sys.path for custom modules ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add ASR and LLM module paths
sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'vocomate_app', 'asr')))
sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'vocomate_app', 'llm')))

from whisper_asr import transcribe_audio           # Your custom ASR module
from ollama_client import query_ollama            # Your custom LLM client

# MeloTTS and OpenVoice imports
from melo.api import TTS
from openvoice.api import ToneColorConverter
from openvoice import se_extractor

# --- Configuration ---
LLM_MODEL = "mistral"
LANGUAGE = "EN"
SPEAKER = "EN-Default"  # Change to your preferred accent if needed

BASE_AUDIO_PATH = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..', 'vocomate_app', 'assets', 'cloned_outputs', 'base.wav'
))
CLONED_AUDIO_PATH = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..','vocomate_app', 'assets', 'cloned_outputs', 'final_cloned.wav'
))
REFERENCE_AUDIO_PATH = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..','vocomate_app', 'assets', 'audio_inputs', 'my_voic.wav'
))
OPENVOICE_CONFIG = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..','OpenVoice', 'openvoice', 'checkpoints_v2', 'converter', 'config.json'
))
OPENVOICE_CKPT = os.path.abspath(os.path.join(
    SCRIPT_DIR, '..','OpenVoice', 'openvoice', 'checkpoints_v2', 'converter', 'checkpoint.pth'
))
print("Config path:", OPENVOICE_CONFIG)

def generate_base_speech(text, output_path=BASE_AUDIO_PATH, language=LANGUAGE, speaker=SPEAKER, speed=1.0):
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    tts = TTS(language=language, device="auto")
    speaker_ids = tts.hps.data.spk2id
    # --- FIXED SPEAKER SELECTION ---
    if speaker in speaker_ids:
        speaker_id = speaker_ids[speaker]
    else:
        print(f"Speaker '{speaker}' not found. Using first available speaker: {list(speaker_ids.keys())[0]}")
        speaker_id = list(speaker_ids.values())[0]
    tts.tts_to_file(
        text=text,
        speaker_id=speaker_id,
        output_path=output_path,
        speed=speed
    )
    print(f"Base speech generated at: {os.path.abspath(output_path)}")
    return os.path.abspath(output_path)

def clone_voice(
    base_audio_path=BASE_AUDIO_PATH,
    reference_audio_path=REFERENCE_AUDIO_PATH,
    output_path=CLONED_AUDIO_PATH,
    config_path=OPENVOICE_CONFIG,
    checkpoint_path=OPENVOICE_CKPT
):
    converter = ToneColorConverter(config_path=config_path, device="cpu")
    converter.load_ckpt(checkpoint_path)
    source_se = se_extractor.get_se(base_audio_path, converter, vad=True)
    if isinstance(source_se, tuple): source_se = source_se[0]
    target_se = se_extractor.get_se(reference_audio_path, converter, vad=True)
    if isinstance(target_se, tuple): target_se = target_se[0]
    converter.convert(
        audio_src_path=base_audio_path,
        src_se=source_se,
        tgt_se=target_se,
        output_path=output_path,
        message="@MyShell"
    )
    print(f"✅ Cloned speech saved at: {output_path}")
    return output_path

def play_audio(file_path):
    data, samplerate = sf.read(file_path)
    sd.play(data, samplerate)
    sd.wait()  # Wait until playback is finished
    print(f"Played audio: {file_path}")

if __name__ == "__main__":
    # 1. Get user input (simulate ASR/LLM pipeline)
    user_text = input("Type user prompt (or paste ASR/LLM text): ")
    llm_response = query_ollama(user_text, model=LLM_MODEL)
    print("LLM Response:", llm_response)

    # 2. Generate base speech with MeloTTS
    base_audio = generate_base_speech(llm_response)

    # 3. Clone the base speech into your own voice with OpenVoice
    cloned_audio = clone_voice(base_audio_path=base_audio)

    # 4. Play the cloned audio output automatically
    play_audio(cloned_audio)
