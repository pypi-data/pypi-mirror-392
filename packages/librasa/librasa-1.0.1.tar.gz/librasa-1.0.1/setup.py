from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="librasa",
    version="1.0.1",
    author="Sameer Rizwan",
    author_email="xie19113@gmail.com",
    description="A comprehensive Python library for speech processing tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
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
        "librosa>=0.10.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.9.0",
        "soundfile>=0.12.0",
        "scikit-learn>=1.0.0",
    ],
)