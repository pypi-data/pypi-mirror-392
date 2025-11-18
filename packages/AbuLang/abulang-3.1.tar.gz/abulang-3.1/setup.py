from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="abulang",
    version="3.1",
    author="Abu",
    author_email="abu.shariffaiml@gmail.com",
    description="A friendly, Pythonic programming language for beginners and creative coders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbuCodingAI/abulang",
    project_urls={
        "Bug Tracker": "https://github.com/AbuCodingAI/abulang/issues",
        "Documentation": "https://abulang.readthedocs.io",
        "Source Code": "https://github.com/AbuCodingAI/abulang",
    },
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
        "Topic :: Education",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=5.4",
        "psutil>=5.8.0",
        "pyperclip>=1.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
        "chess": [
            "python-chess>=1.9.0",
            "torch>=1.9.0",
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "abulang=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.abu"],
        "essentials": ["python/*.yaml"],
    },
)
