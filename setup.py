#!/usr/bin/env python3
"""
Setup script for the TTBT5 Application.
This file allows installing the application as a package.
"""

from setuptools import setup, find_packages

# List of dependencies
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name='ttbt5',
    version='1.0.0',
    description='TTBT5 Application',
    author='TTBT5 Team',
    author_email='example@example.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ttbt5=src.main:main',
        ],
    },
    package_dir={'': '.'},
    python_requires='>=3.6',
    install_requires=requirements,
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
)
