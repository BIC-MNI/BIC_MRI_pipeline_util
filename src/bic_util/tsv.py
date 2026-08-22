import csv
from pathlib import Path
from typing import cast


class TabularMetadataError(ValueError):
    """
    Error raised when a BIDS tabular metadata file cannot be safely updated.
    """


def upsert_tsv_row(file_path: Path, key_columns: str | tuple[str, ...], values: dict[str, str]) -> None:
    """
    Insert or update a row in a TSV file and sort all rows by their key.

    Existing columns and values are preserved. New columns are appended to the existing header,
    and missing values are represented by ``n/a``. An incoming ``n/a`` never replaces an existing
    concrete value.
    """

    if isinstance(key_columns, str):
        key_columns = (key_columns,)

    key = tuple(values[column] for column in key_columns)

    if file_path.exists():
        with file_path.open(encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file, delimiter='\t')
            columns = list(reader.fieldnames or [])
            rows = [cast(dict[str, str], row) for row in reader]

        if columns[:len(key_columns)] != list(key_columns):
            raise TabularMetadataError(f"Expected the first columns of '{file_path}' to be {key_columns}.")
    else:
        columns = list(key_columns)
        rows: list[dict[str, str]] = []

    columns.extend(column for column in values if column not in columns)

    rows_by_key: dict[tuple[str, ...], dict[str, str]] = {}
    for row in rows:
        row_key = tuple(row[column] for column in key_columns)
        if row_key in rows_by_key:
            raise TabularMetadataError(f"Duplicate key {row_key} in '{file_path}'.")
        rows_by_key[row_key] = row

    row = rows_by_key.get(key, {})
    for column, value in values.items():
        if value != 'n/a' or row.get(column, 'n/a') == 'n/a':
            row[column] = value
    rows_by_key[key] = row

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(
            {column: row.get(column, 'n/a') or 'n/a' for column in columns}
            for _, row in sorted(rows_by_key.items())
        )
