import pandas as pd
from validata import check_required_columns
import tempfile
import os


def test_required_columns():
    df = pd.DataFrame({
        "Hotel Name": ["Marriott"],
        "Hotel City": ["Paris"],
        "Hotel Country": ["France"],
        "Transaction Date": ["2025-10-12"]
    })

    required = [
        "Hotel Name",
        "Hotel City",
        "Hotel Address",          
        "Transaction Date"
    ]

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.to_csv(tmp.name, index=False)

        result = check_required_columns(required, tmp.name)

    os.unlink(tmp.name)

    missing = result["Missing Required Columns"].dropna().tolist()

    assert "Hotel Address" in missing
    assert len(missing) == 1
