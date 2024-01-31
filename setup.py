#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ready to go FastAPI project template 🍪
"""

from setuptools import setup

__version__ = "0.1.0"

with open("README.md") as readme_file:
    long_description = readme_file.read()

setup(
    name="cookiecutter-fastapi-docker",
    version=__version__,
    description="Ready to go FastAPI project template 🍪",
    long_description=long_description,
    author="Vital Kudzelka",
    author_email="vital.kudzelka@gmail.com",
    url="https://github.com/vitalk/cookiecutter-fastapi-docker",
    download_url="",
    packages=[],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Framework :: FastAPI",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
    ],
    keywords=(
        """
        cookiecutter, Python, project templates, fastapi, skeleton,
        scaffolding, docker, sqlalchemy, alembic
        """
    ),
)
