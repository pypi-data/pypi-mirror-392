from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="evolvo",
    version="0.1.1",
    author="Sameer Rizwan",
    author_email="sameer@example.com",
    description="Advanced Speech Processing and Code Generation Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/evolvo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "librosa>=0.9.0",
        "matplotlib>=3.5.0",
        "soundfile>=0.10.0",
    ],
    keywords="speech-processing, audio-analysis, code-generation, mfcc, spectrogram",
)