import sounddevice as sd
import numpy as np

# print(sd.query_devices())

def play_frequencies(freqs, duration=1, sample_rate = 44100, amplitude = 0.5):
    for freq in freqs:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        waveform = amplitude * np.sin(2 * np.pi * freq * t).astype(np.float32)
        sd.play(waveform, sample_rate)
        sd.wait()