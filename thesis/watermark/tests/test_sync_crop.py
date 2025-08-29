import numpy as np
import scipy.io.wavfile as wavfile
import os
import pytest
from pathlib import Path

# Add the parent directory to the sys.path to allow imports of encode, decode, etc.
import sys
sys.path.append(str(Path(__file__).parent.parent))

from encode import encode_file
from decode import decode_file
from crypto import load_key
import params

@pytest.fixture(scope="module")
def secret_key():
    # Create a dummy secret key for testing
    key_dir = Path("/tmp/test_secrets")
    key_dir.mkdir(exist_ok=True)
    key_path = key_dir / "aead_key"
    if not key_path.exists():
        with open(key_path, "wb") as f:
            f.write(os.urandom(32))
    # Set the environment variable for load_key
    os.environ["AEAD_KEY_PATH"] = str(key_path)
    return load_key(str(key_path))

@pytest.fixture
def audio_file(tmp_path):
    sr = params.SR
    t = np.linspace(0, 5, 5 * sr, endpoint=False)
    data = (0.2 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    file_path = tmp_path / "test.wav"
    wavfile.write(file_path, sr, data)
    return str(file_path)

def test_sync_after_crop(audio_file, secret_key, tmp_path):
    track_id = 123
    
    # 1. Encode the original file
    encode_file(audio_file, secret_key, track_id)
    
    # 2. Create a cropped version
    sr, data = wavfile.read(audio_file)
    crop_seconds = 2
    crop_samples = int(crop_seconds * sr)
    cropped_data = data[crop_samples:]
    
    cropped_file_path = tmp_path / "cropped.wav"
    wavfile.write(cropped_file_path, sr, cropped_data)
    
    # 3. Decode the cropped file
    windows, stats = decode_file(str(cropped_file_path), secret_key, track_id)
    
    # 4. Assertions
    assert len(windows) > 0, "Decoder should find a watermark in the cropped file"
    
    max_lock_time_ms = (params.HOP / params.SR) * 1000 * 5 # Allow 5 frames to lock
    assert windows[0]["start_ms"] < max_lock_time_ms, f"Decoder should relock quickly, but took {windows[0]['start_ms']}ms"