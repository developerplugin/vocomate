# scripts/base_speech.py

import os
from melo.api import TTS

def generate_base_speech(
    text,
    output_path="assets/cloned_outputs/base.wav",
    language="EN",
    speaker="EN-Default",
    speed=1.0
):
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Initialize TTS engine
    tts = TTS(language=language, device="auto")

    # Get speaker ID (print available speakers for reference)
    speaker_ids = tts.hps.data.spk2id
    if speaker not in speaker_ids:
        print(f"Speaker '{speaker}' not found. Available speakers: {list(speaker_ids.keys())}")
        speaker_id = list(speaker_ids.values())[0]  # Use first available
    else:
        speaker_id = speaker_ids[speaker]

    # Synthesize speech to file
    try:
        tts.tts_to_file(
            text=text,
            speaker_id=speaker_id,
            output_path=output_path,
            speed=speed
        )
        print(f"Base speech generated and saved to: {os.path.abspath(output_path)}" )
        print("base_audio from generate_base_speech:")
        print("output_path from output_path:",output_path)
        return os.path.abspath(output_path)
    except Exception as e:
        print(f"Error generating base speech: {e}")
        return None