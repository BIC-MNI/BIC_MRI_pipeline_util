import os
import re
import shutil
from dataclasses import dataclass


@dataclass
class BidsSubjectSession:
    """
    A pair of subject and session labels found in a BIDS dataset.
    """

    subject: str
    session: str


def get_bids_subject_session_pairs(bids_dir_path: str) -> list[BidsSubjectSession]:
    """
    Get the list of subject and session pairs present in a BIDS dataset.
    """

    pairs: list[BidsSubjectSession] = []

    for file_1 in os.scandir(bids_dir_path):
        subject_match = re.search(r'^sub-(.*)', file_1.name)
        if not subject_match:
            continue

        if not os.path.isdir(file_1.path):
            continue

        for file_2 in os.scandir(file_1.path):
            session_match = re.search(r'ses-(.*)', file_2.name)
            if not session_match:
                continue

            if not os.path.isdir(file_2.path):
                continue

            pairs.append(BidsSubjectSession(
                subject = subject_match.group(1),
                session = session_match.group(1),
            ))

    return pairs


def filter_bids_subject_session_pairs(input_bids_path: str, output_bids_path: str, pairs: list[BidsSubjectSession]):
    """
    Filter a BIDS dataset by copying only the files related to the whole BIDS dataset or the
    specified subject and session pairs to the output directory.
    """

    for file_1 in os.scandir(input_bids_path):
        subject_match = re.search(r'sub-(.+)', file_1.name)
        if subject_match:
            subject_label = subject_match.group(1)
            if not any(subject_label == pair.subject for pair in pairs):
                continue

        file_1_output_path = os.path.join(output_bids_path, file_1.name)

        if not os.path.isdir(file_1.path):
            shutil.copy(file_1.path, file_1_output_path)
            continue

        os.mkdir(file_1_output_path)

        for file_2 in os.scandir(file_1.path):
            session_match = re.search(r'ses-(.*)', file_2.name)
            if session_match:
                session_label = session_match.group(1)
                if not any(session_label == pair.session for pair in pairs):
                    continue

            file_2_output_path = os.path.join(output_bids_path, file_1.name, file_2.name)

            if not os.path.isdir(file_2.path):
                shutil.copy(file_2.path, file_2_output_path)
                continue

            shutil.copytree(file_2.path, file_2_output_path)
