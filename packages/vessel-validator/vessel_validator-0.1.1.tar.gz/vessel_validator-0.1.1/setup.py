"""Setup script for vessel-validator package."""

from setuptools import setup, find_packages

setup(
    name="vessel-validator",
    version="0.1.1",
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    package_data={"vessel_validator": ["py.typed"]},
    python_requires=">=3.8",
)
