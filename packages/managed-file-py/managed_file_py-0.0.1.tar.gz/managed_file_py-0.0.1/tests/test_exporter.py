import pytest
import pandas as pd
from pathlib import Path
from tools_managed_file.exporter import export_dataset


def test_export_dataset(tmp_path):
    # Create DataFrame (df adalah argumen pertama)
    df = pd.DataFrame([
        {"name": "Adam", "age": 20}
    ])

    output_dir = tmp_path / "exports"
    base_name = "data_test"

    output_path = export_dataset(df, output_dir, base_name)

    # File harus ada
    assert output_path.exists()

    # Nama file harus sesuai base_name
    assert output_path.name == "data_test.csv"

    # Isi harus sesuai
    content = output_path.read_text()
    assert "Adam" in content
    assert "20" in content


def test_export_dataset_safe_filename(tmp_path):
    """
    Jika nama file mengandung karakter ilegal, safe_filename harus bekerja.
    """
    df = pd.DataFrame([{"x": 1}])
    output_dir = tmp_path / "out"
    base_name = 'te/st:fi*le?'     # nama berbahaya

    output_path = export_dataset(df, output_dir, base_name)

    # Safe filename seharusnya mengganti karakter berbahaya
    assert "/" not in output_path.name
    assert ":" not in output_path.name
    assert "*" not in output_path.name
    assert "?" not in output_path.name


def test_export_empty_dataframe(tmp_path):
    """
    Exporting empty DataFrame tetap menghasilkan file CSV kosong (tanpa error).
    """
    df = pd.DataFrame()  # DF kosong tetap valid
    output_dir = tmp_path / "empty"
    base_name = "empty_df"

    output_path = export_dataset(df, output_dir, base_name)

    assert output_path.exists()
