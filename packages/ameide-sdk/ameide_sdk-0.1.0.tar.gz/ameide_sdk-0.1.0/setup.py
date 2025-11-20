#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_namespace_packages, setup

ROOT = Path(__file__).parent

setup(
    name="ameide-sdk",
    version="0.1.0",
    description="Official AMEIDE Python SDK",
    author="AMEIDE Team",
    author_email="team@ameide.io",
    packages=find_namespace_packages(
        where="src",
        include=["ameide_sdk", "ameide_sdk.*", "buf", "buf.*"],
    ),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "grpcio>=1.65.5",
        "protobuf>=5.28.0",
    ],
    python_requires=">=3.12",
)
