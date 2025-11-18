"""
Legacy setup.py shim for backward compatibility.
Modern builds use pyproject.toml (PEP 621).
"""

from __future__ import annotations
import pathlib
from setuptools import setup

# Read long description (README.md)
README = pathlib.Path(__file__).parent / "README.md"
long_description = README.read_text(encoding="utf-8") if README.exists() else ""

setup(
    name="tree2cmd",
    version="0.2.1",  # ⚠ Must match pyproject.toml, or use dynamic versioning
    description="Convert text-based folder tree structures into real directories and files.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Antony Joseph Mathew",
    author_email="antonyjosephmathew1@gmail.com",

    url="https://github.com/ajmanjoma/tree2cmd",
    project_urls={
        "Documentation": "https://github.com/ajmanjoma/tree2cmd/tree/main/docs",
        "Source": "https://github.com/ajmanjoma/tree2cmd",
        "Issue Tracker": "https://github.com/ajmanjoma/tree2cmd/issues",
    },

    packages=["tree2cmd"],
    include_package_data=True,

    entry_points={
        "console_scripts": [
            "tree2cmd = tree2cmd.cli:main",
        ]
    },

    install_requires=[],  # No dependencies

    license="MIT",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Topic :: Utilities",
        "Topic :: Software Development :: Code Generators",
    ],

    python_requires=">=3.8",
)
