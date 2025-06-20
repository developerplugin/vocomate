#srcipt/clone_voice
import os
from openvoice.api import ToneColorConverter
from openvoice import se_extractor

def clone_voice(
    base_audio_path="../vocomate_app/assets/cloned_outputs/base.wav",
    reference_audio_path="../vocomate_app/assets/audio_inputs/my_voic.wav",
    output_path="../vocomate_app/assets/cloned_outputs/final_cloned.wav",
    config_path="../OpenVoice/openvoice/checkpoints_v2/converter/config.json",
    checkpoint_path="../OpenVoice/openvoice/checkpoints_v2/converter/checkpoint.pth"
):
      # Resolve paths relative to this script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_audio_path = os.path.abspath(os.path.join(base_dir, base_audio_path))
    reference_audio_path = os.path.abspath(os.path.join(base_dir, reference_audio_path))
    output_path = os.path.abspath(os.path.join(base_dir, output_path))
    config_path = os.path.abspath(os.path.join(base_dir, config_path))
    checkpoint_path = os.path.abspath(os.path.join(base_dir, checkpoint_path))

    print("Base audio:", base_audio_path)
    print("Reference audio:", reference_audio_path)
    print("Output path:", output_path)
    print("Config path:", config_path)
    print("Checkpoint path:", checkpoint_path)

    # Check if files exist
    for path, label in [
        (base_audio_path, "Base audio"),
        (reference_audio_path, "Reference audio"),
        (config_path, "Config file"),
        (checkpoint_path, "Checkpoint file")
    ]:
        if not os.path.exists(path):
            print(f"❌ {label} not found: {path}")
            return

    # Create output folder if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # Initialize converter on CPU
        print("Loading ToneColorConverter...")
        converter = ToneColorConverter(config_path=config_path, device="cpu")
        converter.load_ckpt(checkpoint_path)

        # Extract speaker embeddings
        print("Extracting source speaker embedding...")
        source_se = se_extractor.get_se(base_audio_path, converter, vad=True)
        if isinstance(source_se, tuple):
            source_se = source_se[0]

        print("Extracting target speaker embedding...")
        target_se = se_extractor.get_se(reference_audio_path, converter, vad=True)
        if isinstance(target_se, tuple):
            target_se = target_se[0]

        # Perform the voice cloning
        print("Converting voice...")
        converter.convert(
            audio_src_path=base_audio_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=output_path,
            message="@MyShell"  # Optional watermark, can be omitted
        )
        print(f"\n✅ Cloned speech saved to: {output_path}")
        return os.path.abspath(output_path)
    except Exception as e:
        print(f"❌ Error during voice cloning: {e}")