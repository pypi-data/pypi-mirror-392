# core/datafake_generator.py
from pathlib import Path
from core.base_generator import BaseGenerator
from core.exporters import Exporter
import os
import shutil


def clean_pycache(path='.'):
    for root, dirs, files in os.walk(path):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))


class DataFakeGenerator:
    """
    Unified main entrypoint for the DataFakeGenerator project.

    Usage:
        from core.datafake_generator import DataFakeGenerator

        schema = [...]
        dfg = DataFakeGenerator(schema)
        dfg.many(100).export("users", "output", formats=["csv", "json"])
    """

    def __init__(self, schema: list[dict]):
        self.generator = BaseGenerator(schema)
        self._data = None

    def many(self, n: int):
        """Generate multiple fake records."""
        self._data = self.generator.generate_many(n)
        clean_pycache()
        return self

    def one(self):
        """Generate a single fake record."""
        self._data = [self.generator.generate_many(1)[0]]
        clean_pycache()
        return self

    @property
    def data(self):
        """Access generated data."""
        if self._data is None:
            raise ValueError(
                "No data generated yet. Use .one() or .many() first.")
        return self._data

    def export(
        self,
        table_name: str,
        output_dir: str = "output",
        formats: list[str] | None = None,
        create_table: bool = True,
    ):
        """Export generated data in one or more formats."""
        if not self._data:
            raise ValueError(
                "No data to export. Generate data first using .one() or .many().")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        formats = formats or [
            "csv",
            "json",
            "sql",
            "cql",
            "firebase",
            "excel",
            "xml",
            "dbunit",
            "parquet",
            "duckdb",
        ]

        for fmt in formats:
            match fmt.lower():
                case "csv":
                    Exporter.to_csv(
                        self._data, f"{output_dir}/{table_name}.csv")
                case "json":
                    Exporter.to_json(
                        self._data, f"{output_dir}/{table_name}.json")
                case "sql":
                    Exporter.to_sql(
                        self._data, table_name, f"{output_dir}/{table_name}.sql", create_table
                    )
                case "cql":
                    Exporter.to_cql(
                        self._data,
                        keyspace=table_name,
                        table_name=table_name,
                        file_path=f"{output_dir}/{table_name}.cql",
                    )
                case "firebase":
                    Exporter.to_firebase(
                        self._data, f"{output_dir}/{table_name}_firebase.json")
                case "excel":
                    Exporter.to_excel(
                        self._data, f"{output_dir}/{table_name}.xlsx")
                case "xml":
                    Exporter.to_xml(
                        self._data,
                        f"{output_dir}/{table_name}.xml",
                        root_element="root",
                        record_element="record",
                    )
                case "dbunit":
                    Exporter.to_dbunit_xml(
                        self._data, f"{output_dir}/{table_name}_dbunit.xml", table_name
                    )
                case "parquet":
                    Exporter.to_parquet(
                        self._data, f"{output_dir}/{table_name}.parquet")
                case "duckdb":
                    Exporter.to_duckdb(
                        self._data, f"{output_dir}/{table_name}.duckdb", table_name)
                case _:
                    print(f"Unknown export format: {fmt}")

        print(f"Export complete for table '{table_name}' → {output_dir}/")
        return self
