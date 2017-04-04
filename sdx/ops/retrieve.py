#!/usr/bin/env python
#   coding: UTF-8

import argparse
import sys

from pymongo import MongoClient

__doc__ = """
Retrieve survey results from the SDX store.

"""

def main(args):
    for line in args.input:
        print(line, file=sys.stderr)

def parser(description=__doc__):
    rv =  argparse.ArgumentParser(
        description,
    )
    parser.add_argument(
        "input",
        nargs="?", type=argparse.FileType("r"), default=sys.stdin,
        help="Designate a text file of transaction ids."
    )
    rv.add_argument(
        "--url", required=True,
        help="Set the URL to the SDX store."
    )
    return rv

def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
