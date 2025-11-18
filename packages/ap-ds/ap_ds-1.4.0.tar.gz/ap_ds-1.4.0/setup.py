from setuptools import setup, find_packages

setup(
    name="ap-ds",
    version="1.4.0",
    description="DVS Audio Library - Advanced audio processing and playback",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="DVS",
    author_email="me@dvsyun.top",
    url="https://www.dvsyun.top/ap_ds",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="audio music playback sdl2",
    python_requires=">=3.7",
    install_requires=[],  # 纯Python依赖
    include_package_data=True,
)
