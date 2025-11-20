"""
Evolvo Speech Processing Library
Advanced audio analysis and code generation for speech processing tasks.
"""

from .core import Evolvo
from .code_generator import CodeGenerator
from .utils import create_speech_dataset, analyze_audio_file, save_analysis_report

__version__ = "0.1.1"
__author__ = "Sameer Rizwan"
__email__ = "sameer@example.com"

__all__ = [
    "Evolvo",
    "CodeGenerator", 
    "create_speech_dataset",
    "analyze_audio_file",
    "save_analysis_report",
]