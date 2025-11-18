"""Setup script for vessel-validator package."""

from setuptools import setup, find_packages

setup(
    name="vessel-validator",
    version="0.1.0",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    python_requires=">=3.8",
)
