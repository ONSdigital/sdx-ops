#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup

try:
    # For setup.py install
    from sdx.ops import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "sdx", "ops", "__init__.py"),
                'r').read().split("=")[-1].strip()
        )
    )

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

installRequirements = [
    i.strip() for i in open(
        os.path.join(os.path.dirname(__file__), "requirements.txt"), 'r'
    ).readlines()
]

setup(
    name="sdx-ops",
    version=version,
    description="Operations scripts for SDX deployment and administration.",
    author="D Haynes",
    author_email="tundish@thuswise.org",
    url="https://github.com/ONSdigital/sdx-ops",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=[
        "sdx.ops",
        "sdx.ops.test",
    ],
    package_data={},
    install_requires=installRequirements,
    extras_require={
        "dev": [
            "pep8>=1.6.2",
        ],
    },
    tests_require=[
    ],
    entry_points={
        "console_scripts": [
        ],
    },
    zip_safe=False
)
