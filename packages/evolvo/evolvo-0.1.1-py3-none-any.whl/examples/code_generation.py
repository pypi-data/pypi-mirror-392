#!/usr/bin/env python3
"""
Code generation examples for Evolvo library
"""

from evolvo import CodeGenerator

def generate_complete_analysis():
    """Generate complete speech analysis code"""
    generator = CodeGenerator()
    
    code = generator.generate_analysis_code(
        'my_speech.wav',
        sr=16000,
        analysis_types=['waveform', 'fft', 'stft', 'mel', 'pitch', 'formants', 'mfcc']
    )
    
    print("=== Generated Complete Analysis Code ===")
    print("First 300 characters:")
    print(code[:300] + "...")
    
    # Save to file
    with open('complete_speech_analysis.py', 'w') as f:
        f.write(code)
    
    print("✅ Complete analysis code saved to 'complete_speech_analysis.py'")
    return code

def generate_mfcc_only():
    """Generate MFCC-only analysis code"""
    generator = CodeGenerator()
    
    mfcc_code = generator.generate_from_template('mfcc_extraction', num_ceps=13)
    
    complete_mfcc_code = f"""{generator.generate_from_template('imports')}

{generator.generate_from_template('load_audio', filename='audio.wav', sr=16000)}

{mfcc_code}
"""
    
    with open('mfcc_analysis.py', 'w') as f:
        f.write(complete_mfcc_code)
    
    print("✅ MFCC analysis code saved to 'mfcc_analysis.py'")
    return complete_mfcc_code

if __name__ == "__main__":
    generate_complete_analysis()
    generate_mfcc_only()