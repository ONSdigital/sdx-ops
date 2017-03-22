..  Titling
    ##++::==~~--''``

SDX-common
::::::::::

Utilities and classes for SDX apps.

sdx.common
==========

A common library for SDX apps. App projects declare their dependence on *sdx-common* which
is deployed and installed via pip.

sdx.ops
=======

Operations scripts for SDX deployment and administration. These run from the command line
and are not part of the deployed package.

Basic use
=========

Assuming a Python 3.5 virtual environment at ``~/py3.5``...

#. Run the unit tests::

    ~/py3.5/bin/python -m unittest discover sdx

#. Create a package for deployment::

    ~/py3.5/bin/python setup.py sdist
