..  Titling
    ##++::==~~--''``

.. _processors:

Processing functions
::::::::::::::::::::

Surveys often require some business logic to be applied.

In the general case, this means deriving an output value for a single question id,
based on the supplied data for a *group* of question ids. 

In the simplest case, the size of that group is 1, and contains only the question
for which data is calculated.

.. automodule:: sdx.common.processor

.. autoclass:: sdx.common.processor.Processor
   :members:
   :member-order: bysource

