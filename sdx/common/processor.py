from decimal import Decimal, InvalidOperation
from functools import reduce
import operator

from sdx.common.survey import Survey


class Processor:
    """Apply operations to data.

    These methods are used to perform business logic on survey data.
    They are mostly concerned with combining multiple fields into a
    single field for output.

    Principles for processor methods:

    * Method is responsible for range check according to own logic.
    * Parametrisation is possible; use functools.partial to bind arguments.
    * Return data of the same type as the supplied default.
    * On any error, return the default.

    """

    @staticmethod
    def aggregate(qid, data, default, *args, weights=[], **kwargs):
        """Calculate the weighted sum of a question group."""
        try:
            return type(default)(
                Decimal(data.get(qid, 0)) +
                sum(Decimal(scale) * Decimal(data.get(q, 0)) for q, scale in weights)
            )
        except (InvalidOperation, ValueError):
            return default

    @staticmethod
    def evaluate(qid, data, default, *args, group=[], convert=bool, op=operator.or_, **kwargs):
        """Perform a map/reduce evaluation of a question group."""
        try:
            group_vals = [data.get(qid, None)] + [data.get(q, None) for q in group]
            data = [convert(i) for i in group_vals if i is not None]
            return type(default)(reduce(op, data))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def mean(qid, data, default, *args, group=[], **kwargs):
        """Calculate the mean of all fields in a question group."""
        try:
            group_vals = [data.get(qid, None)] + [data.get(q, None) for q in group]
            data = [Decimal(i) for i in group_vals if i is not None]
            divisor = len(data) or 1
            rv = sum(data) / divisor
            return type(default)(rv)
        except (AttributeError, InvalidOperation, TypeError, ValueError):
            return default

    @staticmethod
    def events(qid, data, default, *args, group=[], **kwargs):
        """Return a sequence of time events from a question group."""
        try:
            group_vals = [data.get(qid, None)] + [data.get(q, None) for q in group]
            data = sorted(filter(
                None, (Survey.parse_timestamp(i) for i in group_vals if i is not None)
            ))
            if all(isinstance(i, type(default)) for i in data):
                return data
            else:
                return type(default)(data)
        except (AttributeError, TypeError, ValueError):
            return default

    @staticmethod
    def survey_string(qid, data, default, *args, survey=None, **kwargs):
        """Accept a string as an option for a question.

        This method provides an opportunity for validating the string against
        the survey definition, though this has not been a requirement so far.

        """
        try:
            return type(default)(data[qid])
        except (KeyError, ValueError):
            return default

    @staticmethod
    def unsigned_integer(qid, data, default, *args, **kwargs):
        """Process a string as an unsigned integer."""
        try:
            rv = int(data.get(qid, default))
        except ValueError:
            return default
        else:
            return type(default)(rv) if rv >= 0 else default

    @staticmethod
    def percentage(qid, data, default, *args, **kwargs):
        """Process a string as a percentage."""
        try:
            rv = int(data.get(qid, default))
        except ValueError:
            return default
        else:
            return type(default)(rv) if 0 <= rv <= 100 else default
