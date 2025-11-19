from pathlib import Path
from tools_managed_file.duplicate import duplicate_file
import pytest


def test_duplicate_file(tmp_path):
    # Create sample file
    src = tmp_path / "sample.txt"
    src.write_text("hello world")

    dst_dir = tmp_path / "out"

    result = duplicate_file(src, dst_dir, count=3)

    assert len(result) == 3
    assert all(p.exists() for p in result)

    # Check generated names
    assert result[0].name == "sample_copy1.txt"
    assert result[1].name == "sample_copy2.txt"
    assert result[2].name == "sample_copy3.txt"

    # Check file content preserved
    for f in result:
        assert f.read_text() == "hello world"


def test_duplicate_invalid_count(tmp_path):
    src = tmp_path / "sample.txt"
    src.write_text("x")

    with pytest.raises(ValueError):
        duplicate_file(src, tmp_path, count=0)
