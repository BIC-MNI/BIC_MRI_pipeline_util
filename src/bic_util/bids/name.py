import re
from dataclasses import dataclass
from re import Match, Pattern

BIDS_LABEL_ORDER = [
    'sub',
    'ses',
    'task',
    'acq',
    'ce',
    'rec',
    'inv',
    'mt',
    'dir',
    'run',
    'echo',
    'part',
    'chunk',
    'desc',
]

_BIDS_LABEL_ORDER_MAP = {label: index for index, label in enumerate(BIDS_LABEL_ORDER)}


@dataclass
class BidsName:
    """The entities and extension that make up a BIDS file name."""

    entries: dict[str, str | None]
    extension: str | None

    @staticmethod
    def from_string(name_string: str) -> 'BidsName':
        """Parse a BIDS file name."""

        extension_index = name_string.find('.')
        if extension_index != -1:
            extension = name_string[extension_index + 1:]
            name_string = name_string[:extension_index]
        else:
            extension = None

        entries: dict[str, str | None] = {}
        for entry_string in name_string.split('_'):
            label_value = entry_string.split('-', maxsplit=1)
            label = label_value[0]
            value = label_value[1] if len(label_value) == 2 else None
            entries[label] = value

        return BidsName(entries, extension)

    def __str__(self) -> str:
        """Serialize the BIDS file name in canonical entity order."""

        entries = sorted(self.entries.items(), key=lambda entry: _bids_label_key(entry[0]))
        entry_strings = [label if value is None else f'{label}-{value}' for label, value in entries]
        name_string = '_'.join(entry_strings)

        if self.extension is not None:
            name_string += f'.{self.extension}'

        return name_string

    def has(self, label: str) -> bool:
        """Return whether the file name has an entity or suffix label."""

        return label in self.entries

    def has_value(self, label: str, value: str | None) -> bool:
        """Return whether the file name has a label with the given value."""

        return label in self.entries and self.entries[label] == value

    def get(self, label: str) -> str | None:
        """Return the value associated with a label."""

        return self.entries[label]

    def match(self, pattern: str | Pattern[str]) -> Match[str] | None:
        """Return the first label matching a regular expression."""

        for label in self.entries:
            match = re.match(pattern, label)
            if match is not None:
                return match

        return None

    def add(self, label: str, value: str | None = None):
        """Add or replace a label and its value."""

        self.entries[label] = value

    def remove(self, label: str):
        """Remove a label and its value."""

        self.entries.pop(label)


def _bids_label_key(label: str) -> int:
    return _BIDS_LABEL_ORDER_MAP.get(label, len(_BIDS_LABEL_ORDER_MAP))
