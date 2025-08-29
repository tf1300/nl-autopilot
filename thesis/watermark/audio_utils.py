import numpy as np
import scipy.io.wavfile as wavfile

def mix_audio_files(file1_path, file2_path, output_path):
    """
    Mixes two WAV audio files and saves the result to an output path.
    Assumes both files have the same sample rate and number of channels.
    If durations differ, the shorter file is padded with zeros.
    """
    sr1, data1 = wavfile.read(file1_path)
    sr2, data2 = wavfile.read(file2_path)

    if sr1 != sr2:
        raise ValueError("Sample rates of input files must be the same.")

    # Ensure data is float for mixing
    data1 = data1.astype(np.float64)
    data2 = data2.astype(np.float64)

    # Handle mono/stereo consistency
    if data1.ndim == 1 and data2.ndim == 2:
        data1 = np.expand_dims(data1, axis=1) # Convert mono to stereo-like (N, 1)
    elif data1.ndim == 2 and data2.ndim == 1:
        data2 = np.expand_dims(data2, axis=1) # Convert mono to stereo-like (N, 1)

    # Pad shorter audio with zeros
    max_len = max(len(data1), len(data2))
    if len(data1) < max_len:
        if data1.ndim == 2:
            padding = np.zeros((max_len - len(data1), data1.shape[1]), dtype=np.float64)
        else:
            padding = np.zeros(max_len - len(data1), dtype=np.float64)
        data1 = np.concatenate((data1, padding))
    elif len(data2) < max_len:
        if data2.ndim == 2:
            padding = np.zeros((max_len - len(data2), data2.shape[1]), dtype=np.float64)
        else:
            padding = np.zeros(max_len - len(data2), dtype=np.float64)
        data2 = np.concatenate((data2, padding))

    # Mix (sum) the audio data
    mixed_data = data1 + data2

    # Normalize to prevent clipping (optional, but good practice)
    # Find the maximum absolute value in the mixed data
    max_val = np.max(np.abs(mixed_data))
    if max_val > 0:
        mixed_data = mixed_data / max_val * (np.iinfo(np.int16).max * 0.9) # Scale to 90% of max int16

    # Convert back to int16 for saving
    mixed_data = mixed_data.astype(np.int16)

    wavfile.write(output_path, sr1, mixed_data)

    return output_path

def concatenate_audio_files(file1_path, file2_path, output_path):
    """
    Concatenates two WAV audio files and saves the result to an output path.
    Assumes both files have the same sample rate and number of channels.
    """
    sr1, data1 = wavfile.read(file1_path)
    sr2, data2 = wavfile.read(file2_path)

    if sr1 != sr2:
        raise ValueError("Sample rates of input files must be the same.")

    # Handle mono/stereo consistency
    if data1.ndim == 1 and data2.ndim == 2:
        data1 = np.expand_dims(data1, axis=1) # Convert mono to stereo-like (N, 1)
    elif data1.ndim == 2 and data2.ndim == 1:
        data2 = np.expand_dims(data2, axis=1) # Convert mono to stereo-like (N, 1)

    # Concatenate the audio data
    concatenated_data = np.concatenate((data1, data2))

    wavfile.write(output_path, sr1, concatenated_data)

    return output_path