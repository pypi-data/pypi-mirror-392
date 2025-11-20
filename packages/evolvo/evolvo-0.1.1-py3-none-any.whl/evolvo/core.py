import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import soundfile as sf
from scipy.signal import lfilter
from scipy.signal.windows import hamming  # FIXED IMPORT
from scipy.fft import fft, fftfreq
from scipy.fftpack import dct
from IPython.display import Audio
import scipy.linalg  # For lstsq

class Evolvo:
    def __init__(self):
        self.sr = None
        self.y = None
    
    def load_audio(self, filename, target_sr=16000):
        try:
            self.y, self.sr = librosa.load(filename, sr=target_sr, mono=True)
            print(f"Loaded {filename} successfully")
            print(f"Duration: {len(self.y)/self.sr:.2f} seconds, Sampling rate: {self.sr} Hz")
        except FileNotFoundError:
            print(f"File '{filename}' not found")
            self.sr = target_sr
            self.y = np.random.randn(self.sr * 2)
            print("Using dummy audio")
        return self.y, self.sr
    
    def pre_emphasis(self, signal, coeff=0.97):
        return np.append(signal[0], signal[1:] - coeff * signal[:-1])
    
    def normalize_audio(self, signal):
        return librosa.util.normalize(signal, norm=np.inf)
    
    def plot_waveform(self, signal=None, sr=None, title="Waveform", segment_ms=None):
        if signal is None:
            signal = self.y
        if sr is None:
            sr = self.sr
        
        plt.figure(figsize=(10, 3))
        if segment_ms:
            samples = int(segment_ms * sr / 1000)
            librosa.display.waveshow(signal[:samples], sr=sr)
        else:
            librosa.display.waveshow(signal, sr=sr)
        plt.title(title)
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def compute_fft_spectrum(self, signal=None):
        if signal is None:
            signal = self.y
        
        y_preemph = self.pre_emphasis(signal)
        n = len(y_preemph)
        Y = np.abs(fft(y_preemph))[:n//2]
        freq = fftfreq(n, 1/self.sr)[:n//2]
        
        plt.figure(figsize=(12, 6))
        plt.plot(freq, Y)
        plt.title('Frequency Spectrum (FFT)')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.xlim(0, self.sr/2)
        plt.grid(True)
        plt.show()
        
        return freq, Y
    
    def estimate_f0(self, signal=None):
        if signal is None:
            signal = self.y
        
        f0s = librosa.yin(signal, fmin=50, fmax=400, sr=self.sr)
        f0_median = np.nanmedian(f0s) if not np.isnan(np.nanmedian(f0s)) else 0
        print(f"Estimated Fundamental Frequency (f0): {f0_median:.2f} Hz")
        return f0_median
    
    def estimate_formants_lpc(self, signal=None, order=None):
        if signal is None:
            signal = self.y
        
        if order is None:
            order = int(self.sr / 1000) + 2
        
        y_preemph = self.pre_emphasis(signal)
        segment_start = len(y_preemph) // 4
        segment_end = 3 * len(y_preemph) // 4
        segment = y_preemph[segment_start:segment_end]
        
        window_size = min(int(0.025 * self.sr), len(segment))
        segment = segment[:window_size]
        
        a = librosa.lpc(segment, order=order)
        roots = np.roots(a)
        roots = [r for r in roots if np.imag(r) >= 0]
        angles = np.arctan2(np.imag(roots), np.real(roots))
        formant_freqs = sorted(angles * (self.sr / (2 * np.pi)))
        formant_freqs = [f for f in formant_freqs if 200 < f < 4000]
        
        print(f"Estimated Formant Frequencies: {formant_freqs[:3]}")
        return formant_freqs[:3]
    
    def plot_spectrum_with_features(self, signal=None):
        if signal is None:
            signal = self.y
        
        y_preemph = self.pre_emphasis(signal)
        n = len(y_preemph)
        Y = np.abs(fft(y_preemph))[:n//2]
        freq = fftfreq(n, 1/self.sr)[:n//2]
        
        f0_median = self.estimate_f0(signal)
        formant_freqs = self.estimate_formants_lpc(signal)
        
        plt.figure(figsize=(12, 6))
        plt.plot(freq, Y)
        plt.title('Frequency Spectrum with Estimated Harmonics and Formants')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.xlim(0, self.sr/2)
        plt.grid(True)
        
        if f0_median > 0:
            harmonic_freqs = np.arange(f0_median, self.sr/2, f0_median)
            plt.vlines(harmonic_freqs, 0, np.max(Y), color='r', linestyle='--', 
                      label='Harmonics (estimated f0)', alpha=0.5)
        
        if formant_freqs:
            plt.vlines(formant_freqs[:3], 0, np.max(Y), color='g', linestyle='--', 
                      linewidth=2, label='Formants (estimated)')
            
            labeled_formants = 0
            for f in formant_freqs:
                if labeled_formants < 3 and f > 50:
                    plt.text(f, np.max(Y) * 0.95, f'F{labeled_formants+1}', 
                            color='g', fontsize=12, ha='center')
                    labeled_formants += 1
                if labeled_formants >= 3:
                    break
        
        plt.legend()
        plt.show()
    
    def compute_stft_spectrogram(self, signal=None, n_fft=1024, hop_length=256):
        if signal is None:
            signal = self.y
        
        D = librosa.stft(signal, n_fft=n_fft, hop_length=hop_length)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        plt.figure(figsize=(10, 6))
        librosa.display.specshow(S_db, sr=self.sr, hop_length=hop_length, 
                                x_axis='time', y_axis='linear')
        plt.colorbar(label="Magnitude (dB)")
        plt.title("Linear-Frequency Spectrogram (STFT)")
        plt.ylim(0, 5000)
        plt.tight_layout()
        plt.show()
        
        return S_db
    
    def compute_mel_spectrogram(self, signal=None, n_mels=64, fmax=8000):
        if signal is None:
            signal = self.y
        
        S_mel = librosa.feature.melspectrogram(y=signal, sr=self.sr, 
                                              n_mels=n_mels, fmax=fmax)
        S_mel_db = librosa.power_to_db(S_mel, ref=np.max)
        
        plt.figure(figsize=(10, 6))
        librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', 
                                sr=self.sr, fmax=fmax)
        plt.colorbar(label="dB")
        plt.title("Log-Mel Spectrogram")
        plt.tight_layout()
        plt.show()
        
        return S_mel_db
    
    def compare_spectrograms(self, signal=None):
        if signal is None:
            signal = self.y
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 2, 1)
        D = librosa.stft(signal, n_fft=1024, hop_length=256)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        librosa.display.specshow(S_db, sr=self.sr, hop_length=256, 
                                x_axis='time', y_axis='hz')
        plt.colorbar(label='dB')
        plt.title('Linear-Frequency Spectrogram')
        plt.ylim(0, 5000)
        
        plt.subplot(1, 2, 2)
        S_mel = librosa.feature.melspectrogram(y=signal, sr=self.sr, 
                                              n_mels=64, fmax=8000)
        S_mel_db = librosa.power_to_db(S_mel, ref=np.max)
        librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', 
                                sr=self.sr, fmax=8000)
        plt.colorbar(label='dB')
        plt.title('Log-Mel Spectrogram')
        
        plt.tight_layout()
        plt.show()
    
    def segment_energy_analysis(self, signal=None, segments=None):
        if signal is None:
            signal = self.y
        
        if segments is None:
            segment1 = signal[5000:15000]
            segment2 = signal[20000:30000]
        else:
            segment1, segment2 = segments
        
        energy1 = np.sum(segment1**2)
        energy2 = np.sum(segment2**2)
        
        plt.figure(figsize=(15, 4))
        
        plt.subplot(1, 2, 1)
        librosa.display.waveshow(segment1, sr=self.sr)
        plt.title(f"Segment 1 (Energy: {energy1:.2f})")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        
        plt.subplot(1, 2, 2)
        librosa.display.waveshow(segment2, sr=self.sr)
        plt.title(f"Segment 2 (Energy: {energy2:.2f})")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        
        plt.tight_layout()
        plt.show()
        
        print(f"Energy of segment 1: {energy1:.2f}")
        print(f"Energy of segment 2: {energy2:.2f}")
        
        return energy1, energy2
    
    def generate_vowel_sounds(self):
        sr = 8000
        t = np.linspace(0, 1, sr)
        
        y_aa = 0.5*np.sin(2*np.pi*120*t) + 0.2*np.sin(2*np.pi*800*t) + 0.1*np.sin(2*np.pi*2400*t)
        y_aa = y_aa / np.max(np.abs(y_aa))
        
        y_ee = 0.5*np.sin(2*np.pi*270*t) + 0.3*np.sin(2*np.pi*2290*t) + 0.1*np.sin(2*np.pi*3010*t)
        y_ee = y_ee / np.max(np.abs(y_ee))
        
        y_oo = 0.5*np.sin(2*np.pi*120*t) + 0.2*np.sin(2*np.pi*800*t) + 0.1*np.sin(2*np.pi*2460*t)
        y_oo = y_oo / np.max(np.abs(y_oo))
        
        return {'aa': y_aa, 'ee': y_ee, 'oo': y_oo}, sr
    
    def compute_mfcc(self, signal=None, num_ceps=13):
        if signal is None:
            signal = self.y
        
        emphasized = self.pre_emphasis(signal)
        
        frame_size = int(0.025 * self.sr)
        frame_shift = int(0.010 * self.sr)
        
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
        high_mel = hz_to_mel(self.sr / 2)
        mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
        hz_points = mel_to_hz(mel_points)
        bin_points = np.floor((NFFT + 1) * hz_points / self.sr).astype(int)
        
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
        
        mfccs = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
        mfccs -= (np.mean(mfccs, axis=0) + 1e-8)
        
        plt.figure(figsize=(10, 4))
        plt.imshow(mfccs.T, aspect='auto', origin='lower')
        plt.title("MFCCs (13 Coefficients per Frame)")
        plt.xlabel("Frame Index")
        plt.ylabel("Coefficient Index")
        plt.colorbar(label="Coefficient Value")
        plt.show()
        
        return mfccs