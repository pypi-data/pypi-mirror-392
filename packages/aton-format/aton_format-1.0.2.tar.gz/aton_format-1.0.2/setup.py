"""Setup configuration for ATON."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aton-format",
    version="1.0.2",
    author="Stefano D'Agostino",
    author_email="dago.stefano@gmail.com",
    description="ATON FORMAT - Adaptive Token-Oriented Notation - Data format optimized for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.atonformat.com",
    packages=["aton"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    install_requires=[],
)
