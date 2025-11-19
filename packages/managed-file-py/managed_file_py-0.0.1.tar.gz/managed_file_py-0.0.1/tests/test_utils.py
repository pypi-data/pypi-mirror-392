import pytest
from pathlib import Path
from tools_managed_file.utils import validate_file, safe_filename


def test_validate_file_wrong_type():
    with pytest.raises(TypeError):
        validate_file("not_a_path")


def test_validate_file_not_exists(tmp_path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        validate_file(missing)


def test_validate_file_not_a_file(tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()

    with pytest.raises(ValueError):
        validate_file(folder)


def test_safe_filename():
    unsafe = 'te/st:fi*le?.txt'
    safe = safe_filename(unsafe)
    assert "/" not in safe
    assert ":" not in safe
    assert "*" not in safe
    assert "?" not in safe
