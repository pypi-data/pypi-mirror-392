from setuptools import setup, find_packages

setup(
    name="DearDavil",       # choose UNIQUE name
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition",
        "pyaudio",
        "mtranslate",
        "colorama"
    ],
)


