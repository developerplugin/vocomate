import os
import whisper

def transcribe_audio(audio_path, model_size="base", language=None):
    """
    Transcribes the given audio file using OpenAI Whisper.

    Args:
        audio_path (str): Path to the audio file (wav, mp3, m4a, etc.)
        model_size (str): Whisper model size ("tiny", "base", "small", "medium", "large")
        language (str, optional): Language code (e.g., "en" for English)

    Returns:
        str: Transcribed text
    """
    print(f"Loading Whisper model ({model_size})...")
    model = whisper.load_model(model_size)
    print(f"Transcribing {audio_path}...")
    result = model.transcribe(audio_path, language=language) if language else model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    # Build the correct absolute path to the audio file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, '..', 'assets', 'audio_inputs', 'my_voic.wav')
    audio_path = os.path.abspath(audio_path)

    print("Audio file path:", audio_path)
    if not os.path.exists(audio_path):
        print(f"❌ File not found: {audio_path}")
    else:
        text = transcribe_audio(audio_path, language="en")
        print("Transcription:", text)
