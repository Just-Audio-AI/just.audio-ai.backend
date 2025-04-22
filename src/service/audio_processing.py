import subprocess
from pathlib import Path

RNNOISE_MODEL = "ai_models/std.rnnn"


def remove_noise(input_path: str) -> str:
    input_path = Path(input_path)
    output_path = input_path.with_name(input_path.stem + "_denoised.wav")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-af", f"arnndn=m={RNNOISE_MODEL}",
        str(output_path)
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Noise removal failed: {e.stderr.decode()}")
        raise RuntimeError("Noise removal failed")

    return str(output_path)
