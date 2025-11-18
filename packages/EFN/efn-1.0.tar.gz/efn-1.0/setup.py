from setuptools import setup, find_packages

setup(
    name="EFN",
    version="1.0",
    packages=find_packages(),
    author="Andrisgalaxy",
    description="A programming language in a Python library.",
    python_requires=">=3.6",
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
        "pygame"
    ]
)
