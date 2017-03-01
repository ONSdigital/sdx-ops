#!/usr/bin/env python
#   coding: UTF-8

from collections import OrderedDict
import json
import re
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

    tag = re.compile("<.*?>")

    @staticmethod
    def root(title, surveyId, formType):
        return [
            ("title", title), ("survey_id", surveyId), ("form_type", formType),
            ("question_groups", []),
        ]

    @staticmethod
    def group(title):
        return [
            ("title", title), ("questions", []),
        ]

    @staticmethod
    def question(number, title, text, questionId, typ, options):
        return [
            ("number", number), ("title", title),
            ("text", text), ("question_id", questionId), ("type", typ),
            ("options", options)
        ]

    def read(self, data):
        """
        Read EQ-style survey definition and flatten it for use by the SDX image generator.

        """
        rv = OrderedDict(
            ImageDefinition.root(
                title=data["title"],
                surveyId=data["survey_id"],
                formType=data["questionnaire_id"],
            )
        )
        for g in data.get("groups", []):
            group = OrderedDict(
                ImageDefinition.group(
                    title=g["title"],
                )
            )
            for b in g.get("blocks", []):
                for s in b.get("sections", []):
                    for q in s.get("questions", []):
                        number, title = q.get("number"), q.get("title")
                        for a in q.get("answers", []):

                            typ = a["type"].lower()
                            if typ in ("checkbox"):
                                for o in a["options"]:
                                    group["questions"].append(
                                        OrderedDict(
                                            ImageDefinition.question(
                                                number=number,
                                                title=ImageDefinition.tag.sub("", title),
                                                text=ImageDefinition.tag.sub("", o["label"]),
                                                questionId=o.get("q_code"),
                                                typ=typ,
                                                options=[o["value"]],
                                            )
                                        )
                                    )
                            else:
                                text = a.get("label") or q.get("title")
                                group["questions"].append(
                                    OrderedDict(
                                        ImageDefinition.question(
                                            number=number,
                                            title=ImageDefinition.tag.sub("", title),
                                            text=ImageDefinition.tag.sub("", text),
                                            questionId=a.get("q_code"),
                                            typ=typ,
                                            options=[
                                                o.get("value") for o in a.get("options", [])
                                            ]
                                        )
                                    )
                                )

            if group["questions"]:
                # We exclude interstitials, etc
                rv["question_groups"].append(group)

        return rv

if __name__ == "__main__":
    imgDefn = ImageDefinition().read(json.load(sys.stdin))
    json.dump(imgDefn, sys.stdout, indent=2)
