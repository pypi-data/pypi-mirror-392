"""
ProveChain - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="provechain",
    version="0.1.0",
    author="John Doyle",
    author_email="john.doyle.mail@icloud.com",
    description="Blockchain Timestamping for Source Code - Prove code authorship with cryptographic proofs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aramantos/provechain",
    packages=["provechain"],
    package_dir={"provechain": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0.1",
        "cryptography>=41.0.4",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "provechain=provechain.cli:main",
        ],
    },
    keywords="blockchain timestamp proof authorship ip-protection git source-code",
    project_urls={
        "Bug Reports": "https://github.com/Aramantos/provechain/issues",
        "Source": "https://github.com/Aramantos/provechain",
    },
)
