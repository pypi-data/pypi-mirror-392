import pandas as pd
from validata import extract_months
import tempfile
import os


def test_extract_months():
    df = pd.DataFrame({
        "Booking Date": [
            "2025-06-10",
            "2025-10-05",
            "2025-06-22"
        ]
    })

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        result = extract_months(tmp.name, column="Booking Date")

    os.unlink(tmp.name)

    months = result["Months Present in Data"].tolist()

    assert "June" in months
    assert "October" in months
    assert len(months) == 2
