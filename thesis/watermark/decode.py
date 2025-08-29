import numpy as np
import scipy.io.wavfile as wavfile
import params
from encode import frame_pn
from crypto import load_key

def decode_file(file_path, secret, track_id):
    """
    Decode with HMAC verification, no crop recovery
    """
    sample_rate, audio = wavfile.read(file_path)
    if sample_rate != params.SR:
        raise ValueError(f"Sample rate {sample_rate} not supported, expected {params.SR}")

    if audio.dtype != np.float32:
        audio = audio.astype(np.float32) / 32767.0

    windows = []
    n_frames = len(audio) // params.HOP
    
    for frame_idx in range(n_frames):
        start = frame_idx * params.HOP
        end = start + params.FRAME
        if end > len(audio):
            break
        
        frame = audio[start:end]
        
        pn = np.asarray(frame_pn(secret, track_id, frame_idx, params.SYNC_CHIPS))
        
        if len(frame) < len(pn):
            continue

        correlation = np.correlate(frame[:len(pn)], pn, mode='valid')[0]
        normalized = correlation / (len(pn) * (np.std(frame[:len(pn)]) + 1e-10) * (np.std(pn) + 1e-10))
        
        if normalized > 0.7:
            windows.append({
                'source_id': str(track_id),
                'start_ms': int(start * 1000 / sample_rate),
                'end_ms': int(end * 1000 / sample_rate),
                'confidence': float(normalized)
            })
    
    stats = {}
    return windows, stats