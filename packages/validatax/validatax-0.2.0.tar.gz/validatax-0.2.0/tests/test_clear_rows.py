import pandas as pd
from validata import clear_rows
import tempfile
import os


def test_clear_rows_csv():
    df = pd.DataFrame({
        "Hotel Name": ["A", "B", "C"],
        "City": ["Paris", "Berlin", "Rome"]
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        clear_rows(tmp.name)
        cleaned = pd.read_csv(tmp.name)

    os.unlink(tmp.name)

    assert cleaned.empty
    assert list(cleaned.columns) == ["Hotel Name", "City"]


def test_clear_rows_excel():
    df = pd.DataFrame({
        "Hotel Name": ["A", "B", "C"],
        "City": ["Paris", "Berlin", "Rome"]
    })

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        df.to_excel(tmp.name, index=False)

        clear_rows(tmp.name)
        cleaned = pd.read_excel(tmp.name)

    os.unlink(tmp.name)

    assert cleaned.empty
    assert list(cleaned.columns) == ["Hotel Name", "City"]
