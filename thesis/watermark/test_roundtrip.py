import pytest
import os
import shutil
import numpy as np
import scipy.io.wavfile as wavfile

from encode import encode_audio_file
from decode import decode_audio_file
from audio_utils import mix_audio_files, concatenate_audio_files

# Define paths to original stem files
STEM_A_PATH = "/app/testdata/stemA.wav"
STEM_B_PATH = "/app/testdata/stemB.wav"

@pytest.fixture
def temp_wav_file(tmp_path):
    """Fixture to create a temporary WAV file for testing."""
    def _create_temp_wav(original_path, filename="temp_encoded.wav"):
        temp_path = tmp_path / filename
        shutil.copy(original_path, temp_path)
        return str(temp_path)
    return _create_temp_wav

def test_roundtrip_stemA(temp_wav_file):
    """Test encoding and decoding on stemA.wav."""
    original_id = 1  # A simple ID
    temp_file = temp_wav_file(STEM_A_PATH)

    encoded_file = encode_audio_file(temp_file, original_id)
    decoded_windows = decode_audio_file(encoded_file)

    assert len(decoded_windows) >= 1 # Expect at least one window
    decoded_id = int(decoded_windows[0]["source_id"])
    assert decoded_id == original_id

def test_roundtrip_stemB(temp_wav_file):
    """Test encoding and decoding on stemB.wav."""
    original_id = 2  # Another simple ID
    temp_file = temp_wav_file(STEM_B_PATH)

    encoded_file = encode_audio_file(temp_file, original_id)
    decoded_windows = decode_audio_file(encoded_file)

    assert len(decoded_windows) >= 1 # Expect at least one window
    decoded_id = int(decoded_windows[0]["source_id"])
    assert decoded_id == original_id

def test_property_concatenated_file(temp_wav_file, tmp_path):
    """Test decoding on a concatenated file, asserting expected IDs and window properties."""
    id_a = 1
    id_b = 2

    # Encode stemA and stemB with different IDs
    encoded_stem_a_path = temp_wav_file(STEM_A_PATH, "encoded_stemA.wav")
    encode_audio_file(encoded_stem_a_path, id_a)

    encoded_stem_b_path = temp_wav_file(STEM_B_PATH, "encoded_stemB.wav")
    encode_audio_file(encoded_stem_b_path, id_b)

    # Concatenate the encoded files
    concatenated_file_path = str(tmp_path / "concatenated.wav")
    concatenate_audio_files(encoded_stem_a_path, encoded_stem_b_path, concatenated_file_path)

    # Decode the concatenated file
    decoded_windows = decode_audio_file(concatenated_file_path)

    # Assertions:
    # Expect six windows, three for each original stem (12s stem / 5s chunk = 2.4 chunks, so 3 IDs per stem)
    assert len(decoded_windows) == 6

    # Check the first three windows (should correspond to stemA)
    assert int(decoded_windows[0]["source_id"]) == id_a
    assert decoded_windows[0]["start_ms"] == 0
    assert decoded_windows[0]["end_ms"] == 5000

    assert int(decoded_windows[1]["source_id"]) == id_a
    assert decoded_windows[1]["start_ms"] == 5000
    assert decoded_windows[1]["end_ms"] == 10000

    assert int(decoded_windows[2]["source_id"]) == id_a
    assert decoded_windows[2]["start_ms"] == 10000
    assert decoded_windows[2]["end_ms"] == 15000

    # Check the next three windows (should correspond to stemB)
    assert int(decoded_windows[3]["source_id"]) == id_b
    assert decoded_windows[3]["start_ms"] == 12000 # Start of stemB in concatenated file
    assert decoded_windows[3]["end_ms"] == 17000

    assert int(decoded_windows[4]["source_id"]) == id_b
    assert decoded_windows[4]["start_ms"] == 17000
    assert decoded_windows[4]["end_ms"] == 22000

    assert int(decoded_windows[5]["source_id"]) == id_b
    assert decoded_windows[5]["start_ms"] == 22000 # Start of stemB's 10s mark
    assert decoded_windows[5]["end_ms"] == 24000 # End of file

    # Verify monotonicity and non-overlapping (implied by start/end checks)
    # Verify correct totals (total duration)
    assert decoded_windows[5]["end_ms"] == (12 + 12) * 1000 # Total duration

