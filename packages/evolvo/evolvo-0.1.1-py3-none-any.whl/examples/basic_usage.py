#!/usr/bin/env python3
"""
Basic usage examples for Evolvo library
"""

from evolvo import Evolvo, CodeGenerator

def example_basic_analysis():
    """Basic audio analysis example"""
    print("=== Basic Audio Analysis ===")
    
    # Initialize library
    evo = Evolvo()
    
    # Load audio file (replace with your file)
    y, sr = evo.load_audio('your_audio.wav')
    
    # Perform analyses
    evo.plot_waveform(title="Audio Waveform")
    evo.compute_fft_spectrum()
    evo.compute_stft_spectrogram()
    evo.compute_mel_spectrogram()
    
    # Extract features
    f0 = evo.estimate_f0()
    formants = evo.estimate_formants_lpc()
    mfccs = evo.compute_mfcc()
    
    print(f"Pitch: {f0:.2f} Hz")
    print(f"Formants: {formants}")
    print(f"MFCCs shape: {mfccs.shape}")

def example_code_generation():
    """Code generation example"""
    print("\n=== Code Generation ===")
    
    generator = CodeGenerator()
    
    # Generate complete analysis code
    code = generator.generate_analysis_code(
        'speech.wav', 
        analysis_types=['waveform', 'fft', 'stft', 'mel', 'pitch', 'formants', 'mfcc']
    )
    
    print("Generated code length:", len(code))
    print("\nFirst 500 characters:")
    print(code[:500] + "...")
    
    # Save to file
    with open('generated_analysis.py', 'w') as f:
        f.write(code)
    
    print("Code saved to 'generated_analysis.py'")

def example_synthetic_speech():
    """Synthetic speech generation example"""
    print("\n=== Synthetic Speech ===")
    
    from evolvo import create_speech_dataset
    
    vowels, sr = create_speech_dataset()
    
    for vowel, signal in vowels.items():
        print(f"Generated {vowel.upper()} sound - Duration: {len(signal)/sr:.2f}s")
        
        # You can play the sound with:
        # Audio(signal, rate=sr)

if __name__ == "__main__":
    example_basic_analysis()
    example_code_generation() 
    example_synthetic_speech()