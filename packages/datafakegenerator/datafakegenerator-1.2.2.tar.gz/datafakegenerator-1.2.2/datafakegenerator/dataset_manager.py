from pathlib import Path
import importlib.resources as pkg_resources
import json
import csv


class DatasetManager:
    _cache = {}

    @classmethod
    def _get_base_path(cls):
        with pkg_resources.path("datafakegenerator", "external_datasets") as p:
            return p

    @classmethod
    def load(cls, name: str):
        if name in cls._cache:
            return cls._cache[name]

        base_path = cls._get_base_path()
        for ext in ["json", "csv"]:
            file_path = base_path / ext / f"{name}.{ext}"
            if file_path.exists():
                data = cls._load_file(file_path)
                cls._cache[name] = data
                return data

        raise FileNotFoundError(f"Dataset '{name}' not found in {base_path}")

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
