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
    def root(title, survey_id, form_type):
        return [
            ("title", title), ("survey_id", survey_id), ("form_type", form_type),
            ("question_groups", []),
        ]

    @staticmethod
    def group(title):
        return [
            ("title", title), ("questions", []),
        ]

    @staticmethod
    def question(number, title, text, question_id, typ, options):
        return [
            ("number", number), ("title", title),
            ("text", text), ("question_id", question_id), ("type", typ),
            ("options", options)
        ]

    def read(self, data):
        """
        Read EQ-style survey definition and flatten it for use by the SDX image generator.

        """
        rv = OrderedDict(
            ImageDefinition.root(
                title=data["title"],
                survey_id=data["survey_id"],
                form_type=data["questionnaire_id"],
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
                                                question_id=o.get("q_code"),
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
                                            question_id=a.get("q_code"),
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
