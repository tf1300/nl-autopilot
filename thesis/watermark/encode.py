import numpy as np
import scipy.io.wavfile as wavfile
import hmac
import hashlib
import struct
import params
from crypto import frame_tag

def frame_pn(secret, track_id: int, frame_idx: int, chips: int):
    msg = struct.pack(">QQ", track_id, frame_idx)
    digest = hmac.new(secret, msg, hashlib.sha256).digest()
    # expand to chips in {+1,-1}
    bits = []
    while len(bits) < chips:
        digest = hashlib.sha256(digest).digest()
        for b in digest:
            for i in range(8):
                bits.append(1 if (b >> i) & 1 else -1)
    return bits[:chips]

def tag_to_bits(tag):
    bits = []
    for byte in tag:
        for i in range(8):
            bits.append(1 if (byte >> i) & 1 else -1)
    return bits

def encode_file(file_path, secret, track_id):
    """
    Embeds a watermark into a WAV file using spread-spectrum modulation, including an HMAC tag.
    """
    sample_rate, data = wavfile.read(file_path)
    if sample_rate != params.SR:
        raise ValueError(f"Sample rate {sample_rate} not supported, expected {params.SR}")

    if data.dtype != np.float32:
        data = data.astype(np.float32) / 32767.0

    if data.ndim > 1:
        data = data[:, 0]

    num_samples = len(data)
    output_data = np.zeros_like(data)
    frame_idx = 0
    window = np.hanning(params.FRAME)
    
    total_chips = params.SYNC_CHIPS + params.TAG_BITS

    for i in range(0, num_samples - params.FRAME, params.HOP):
        frame = data[i : i + params.FRAME] * window

        fft_frame = np.fft.fft(frame)
        
        pn = frame_pn(secret, track_id, frame_idx, params.SYNC_CHIPS)
        tag = frame_tag(secret, track_id, frame_idx, pn, params.TAG_BITS)
        tag_bits = tag_to_bits(tag)
        
        payload = pn + tag_bits
        
        freqs = np.fft.fftfreq(params.FRAME, 1.0 / params.SR)
        band_indices = np.where((freqs >= params.BANDS[0]) & (freqs <= params.BANDS[1]))[0]
        
        if len(band_indices) < total_chips:
            raise ValueError("Not enough frequency bins in the selected band to embed the watermark payload.")

        for j in range(total_chips):
            idx = band_indices[j]
            fft_frame[idx] = (np.abs(fft_frame[idx]) + params.ALPHA * payload[j]) * np.exp(1j * np.angle(fft_frame[idx]))

        watermarked_frame = np.fft.ifft(fft_frame)
        
        output_data[i : i + params.FRAME] += watermarked_frame.real

        frame_idx += 1

    max_abs = np.max(np.abs(output_data))
    if max_abs > 0:
        output_data = (output_data / max_abs) * 32767.0
    
    output_data = output_data.astype(np.int16)

    wavfile.write(file_path, sample_rate, output_data)
    return file_path
