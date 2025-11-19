import csv
import pandas as pd
from pathlib import Path
from .utils import safe_filename

def load_dataset(path: Path):
    """
    Load CSV or Excel file into pandas DataFrame.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset does not exist: {path}")

    if path.suffix.lower() in [".csv"]:
        return pd.read_csv(path)

    if path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    raise ValueError("File must be CSV or Excel.")

def export_dataset(df, output_dir: Path, base_name: str) -> Path:
    """
    Export a pandas DataFrame to CSV.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = safe_filename(base_name) + ".csv"
    output_path = output_dir / filename

    df.to_csv(output_path, index=False, encoding="utf-8")

    return output_path
