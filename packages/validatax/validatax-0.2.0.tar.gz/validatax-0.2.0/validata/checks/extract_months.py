import calendar
import pandas as pd

from validata.io.loader import load_file
from .month_utils import parse_dates


def extract_months(file, sheet=None, column=None, date_format=None):
    """
    Extract distinct months present in a date column.

    Parameters
    ----------
    file : str or path-like
        Path to the CSV or Excel file.
    sheet : str | int | None, optional
        Sheet name or index for Excel. Ignored for CSV.
    column : str
        Date column name.
    date_format : str | None, optional
        Optional explicit datetime format.

    Returns
    -------
    pandas.DataFrame
        Single-column DataFrame:
        "Months Present in Data"
        with month names sorted in calendar order.
    """
    if column is None:
        raise ValueError("column must be provided")

    df = load_file(file, sheet=sheet)

    if column not in df.columns:
        raise ValueError(f"Column {column!r} not found in file.")

    dt = parse_dates(df[column])
    dt_non_null = dt.dropna()
    if dt_non_null.empty:
        return pd.DataFrame({"Months Present in Data": []})

    unique_months = sorted(dt_non_null.dt.month.unique())
    month_names = [calendar.month_name[m] for m in unique_months]

    return pd.DataFrame({"Months Present in Data": month_names})
