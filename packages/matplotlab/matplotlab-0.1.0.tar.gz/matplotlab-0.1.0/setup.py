from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies (only numpy - minimal installation)
core_requirements = [
    "numpy>=1.21.0",
]

# Module-specific optional dependencies
rl_requirements = [
    "numpy>=1.21.0",
    "matplotlib>=3.4.0",
    "gymnasium>=0.28.0",
    "google-generativeai>=0.3.0",  # For helper function
]

ann_requirements = [
    "numpy>=1.21.0",
    "matplotlib>=3.4.0",
    # Will add: tensorflow, keras, etc. when ANN module is built
]

speech_requirements = [
    "numpy>=1.21.0",
    "matplotlib>=3.4.0",
    # Will add: librosa, soundfile, etc. when Speech module is built
]

setup(
    name="matplotlab",
    version="0.1.0",
    author="Sohail-Creates",
    author_email="your.email@example.com",  # Update with your actual email
    description="Extended plotting and ML utilities library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sohail-Creates/matplotlab",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    
    # Only numpy installed by default (minimal)
    install_requires=core_requirements,
    
    # Optional dependencies - install only what you need!
    extras_require={
        "rl": rl_requirements,              # pip install matplotlab[rl]
        "ann": ann_requirements,            # pip install matplotlab[ann]
        "speech": speech_requirements,      # pip install matplotlab[speech]
        "all": rl_requirements + ann_requirements + speech_requirements,  # pip install matplotlab[all]
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.9"],
    },
)
