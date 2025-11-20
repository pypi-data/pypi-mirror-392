from setuptools import setup, find_packages

setup(
    name="GearAPI",
    version="0.15.11",
    packages=find_packages(),
    install_requires=[
        "pandas<=2.2.2",
        "requests",
        "dataclasses==0.6",
        "wheel==0.37.1",
        "websocket-client==1.8.0"
    ],
    author="Darius Lim Hong Yi",
    author_email="hy.lim@kajima.com.sg",
    description="An API wrapper for cumulocity API. Made for researcher. Focus on Measurements and events resources from GEAR data",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/kajimadev-KaTRIS/GearAPI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
