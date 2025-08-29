import numpy as np
import scipy.io.wavfile as wavfile

# Define the duration of each watermark window in seconds
WATERMARK_WINDOW_DURATION_SEC = 5

# Define a magic number to identify embedded watermarks
MAGIC_NUMBER = 10000 # A distinct int16 value

# Number of samples used to embed a 64-bit integer (8 bits per sample)
# Not used in this simplified version, but kept for context
SAMPLES_PER_64BIT_INT = 8

# Multiplier to scale 8-bit parts to a larger range within int16
# Not used in this simplified version, but kept for context
MULTIPLIER = 128

def encode_file(file_path, watermark_id):
    """
    Minimal placeholder for audio encoding logic.
    Takes a WAV file path and a 64-bit watermark ID (integer).
    Embeds a magic number and the ID at the beginning of every 5-second chunk.
    This is NOT a real spread-spectrum encoder.
    """
    sample_rate, data = wavfile.read(file_path)

    # Ensure data is writable
    if data.flags['WRITEABLE'] == False:
        data = data.copy()

    # Calculate chunk size in samples
    chunk_size_samples = int(WATERMARK_WINDOW_DURATION_SEC * sample_rate)

    # Iterate through the audio data in chunks and embed the ID
    for i in range(0, len(data), chunk_size_samples):
        # Need at least 2 samples for embedding (1 for magic, 1 for ID)
        if len(data[i:]) < 2:
            continue

        # Embed magic number
        if data.ndim > 1:  # Stereo
            data[i, 0] = MAGIC_NUMBER
            data[i, 1] = MAGIC_NUMBER
        else:  # Mono
            data[i] = MAGIC_NUMBER

        # Embed watermark ID
        if data.ndim > 1:  # Stereo
            data[i + 1, 0] = watermark_id
            data[i + 1, 1] = watermark_id
        else:  # Mono
            data[i + 1] = watermark_id

    wavfile.write(file_path, sample_rate, data)

    # Debugging: Read back and print samples
    _, debug_data = wavfile.read(file_path)
    print(f"\n--- Debugging encode.py for {file_path} ---")
    for i in range(0, len(debug_data), chunk_size_samples):
        if len(debug_data[i:]) < 2:
            continue
        print(f"Chunk start: {i}, Magic: {debug_data[i, 0] if debug_data.ndim > 1 else debug_data[i]}, ID: {debug_data[i+1, 0] if debug_data.ndim > 1 else debug_data[i+1]}")
    print(f"--- End debugging encode.py ---")

    return file_path
