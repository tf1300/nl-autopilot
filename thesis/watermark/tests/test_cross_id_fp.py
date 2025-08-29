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
def secret_keys():
    # Create two dummy secret keys for testing
    key_dir = Path("/tmp/test_secrets")
    key_dir.mkdir(exist_ok=True)
    key_path1 = key_dir / "aead_key1"
    key_path2 = key_dir / "aead_key2"
    if not key_path1.exists():
        with open(key_path1, "wb") as f:
            f.write(os.urandom(32))
    if not key_path2.exists():
        with open(key_path2, "wb") as f:
            f.write(os.urandom(32))
    return load_key(str(key_path1)), load_key(str(key_path2))

@pytest.fixture
def audio_file(tmp_path):
    sr = params.SR
    t = np.linspace(0, 5, 5 * sr, endpoint=False)
    data = (0.2 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    file_path = tmp_path / "test.wav"
    wavfile.write(file_path, sr, data)
    return str(file_path)

def test_cross_id_fp(audio_file, secret_keys):
    correct_secret, wrong_secret = secret_keys
    correct_track_id = 123
    wrong_track_id = 456
    
    # 1. Encode with correct key and track_id
    encode_file(audio_file, correct_secret, correct_track_id)
    
    # 2. Decode with wrong track_id
    windows_wrong_id, _ = decode_file(audio_file, correct_secret, wrong_track_id)
    assert len(windows_wrong_id) == 0, "Decoder should not find a watermark with the wrong track_id"
    
    # 3. Decode with wrong key
    windows_wrong_key, _ = decode_file(audio_file, wrong_secret, correct_track_id)
    assert len(windows_wrong_key) == 0, "Decoder should not find a watermark with the wrong secret key"