from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="realtime-asr-sdk",
    version="0.1.2",
    author="Leon",
    author_email="962055298@qq.com",
    description="Python SDK for real-time speech transcription via WebSocket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/inccleo/realtime-asr-sdk",
    packages=find_packages(exclude=["examples", "tests"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websocket-client>=1.6.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "audio": ["PyAudio>=0.2.13"],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="speech recognition asr websocket realtime transcription",
    project_urls={
        "Bug Reports": "https://github.com/inccleo/realtime-asr-sdk/issues",
        "Source": "https://github.com/inccleo/realtime-asr-sdk",
    },
)
