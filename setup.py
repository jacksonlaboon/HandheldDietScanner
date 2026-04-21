"""
Setup script for HandheldDietScanner
"""
from setuptools import setup, find_packages

setup(
    name="HandheldDietScanner",
    version="1.0.0",
    description="A modular allergen detection system for Raspberry Pi Zero 2W",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.1.0",
    ],
    extras_require={
        "raspberry-pi": [
            "picamera2>=0.3.0",
            "numpy>=1.20.0",
        ],
        "ml": [
            "tensorflow>=2.8.0",
            "opencv-python>=4.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "diet-scanner=main:main",
        ],
    },
    package_data={
        "ui": ["assets/*"],
    },
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
)