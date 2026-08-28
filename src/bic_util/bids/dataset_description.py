import json
from pathlib import Path
from typing import cast


class DatasetDescriptionError(ValueError):
    """Raised when a dataset_description.json file cannot be safely handled."""


def read_dataset_description(file_path: Path) -> dict[str, object]:
    """Read and validate a BIDS dataset_description.json object."""

    try:
        with file_path.open(encoding='utf-8') as file:
            value: object = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetDescriptionError(f"Cannot read valid JSON from '{file_path}': {error}") from error

    if not isinstance(value, dict):
        raise DatasetDescriptionError(f"Expected the root of '{file_path}' to be a JSON object.")

    return cast(dict[str, object], value)


def write_dataset_description(file_path: Path, dataset_description: dict[str, object]):
    """Write a BIDS dataset_description.json object."""

    try:
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(dataset_description, file, indent=4, ensure_ascii=False)
            file.write('\n')
    except OSError as error:
        raise DatasetDescriptionError(f"Cannot write '{file_path}': {error}") from error


def get_generated_by(value: object | None) -> list[dict[str, object]]:
    """Validate and return the entries of a GeneratedBy value."""

    if value is None:
        return []
    if not isinstance(value, list):
        raise DatasetDescriptionError("Expected 'GeneratedBy' in 'dataset_description.json' to be an array.")

    generated_by: list[dict[str, object]] = []
    for entry in cast(list[object], value):
        if not isinstance(entry, dict):
            raise DatasetDescriptionError(
                "Expected every entry in 'GeneratedBy' in 'dataset_description.json' to be an object."
            )
        generated_by.append(cast(dict[str, object], entry))

    return generated_by


def upsert_generated_by_entry(generated_by: list[dict[str, object]], managed_values: dict[str, object]):
    """Add or update a GeneratedBy entry, identified by its Name."""

    name = managed_values.get('Name')
    if not isinstance(name, str):
        raise DatasetDescriptionError("Expected a managed 'GeneratedBy' entry to have a string 'Name'.")

    for entry in generated_by:
        if entry.get('Name') == name:
            entry.update(managed_values)
            return

    generated_by.append(managed_values)
