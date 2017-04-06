..  Titling
    ##++::==~~--''``

.. _commands:

Tooling
:::::::

Transformers can be called from the command line for testing or remediation purposes.

Under these conditions, certain parameters need to be supplied by the user. To facilitate
that, there are some helper functions you can use to parse the command line for those values.

Boilerplate
===========

Here is an example of code which turns a Transformer module into a CLI utility::

    #!/usr/bin/env python
    #  coding: UTF-8

    from collections import namedtuple
    import itertools
    import json
    import sys

    import sdx.common.cli

    __doc__ = """Module documentation"""

    class MyTransformer(Transformer):

        <class definition goes here>

    def main(args):
        Settings = namedtuple(
            "Settings",
            [
                "FTP_HOST",
                "SDX_FTP_IMAGE_PATH",
            ]
        )

        reply = json.load(args.input)
        tfr = MyTransformer(reply, seq_nr=args.seq_nr)
        zipfile = tfr.pack(
            settings=Settings("", ""),
            img_seq=itertools.count(args.img_nr),
            tmp=args.work
        )
        args.output.write(zipfile.read())


    def run():
        parser = sdx.common.cli.transformer_cli(__doc__)
        args = parser.parse_args()
        rv = main(args)
        sys.exit(rv)

    if __name__ == "__main__":
        run()

Command Line Interface
======================

.. automodule:: sdx.common.cli

.. argparse::
   :ref: sdx.common.cli.transformer_cli
   :prog: SDX
   :nodefault:
