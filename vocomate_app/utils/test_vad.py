import soundfile as sf
from vad import detect_speech_segments

# Path to a test audio file (should be 16kHz mono WAV, ideally with speech and silence)
audio_path = "vocomate_app/assets/audio_inputs/my_voic.wav"

audio, sr = sf.read(audio_path)
segments, hop_size = detect_speech_segments(audio, sr, silence_ms=800)

print(f"Detected {len(segments)} speech segment(s):")
for i, (start, end) in enumerate(segments):
    start_time = start * hop_size / sr
    end_time = end * hop_size / sr
    print(f"Segment {i+1}: {start_time:.2f}s to {end_time:.2f}s")
