#!/usr/bin/env python3
"""
Setup script for the TTBT5 Application.
This file allows installing the application as a package.
"""

from setuptools import setup, find_packages

# List of dependencies
# Add any third-party dependencies here
# Example:
# install_requires=[
#     'requests',
#     'flask',
#     'sqlalchemy'
# ]

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
    python_requires='>=3.6',
    # Add any additional package information here
    # For example:
    # install_requires=[
    #     'requests',
    # ],
    # tests_require=[
    #     'pytest',
    # ],
)
