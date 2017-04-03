..  Titling
    ##++::==~~--''``

.. _commands:

Tooling
:::::::

A transformer can be called from the command line for testing or debugging purposes.

    * The survey is passed to the program as a file path.
    * Respondent data is received from *stdin*.
    * The ZIP file is printed to *stdout*.


Command Line Interface
======================

.. automodule:: sdx.common.cli

.. argparse::
   :ref: sdx.common.cli.parser
   :prog: SDX
   :nodefault:
