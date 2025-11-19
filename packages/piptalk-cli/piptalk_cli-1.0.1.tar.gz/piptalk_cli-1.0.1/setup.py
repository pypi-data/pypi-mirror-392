"""Setup script for gemini-cli."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="piptalk-cli",
    version="1.0.1",
    author="Kartikeya Ranjan",
    author_email="kartikeyaranjan01@gmail.com",
    description="A command-line interface for interacting with Google's Gemini AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/gemini-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "google-generativeai>=0.3.0",
        "colorama>=0.4.6",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "piptalk=gemini_cli.cli:main",
        ],
    },
)

