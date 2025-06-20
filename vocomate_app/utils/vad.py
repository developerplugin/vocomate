import torch
import numpy as np
import soundfile as sf

# Load Silero VAD model and utils once at import time
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False  # Set to True to force a fresh download
)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

def load_audio(audio_path, target_sr=16000):
    # Use Silero's read_audio for best compatibility
    audio = read_audio(audio_path, sampling_rate=target_sr)
    return audio, target_sr

def get_speech_timestamps_vad(audio_path, threshold=0.5, min_speech_duration_ms=250, min_silence_duration_ms=100):
    audio, sr = load_audio(audio_path)
    speech_timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=sr,
        threshold=threshold,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms
    )
    return speech_timestamps

def has_speech(audio_path, threshold=0.5):
    speech_timestamps = get_speech_timestamps_vad(audio_path, threshold=threshold)
    return len(speech_timestamps) > 0

def trim_silence(audio_path, output_path=None, threshold=0.5):
    audio, sr = load_audio(audio_path)
    speech_timestamps = get_speech_timestamps(
        audio,
        model,
        sampling_rate=sr,
        threshold=threshold
    )
    if not speech_timestamps:
        return None
    # Concatenate all speech segments
    speech_audio = np.concatenate([audio[t['start']:t['end']] for t in speech_timestamps])
    if output_path:
        sf.write(output_path, speech_audio, sr)
        return output_path
    return speech_audio
