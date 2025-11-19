#!/usr/bin/env python3
"""Setup configuration for phoenixnebula."""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="phoenixnebula-cli",
    version="1.0.3",
    author="Salih",
    author_email="salihyilboga98@gmail.com",
    description="A feature-rich, customizable Unix shell with themes and job control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SysTechSalihY/phoenixnebula",
    project_urls={
        "Bug Tracker": "https://github.com/SysTechSalihY/phoenixnebula/issues",
        "Documentation": "https://github.com/SysTechSalihY/phoenixnebula",
        "Source Code": "https://github.com/SysTechSalihY/phoenixnebula",
    },
    packages=find_packages(),
    py_modules=["phoenixnebula"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "phoenixnebula=phoenixnebula.phoenixnebula:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: BSD",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Shells",
    ],
    keywords="shell terminal bash cli interactive",
)