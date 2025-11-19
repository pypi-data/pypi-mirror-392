import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from openpyxl import Workbook
import pandas as pd
import pyarrow as pa
import duckdb


class Exporter:

    @staticmethod
    def to_csv(data: list[dict], file_path: str):
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV saved to: {file_path}")

    @staticmethod
    def to_tsv(data: list[dict], file_path: str):
        """Export data to Tab-Delimited TSV."""
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, fieldnames=data[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(data)
        print(f"TSV saved to: {file_path}")

    @staticmethod
    def to_json(data: list[dict], file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"JSON saved to: {file_path}")

    @staticmethod
    def to_sql(data: list[dict], table_name: str, file_path: str, create_table: bool):
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        columns = list(data[0].keys())

        def format_sql_value(v):
            if v is None:
                return "NULL"
            if isinstance(v, bool):
                return "TRUE" if v else "FALSE"
            if isinstance(v, (int,)) and not isinstance(v, bool):
                return str(v)
            if isinstance(v, float):
                return repr(v)
            s = str(v)
            return "'" + s.replace("'", "''") + "'"

        first_row = data[0]
        type_map = {}
        for col, val in first_row.items():
            if isinstance(val, bool):
                type_map[col] = "BOOLEAN"
            elif isinstance(val, int) and not isinstance(val, bool):
                type_map[col] = "INTEGER"
            elif isinstance(val, float):
                type_map[col] = "REAL"
            else:
                type_map[col] = "TEXT"

        with open(file_path, "w", encoding="utf-8") as f:
            if create_table:
                cols_def = ",\n    ".join(
                    f"{col} {type_map[col]}" for col in columns)
                f.write(
                    f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {cols_def}\n);\n\n")

            cols_str = ", ".join(columns)
            for row in data:
                values = ", ".join(format_sql_value(row.get(col))
                                   for col in columns)
                f.write(
                    f"INSERT INTO {table_name} ({cols_str}) VALUES ({values});\n")

        print(f"SQL file saved to: {file_path}")

    @staticmethod
    def to_cql(data: list[dict], keyspace: str, table_name: str, file_path: str, create_table: bool = True):
        """Export data as Cassandra CQL script."""
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        columns = list(data[0].keys())

        type_map = {}
        for col, val in data[0].items():
            if isinstance(val, bool):
                type_map[col] = "boolean"
            elif isinstance(val, int):
                type_map[col] = "int"
            elif isinstance(val, float):
                type_map[col] = "double"
            else:
                type_map[col] = "text"

        def format_cql_value(v):
            if v is None:
                return "null"
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, (int, float)):
                return str(v)
            s = str(v)
            return "'" + s.replace("'", "''") + "'"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"USE {keyspace};\n\n")
            if create_table:
                cols_def = ",\n    ".join(
                    f"{col} {type_map[col]}" for col in columns)
                f.write(
                    f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {cols_def},\n    PRIMARY KEY ({columns[0]})\n);\n\n")
            for row in data:
                cols_str = ", ".join(columns)
                values = ", ".join(format_cql_value(row.get(c))
                                   for c in columns)
                f.write(
                    f"INSERT INTO {table_name} ({cols_str}) VALUES ({values});\n")
        print(f"CQL saved to: {file_path}")

    @staticmethod
    def to_firebase(data: list[dict], file_path: str):
        """Export data as Firebase-style JSON (keyed by unique id if present)."""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        if not data:
            raise ValueError("No data to export.")

        # Use `id` or first key as Firebase node key
        key_field = "id" if "id" in data[0] else list(data[0].keys())[0]
        firebase_data = {str(row[key_field]): row for row in data}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(firebase_data, f, indent=2)
        print(f"Firebase JSON saved to: {file_path}")

    @staticmethod
    def to_excel(data: list[dict], file_path: str, sheet_name: str = "Sheet1"):
        """Export data to Excel workbook."""
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row.get(h) for h in headers])
        wb.save(file_path)
        print(f"Excel saved to: {file_path}")

    @staticmethod
    def to_xml(data: list[dict], file_path: str, root_element: str = "root", record_element: str = "record"):
        """Export data to generic XML with custom root/record element names."""
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        root = ET.Element(root_element)
        for row in data:
            rec = ET.SubElement(root, record_element)
            for k, v in row.items():
                el = ET.SubElement(rec, k)
                el.text = "" if v is None else str(v)

        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f"XML saved to: {file_path}")

    @staticmethod
    def to_dbunit_xml(data: list[dict], file_path: str, table_name: str):
        """Export data to DBUnit-compatible XML format."""
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        dataset = ET.Element("dataset")
        for row in data:
            table_el = ET.SubElement(dataset, table_name)
            for k, v in row.items():
                if v is not None:
                    table_el.set(k, str(v))
        tree = ET.ElementTree(dataset)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)
        print(f"DBUnit XML saved to: {file_path}")

    @staticmethod
    def to_parquet(data: list[dict], file_path: str):
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(data)
        df.to_parquet(file_path, index=False)
        print(f"Parquet file saved to: {file_path}")

    @staticmethod
    def to_duckdb(data: list[dict], file_path: str, table_name: str = "data"):
        if not data:
            raise ValueError("No data to export.")
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame(data)
        con = duckdb.connect(file_path)
        con.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")

        con.close()
        print(f"DuckDB saved at: {file_path} (table: {table_name})")
