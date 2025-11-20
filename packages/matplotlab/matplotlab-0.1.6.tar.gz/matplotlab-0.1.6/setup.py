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

sp_requirements = [
    "numpy>=1.21.0",
    "matplotlib>=3.4.0",
    "librosa>=0.9.0",
    "soundfile>=0.11.0",
    "scipy>=1.7.0",
    "ipython>=7.0.0",
    "google-generativeai>=0.3.0",
]

setup(
    name="matplotlab",
    version="0.1.6",
    author="Sohail-Creates",
    author_email="sohailaslam7888@gmail.com",
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
        "rl": rl_requirements,
        "ann": ann_requirements,
        "sp": sp_requirements,
        "all": rl_requirements + ann_requirements + sp_requirements,
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.9"],
    },
)
