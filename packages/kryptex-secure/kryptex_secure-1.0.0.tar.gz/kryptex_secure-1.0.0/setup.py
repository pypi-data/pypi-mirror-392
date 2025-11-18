#!/usr/bin/env python3
"""
Setup script for kryptex - Secure key wrapping and file encryption tool.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kryptex-secure",
    version="1.0.0",
    author="Adegboyega Samuel",
    author_email="samscwhack@gmail.com",
    description="Production-grade secure key wrapping and file encryption tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sammy750-cyber/kryptex",
    project_urls={
        "Bug Reports": "https://github.com/Sammy750-cyber/kryptex/issues",
        "Source": "https://github.com/Sammy750-cyber/kryptex",
        "Documentation": "https://github.com/Sammy750-cyber/kryptex/docs",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "kryptex=kryptex.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="encryption cryptography security aes-gcm scrypt key-management",
    license="MIT",
)