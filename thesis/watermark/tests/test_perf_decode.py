import numpy as np
import scipy.io.wavfile as wavfile
import os
import pytest
from pathlib import Path
import time

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
    os.environ["AEAD_KEY_PATH"] = str(key_path)
    return load_key(str(key_path))

@pytest.fixture
def audio_file(tmp_path):
    # Create a 30-second audio file for performance testing
    sr = params.SR
    duration_s = 30
    t = np.linspace(0, duration_s, duration_s * sr, endpoint=False)
    data = (0.2 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    file_path = tmp_path / "perf_test.wav"
    wavfile.write(file_path, sr, data)
    return str(file_path)

def test_decode_performance(audio_file, secret_key):
    track_id = 456
    
    # 1. Encode the file
    encode_file(audio_file, secret_key, track_id)
    
    # 2. Run decoder multiple times to get performance stats
    num_runs = 10
    decode_times = []
    for _ in range(num_runs):
        start_time = time.time()
        decode_file(audio_file, secret_key, track_id)
        end_time = time.time()
        decode_times.append((end_time - start_time) * 1000) # in ms
        
    # 3. Assert on p99
    p99 = np.percentile(decode_times, 99)
    # TODO: Optimize decoding performance
    assert p99 < 25000, f"p99 decode time ({p99:.2f}ms) is above the 25000ms target"