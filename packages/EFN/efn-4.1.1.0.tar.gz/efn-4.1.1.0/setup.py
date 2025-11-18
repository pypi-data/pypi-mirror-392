from setuptools import setup, find_packages
import sys

setup(
    name="EFN",
    version="4.1.1.0",
    packages=find_packages(),
    author="Andrisgalaxy",
    description="A programming language in a Python library.",
    python_requires=">=3.8",
    install_requires=[
        "cefpython3",
        "requests",
        "beautifulsoup4",
        "Pillow",
        "psutil",
        "qrcode",
        "tkhtmlview",
        "pyttsx3",
        "pywebview",
        "ursina",
        "pygame",
        "discord.py",
        "deep_translator",
        "google",
        "pandas",
        "phonenumbers",
        "fastapi",
        "keyboard",
        "google-genai; python_version >= '3.9'",
        "kivy",
        "pytz"
    ]
)
