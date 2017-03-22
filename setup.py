#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path

from setuptools import setup

try:
    # For setup.py install
    from sdx.common import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "sdx", "common", "__init__.py"),
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
    name="sdx-common",
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
        "sdx.common",
        "sdx.common.test",
        "sdx.common.formats",
        "sdx.common.formats.test",
        "sdx.common.transforms",
        "sdx.common.transforms.test",
    ],
    package_data={
        "sdx.common": [
            "requirements.txt",
        ],
        "sdx.common.test": [
            "data/*.json",
        ],
        "sdx.ops": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
        ],
    },
    install_requires=installRequirements,
    extras_require={
        "dev": [
            "pep8>=1.6.2",
        ],
        "docbuild": [
            "babel>=2.2.0",
            "sphinx-argparse>=0.1.15",
            "sphinxcontrib-seqdiag>=0.8.4",
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
