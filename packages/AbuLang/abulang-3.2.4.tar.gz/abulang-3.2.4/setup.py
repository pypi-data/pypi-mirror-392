"""
Setup script for AbuLangModule
"""

from setuptools import setup, find_packages

setup(
    name="AbuLang",
    version="3.2.4",
    author="Abu",
    author_email="abu.shariffaiml@gmail.com",
    description="Complete AbuLang integration for Python IDLE - All commands work natively",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=5.4",
    ],
    extras_require={
        "full": [
            "psutil>=5.8.0",
            "pyperclip>=1.8.2",
            "opencv-python>=4.5.0",
        ],
        "chess": [
            "python-chess>=1.9.0",
            "torch>=1.9.0",
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
    },
)
