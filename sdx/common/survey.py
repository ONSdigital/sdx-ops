from collections import namedtuple
import datetime
import json
import logging

import pkg_resources


class Survey:
    """Provide operations and accessors to survey data."""

    Identifiers = namedtuple("Identifiers", [
        "batch_nr", "seq_nr", "ts", "tx_id", "survey_id", "inst_id",
        "user_ts", "user_id", "ru_ref", "ru_check", "period"
    ])

    @staticmethod
    def load_survey(ids, package, pattern):
        """Find the survey definition by id.

        Pattern may contain formatting variables for survey identifiers.

        """
        try:
            content = pkg_resources.resource_string(
                package, pattern.format(**ids._asdict())
            )
        except FileNotFoundError:
            return None
        else:
            return json.loads(content.decode("utf-8"))

    @staticmethod
    def bind_logger(log, ids):
        """Bind a structured logger with survey metadata identifiers."""
        return log.bind(
            ru_ref=ids.ru_ref,
            tx_id=ids.tx_id,
            user_id=ids.user_id,
        )

    @staticmethod
    def parse_timestamp(text):
        """Parse a text field for a date or timestamp.

        Date and time formats vary across surveys.
        This method knows how to read them.

        """

        cls = datetime.datetime

        if text.endswith("Z"):
            return cls.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=datetime.timezone.utc
            )

        try:
            return cls.strptime(text, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            pass

        try:
            return cls.strptime(text.partition(".")[0], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass

        try:
            return cls.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            pass

        try:
            return cls.strptime(text, "%d/%m/%Y").date()
        except ValueError:
            return None

    @staticmethod
    def identifiers(data, batch_nr=0, seq_nr=0, log=None):
        """Parse common metadata from the survey.

        Return a named tuple which code can use to access ids, etc.

        """
        log = log or logging.getLogger(__name__)
        ru_ref = data.get("metadata", {}).get("ru_ref", "")
        ts = datetime.datetime.now(datetime.timezone.utc)
        rv = Survey.Identifiers(
            batch_nr, seq_nr, ts,
            data.get("tx_id"),
            data.get("survey_id"),
            data.get("collection", {}).get("instrument_id"),
            Survey.parse_timestamp(data.get("submitted_at", ts.isoformat())),
            data.get("metadata", {}).get("user_id"),
            ''.join(i for i in ru_ref if i.isdigit()),
            ru_ref[-1] if ru_ref and ru_ref[-1].isalpha() else "",
            data.get("collection", {}).get("period")
        )
        if any(i is None for i in rv):
            log.warning("Missing an id from {0}".format(rv))
            return None
        else:
            return rv
