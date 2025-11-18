from validata.io.loader import load_file
from .month_utils import normalize_month, parse_dates


def validate_month(
    file,
    sheet=None,
    column=None,
    date_format=None,
    month=None,
):
    """
    Validate that all dates in a column belong to a given month.

    Parameters
    ----------
    file : str or path-like
        Path to the CSV or Excel file.
    sheet : str | int | None, optional
        Sheet name or index for Excel. Ignored for CSV. If None,
        uses the first sheet for Excel files.
    column : str
        Name of the date column to validate.
    date_format : str | None, optional
        Optional explicit datetime format, e.g. "%d/%m/%Y".
        If not provided, automatic parsing is used.
    month : str | int
        Target month to validate against. Can be:
        - full name ("October")
        - abbreviation ("Oct")
        - numeric string ("10")
        - integer (10).

    Returns
    -------
    bool
        True if all non-null dates in the column belong to the given month.
        False otherwise.
    """
    if column is None:
        raise ValueError("column must be provided")

    df = load_file(file, sheet=sheet)

    if column not in df.columns:
        raise ValueError(f"Column {column!r} not found in file.")

    target_month = normalize_month(month)
    dt = parse_dates(df[column])

    # focus only on non-null dates
    dt_non_null = dt.dropna()
    if dt_non_null.empty:
        # no valid dates -> treat as False for safety
        return False

    months = dt_non_null.dt.month
    return bool((months == target_month).all())
