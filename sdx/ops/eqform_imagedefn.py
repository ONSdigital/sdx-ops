#!/usr/bin/env python
#   coding: UTF-8

import json
import sys

__doc__ = """
This standalone script reads a JSON file of the type used by EQ to define
its survey structure.

The output is a JSON file containing a simplified tree used by SDX to generate
pre-transform images.

Example:

python eqform_imagedefn.py \
< eq-survey-runner/app/data/1_0001.json \
> sdx-transform-cora/transform/surveys/144.0001.json

"""

if __name__ == "__main__":
    print(json.load(sys.stdin))
