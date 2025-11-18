from setuptools import setup, find_packages

setup(
    name="jardecompiler",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "jardecompile=jardecompiler.__main__:main",
        ],
    },
    description="A Python-native tool to unzip and decompile JAR files",
    author="Casey",
    license="MIT",
)