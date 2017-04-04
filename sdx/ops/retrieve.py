#!/usr/bin/env python
#   coding: UTF-8

import argparse
import os.path
import sys

from pymongo import MongoClient

__doc__ = """
Retrieve survey results from the SDX store.

"""

DFLT_LOCN = os.path.expanduser("~")


def main(args):
    client = MongoClient(args.url)
    collection = client.sdx_store.responses
    for line in args.input:
        tx_id = line.strip()
        doc = collection.find_one({"tx_id": tx_id})
        if doc is None:
            print("No data for {0}".format(tx_id), file=sys.stderr)
        else:
            with open(os.path.join(args.work, tx_id + ".json"), "w") as output:
                output.write(doc)
            print("Retrieved data for {0}".format(tx_id), file=sys.stderr)


def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
    )
    parser.add_argument(
        "input",
        nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="Designate a text file of transaction ids."
    )
    rv.add_argument(
        "--url", required=False, default="mongodb://localhost:27017",
        help="Set the URL to the SDX store."
    )
    parser.add_argument(
        "--work", default=DFLT_LOCN,
        help="Set a path to the working directory.")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
