import numpy as np
import scipy.io.wavfile as wavfile

def generate_silent_wave(duration, sample_rate=44100):
    data = np.zeros(int(sample_rate * duration), dtype=np.int16)
    return data

sample_rate = 44100
duration = 12  # seconds

# Stem A: Silent wave
stem_a_data = generate_silent_wave(duration, sample_rate)
wavfile.write("thesis/watermark/testdata/stemA.wav", sample_rate, stem_a_data)

# Stem B: Silent wave
stem_b_data = generate_silent_wave(duration, sample_rate)
wavfile.write("thesis/watermark/testdata/stemB.wav", sample_rate, stem_b_data)

print("Generated silent stemA.wav and stemB.wav in thesis/watermark/testdata/")
