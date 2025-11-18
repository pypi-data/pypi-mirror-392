import pandas as pd
from validata import validate_month
import tempfile
import os


def test_validate_month_True():
    df = pd.DataFrame({
        "Transaction Date": ["2025-10-01", "2025-10-12", "2025-10-30"]
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        assert validate_month(tmp.name, column="Transaction Date", month="October") is True

    os.unlink(tmp.name)


def test_validate_month_false():
    df = pd.DataFrame({
        "Transaction Date": ["2025-10-12", "2025-09-29"]
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        assert validate_month(tmp.name, column="Transaction Date", month="October") is False

    os.unlink(tmp.name)
