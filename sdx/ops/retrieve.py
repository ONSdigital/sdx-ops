#!/usr/bin/env python
#   coding: UTF-8

import argparse
import os.path
import re
import sys

import bson.json_util
from pymongo import MongoClient

__doc__ = """
Retrieve survey results from the SDX store.

This script matches a specified field against one or more regular expressions.

"""

DFLT_LOCN = os.path.expanduser("~")
DFLT_FIELD = "survey_response.metadata.ru_ref"


def main(args):
    client = MongoClient(args.url)
    collection = client.sdx_store.responses
    for line in args.input:
        pattern = re.compile(line.strip())
        doc = collection.find_one({args.field: pattern})
        if doc is None:
            print("No {0} values match {1.pattern}".format(
                args.field, pattern
            ), file=sys.stderr)
        else:
            tx_id = doc["survey_response"]["tx_id"]
            with open(os.path.join(args.work, tx_id + ".json"), "w") as output:
                output.write(bson.json_util.dumps(doc))
            print("Retrieved data for {0}".format(tx_id), file=sys.stderr)


def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
    )
    rv.add_argument(
        "input",
        nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="Designate a text file of search patterns."
    )
    rv.add_argument(
        "--url", required=False, default="mongodb://localhost:27017",
        help="Set the URL to the SDX store."
    )
    rv.add_argument(
        "--field", default=DFLT_FIELD,
        help="Specify a field to search [{0}].".format(DFLT_FIELD)
    )
    rv.add_argument(
        "--work", default=DFLT_LOCN,
        help="Set a path to the working directory [{0}].".format(DFLT_LOCN)
    )
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
