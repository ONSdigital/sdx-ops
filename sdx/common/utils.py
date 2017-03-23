import arrow


def format_date(value, style="long"):
    """convert a datetime to a different format."""

    timezone = "Europe/London"
    if style == "short":
        return arrow.get(value).to(timezone).format("YYYYMMDD")
    else:
        return arrow.get(value).to(timezone).format("DD/MM/YYYY HH:mm:ss")

