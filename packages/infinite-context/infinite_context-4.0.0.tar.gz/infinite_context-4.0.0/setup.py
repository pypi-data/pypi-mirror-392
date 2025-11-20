from setuptools import setup, find_packages

setup(
    name = 'infinite_context',
    version = '4.0.0',
    author = 'SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'perpetual-context',
        'certifi==2025.11.12',
        'requests',
        'lxml',
        'pandas',
        'pillow',
        'numpy==1.25.2',
        'paddlepaddle==2.6.1',
        'paddleocr==2.7.3',
        'opencv-python',
        'moviepy==1.0.3',
        'SpeechRecognition',
        'ffmpeg-python',
        'pydub',
        'docx2txt',
        'youtube-transcript-extractor'
    ],
    url = 'https://github.com/sapiens-technology/InfiniteContext',
    license = 'Proprietary Software'
)
