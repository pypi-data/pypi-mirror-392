import json
import csv
from pathlib import Path


class DatasetManager:
    _cache = {}
    _base_path = Path(__file__).resolve().parent.parent / "external_datasets"

    @classmethod
    def load(cls, name: str):
        if name in cls._cache:
            return cls._cache[name]

        for ext in ["json", "csv"]:
            file_path = cls._base_path / ext / f"{name}.{ext}"
            if file_path.exists():
                data = cls._load_file(file_path)
                cls._cache[name] = data
                return data

        raise FileNotFoundError(
            f"Dataset '{name}' not found in {cls._base_path}")

    @staticmethod
    def _load_file(path: Path):
        if path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif path.suffix == ".csv":
            with open(path, "r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        else:
            raise ValueError(f"Unsupported file type: {path}")
