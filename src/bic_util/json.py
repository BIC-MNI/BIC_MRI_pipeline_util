import json
from pathlib import Path
from typing import Any


def update_json(json_path: Path, new_data: dict[str, Any]):
    """
    Update a JSON file with new data, overwriting existing keys if they already exist. Raise an
    exception if the JSON file does not exist or cannot be read or written.
    """

    # Read the JSON file.
    with open(json_path) as json_file:
        data = json.load(json_file)

    # Update the JSON data with the new data.
    data.update(new_data)

    # Write the updated data back to the JSON file.
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
