from pathlib import Path
import shutil
from .utils import validate_file

def duplicate_file(src_path: Path, dst_dir: Path, count: int = 1):
    validate_file(src_path)

    if count < 1:
        raise ValueError("count must be >= 1")

    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for i in range(1, count + 1):
        new_name = f"{src_path.stem}_copy{i}{src_path.suffix}"
        dst_file = dst_dir / new_name

        shutil.copy2(src_path, dst_file)
        results.append(dst_file)

    return results
