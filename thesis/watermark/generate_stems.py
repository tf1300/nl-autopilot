import numpy as np
import scipy.io.wavfile as wavfile

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    amplitude_scaled = amplitude * np.iinfo(np.int16).max
    data = amplitude_scaled * np.sin(2 * np.pi * frequency * t)
    return data.astype(np.int16)

sample_rate = 44100
duration = 12  # seconds

# Stem A: 440 Hz sine wave
stem_a_data = generate_sine_wave(440, duration, sample_rate)
wavfile.write("thesis/watermark/testdata/stemA.wav", sample_rate, stem_a_data)

# Stem B: 660 Hz sine wave
stem_b_data = generate_sine_wave(660, duration, sample_rate)
wavfile.write("thesis/watermark/testdata/stemB.wav", sample_rate, stem_b_data)

print("Generated stemA.wav and stemB.wav in thesis/watermark/testdata/")
