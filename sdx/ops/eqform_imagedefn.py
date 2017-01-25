#!/usr/bin/env python
#   coding: UTF-8

from collections import OrderedDict
import json
import pprint
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

class ImageDefinition:

    def root(title, surveyId, formType):
        return [
        ("title", title), ("survey_id", surveyId), ("form_type", formType),
        ("question_groups", []),
    ]

    def group(title):
        return [
            ("title", title), ("questions", []),
        ]

    def question(text, questionId):
        return [("text", text), ("question_id", questionId)]

    @staticmethod
    def populate(tree):
        node = OrderedDict()
        for k, v in tree:
            if isinstance(v, list):
                node[k] = [ImageDefinition.populate(v)]
            else:
                node[k] = v
        return node

    @staticmethod
    def read(data):
        rv = ImageDefinition.populate(
            ImageDefinition.root(
                title=data["title"],
                surveyId=data["survey_id"],
                formType=data["questionnaire_id"],
            )
        )
        for qG in data.get("question_groups", []):
            for q in qG.get("questions", []):
                print(q)
        return rv

if __name__ == "__main__":
    imgDefn = ImageDefinition.read(json.load(sys.stdin))
    json.dump(imgDefn, sys.stdout, indent=2)
