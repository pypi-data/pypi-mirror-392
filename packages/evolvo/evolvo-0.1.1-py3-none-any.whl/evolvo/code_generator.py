class CodeGenerator:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        return {
            'imports': """import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy.signal.windows import hamming
from scipy.fftpack import dct
""",
            'load_audio': """# Load audio file
y, sr = librosa.load('{filename}', sr={sr}, mono=True)
print(f"Loaded audio: {{len(y)/sr:.2f}} seconds, {{sr}} Hz")
""",
            'waveform_plot': """# Plot waveform
plt.figure(figsize=(10, 3))
librosa.display.waveshow(y, sr=sr)
plt.title('{title}')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
""",
            'fft_analysis': """# FFT Spectrum Analysis
y_preemph = np.append(y[0], y[1:] - 0.97 * y[:-1])
n = len(y_preemph)
Y = np.abs(np.fft.fft(y_preemph))[:n//2]
freq = np.fft.fftfreq(n, 1/sr)[:n//2]

plt.figure(figsize=(12, 6))
plt.plot(freq, Y)
plt.title('Frequency Spectrum (FFT)')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.xlim(0, sr/2)
plt.grid(True)
plt.show()
""",
            'stft_spectrogram': """# STFT Spectrogram
D = librosa.stft(y, n_fft={n_fft}, hop_length={hop_length})
S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

plt.figure(figsize=(10, 6))
librosa.display.specshow(S_db, sr=sr, hop_length={hop_length}, x_axis='time', y_axis='linear')
plt.colorbar(label="Magnitude (dB)")
plt.title("Linear-Frequency Spectrogram (STFT)")
plt.ylim(0, 5000)
plt.tight_layout()
plt.show()
""",
            'mel_spectrogram': """# Mel Spectrogram
S_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels={n_mels}, fmax={fmax})
S_mel_db = librosa.power_to_db(S_mel, ref=np.max)

plt.figure(figsize=(10, 6))
librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', sr=sr, fmax={fmax})
plt.colorbar(label="dB")
plt.title("Log-Mel Spectrogram")
plt.tight_layout()
plt.show()
""",
            'pitch_detection': """# Pitch Detection
f0s = librosa.yin(y, fmin=50, fmax=400, sr=sr)
f0_median = np.nanmedian(f0s) if not np.isnan(np.nanmedian(f0s)) else 0
print(f"Estimated Fundamental Frequency (f0): {{f0_median:.2f}} Hz")
""",
            'formant_analysis': """# Formant Analysis using LPC
order = int(sr / 1000) + 2
y_preemph = np.append(y[0], y[1:] - 0.97 * y[:-1])
segment_start = len(y_preemph) // 4
segment_end = 3 * len(y_preemph) // 4
segment = y_preemph[segment_start:segment_end]

window_size = min(int(0.025 * sr), len(segment))
segment = segment[:window_size]

a = librosa.lpc(segment, order=order)
roots = np.roots(a)
roots = [r for r in roots if np.imag(r) >= 0]
angles = np.arctan2(np.imag(roots), np.real(roots))
formant_freqs = sorted(angles * (sr / (2 * np.pi)))
formant_freqs = [f for f in formant_freqs if 200 < f < 4000]

print(f"Estimated Formant Frequencies: {{formant_freqs[:3]}}")
""",
            'mfcc_extraction': """# MFCC Feature Extraction
def pre_emphasis(sig, coeff=0.97):
    return np.append(sig[0], sig[1:] - coeff * sig[:-1])

emphasized = pre_emphasis(y)
frame_size = int(0.025 * sr)
frame_shift = int(0.010 * sr)

frames = []
for start in range(0, len(emphasized) - frame_size, frame_shift):
    frames.append(emphasized[start:start + frame_size])
frames = np.array(frames)

window = hamming(frame_size)
windowed_frames = frames * window

NFFT = 512
def power_spectrum(frame, NFFT):
    mag = np.abs(np.fft.rfft(frame, NFFT))
    power = (1.0 / NFFT) * (mag ** 2)
    return power

power_frames = np.array([power_spectrum(f, NFFT) for f in windowed_frames])

def hz_to_mel(hz): 
    return 2595 * np.log10(1 + hz / 700)
def mel_to_hz(mel): 
    return 700 * (10**(mel / 2595) - 1)

n_filters = 26
low_mel = hz_to_mel(0)
high_mel = hz_to_mel(sr / 2)
mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
hz_points = mel_to_hz(mel_points)
bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)

fbank = np.zeros((n_filters, int(NFFT / 2 + 1)))
for m in range(1, n_filters + 1):
    f_m_minus = bin_points[m - 1]
    f_m = bin_points[m]
    f_m_plus = bin_points[m + 1]
    for k in range(f_m_minus, f_m):
        fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
    for k in range(f_m, f_m_plus):
        fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

filter_banks = np.dot(power_frames, fbank.T)
filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
log_energies = np.log(filter_banks)

mfccs = np.array([dct(f, type=2, norm='ortho')[:{num_ceps}] for f in log_energies])
mfccs -= (np.mean(mfccs, axis=0) + 1e-8)

print(f"MFCCs shape: {{mfccs.shape}}")

# Plot MFCCs
plt.figure(figsize=(10, 4))
plt.imshow(mfccs.T, aspect='auto', origin='lower')
plt.title("MFCCs ({num_ceps} Coefficients per Frame)")
plt.xlabel("Frame Index")
plt.ylabel("Coefficient Index")
plt.colorbar(label="Coefficient Value")
plt.show()
"""
        }
    
    def generate_analysis_code(self, filename, sr=16000, analysis_types=None):
        if analysis_types is None:
            analysis_types = ['waveform', 'fft', 'stft', 'mel', 'pitch', 'formants', 'mfcc']
        
        code_parts = [self.templates['imports']]
        code_parts.append(self.templates['load_audio'].format(filename=filename, sr=sr))
        
        if 'waveform' in analysis_types:
            code_parts.append(self.templates['waveform_plot'].format(title='Audio Waveform'))
        
        if 'fft' in analysis_types:
            code_parts.append(self.templates['fft_analysis'])
        
        if 'stft' in analysis_types:
            code_parts.append(self.templates['stft_spectrogram'].format(n_fft=1024, hop_length=256))
        
        if 'mel' in analysis_types:
            code_parts.append(self.templates['mel_spectrogram'].format(n_mels=64, fmax=8000))
        
        if 'pitch' in analysis_types:
            code_parts.append(self.templates['pitch_detection'])
        
        if 'formants' in analysis_types:
            code_parts.append(self.templates['formant_analysis'])
        
        if 'mfcc' in analysis_types:
            code_parts.append(self.templates['mfcc_extraction'].format(num_ceps=13))
        
        return '\n'.join(code_parts)
    
    def generate_from_template(self, template_name, **kwargs):
        if template_name in self.templates:
            return self.templates[template_name].format(**kwargs)
        else:
            raise ValueError(f"Template '{template_name}' not found")