import calendar
import pandas as pd


def normalize_month(month):
    """
    Convert a month input (name, abbreviation, or number)
    into an integer 1..12.
    """
    if month is None:
        raise ValueError("month must be provided")

    # numeric string or int
    if isinstance(month, int):
        m = month
    else:
        s = str(month).strip().lower()
        if s.isdigit():
            m = int(s)
        else:
            # full names and abbreviations
            for i in range(1, 13):
                full = calendar.month_name[i].lower()
                abbr = calendar.month_abbr[i].lower()
                if s == full or s == abbr:
                    m = i
                    break
            else:
                raise ValueError(f"Could not interpret month: {month!r}")

    if m < 1 or m > 12:
        raise ValueError(f"Invalid month number: {m}")

    return m


def parse_dates(series, date_format=None):
    """
    Parse a pandas Series of date strings into datetime.

    Tries:
    - explicit date_format if provided
    - automatic parse
    - automatic parse with dayfirst=True

    Returns
    -------
    pandas.Series (datetime64[ns])
    """
    if date_format:
        dt = pd.to_datetime(series, format=date_format, errors="coerce")
        if dt.isna().all() and series.notna().any():
            raise ValueError(
                "Could not parse dates with the provided date_format."
            )
        return dt

    # automatic parse
    dt = pd.to_datetime(series, errors="coerce")
    if dt.isna().all() and series.notna().any():
        # try dayfirst as fallback (e.g. 23/09/2025)
        dt = pd.to_datetime(series, errors="coerce", dayfirst=True)

    if dt.isna().all() and series.notna().any():
        raise ValueError("Could not parse dates from the column.")

    return dt
