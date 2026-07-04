import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BidsSession:
    """
    A pair of subject and session labels found in a BIDS dataset.
    """

    subject: str
    session: str


def get_bids_sessions(bids_path: Path) -> list[BidsSession]:
    """
    Get the list of subject and session pairs present in a BIDS dataset.
    """

    bids_sessions: list[BidsSession] = []

    for subject_dir_path in bids_path.iterdir():
        if not subject_dir_path.is_dir():
            continue

        subject_match = re.search(r'^sub-(.*)', subject_dir_path.name)
        if not subject_match:
            continue

        for session_dir_path in subject_dir_path.iterdir():
            if not session_dir_path.is_dir():
                continue

            session_match = re.search(r'ses-(.*)', session_dir_path.name)
            if not session_match:
                continue

            bids_sessions.append(BidsSession(
                subject=subject_match.group(1),
                session=session_match.group(1),
            ))

    return bids_sessions


def copy_bids_sessions(input_bids_path: Path, output_bids_path: Path, bids_sessions: list[BidsSession]):
    """
    Copy a BIDS dataset while filtering the acquisition files that do not belong to the specified
    subject and session pairs.
    """

    for file_1_path in input_bids_path.iterdir():
        subject_match = re.search(r'sub-(.+)', file_1_path.name)
        if subject_match:
            subject_label = subject_match.group(1)
            if not any(subject_label == bids_session.subject for bids_session in bids_sessions):
                continue

        file_1_output_path = output_bids_path / file_1_path.name

        if not file_1_path.is_dir():
            shutil.copy(file_1_path, file_1_output_path)
            continue

        file_1_output_path.mkdir()

        for file_2_path in file_1_path.iterdir():
            session_match = re.search(r'ses-(.*)', file_2_path.name)
            if session_match:
                session_label = session_match.group(1)
                if not any(session_label == bids_session.session for bids_session in bids_sessions):
                    continue

            file_2_output_path = output_bids_path / file_1_path.name / file_2_path.name

            if not file_2_path.is_dir():
                shutil.copy(file_2_path, file_2_output_path)
                continue

            shutil.copytree(file_2_path, file_2_output_path)

    copy_bids_participants_tsv_sessions(input_bids_path, output_bids_path, bids_sessions)


def copy_bids_participants_tsv_sessions(
    input_bids_path: Path,
    output_bids_path: Path,
    bids_sessions: list[BidsSession],
):
    """
    Copy a BIDS `participants.tsv` file while retaining only the subjects that are specified in the
    given BIDS subject and session pairs.
    """

    bids_subject_labels = list(map(lambda bids_session: bids_session.subject, bids_sessions))

    input_participants_path  = input_bids_path  / 'participants.tsv'
    output_participants_path = output_bids_path / 'participants.tsv'

    if not input_participants_path.exists():
        return

    with input_participants_path.open() as input_participants_file:
        reader = csv.DictReader(input_participants_file.readlines(), delimiter='\t')

    if reader.fieldnames is None:
        return

    if 'participant_id' not in reader.fieldnames:
        return

    with output_participants_path.open('w') as output_participants_file:
        writer = csv.DictWriter(output_participants_file, fieldnames=reader.fieldnames, delimiter='\t')
        writer.writeheader()
        for row in reader:
            bids_subject_label = re.sub(r'^sub-', '', row['participant_id'])
            if bids_subject_label in bids_subject_labels:
                writer.writerow(row)


def has_bids_session(bids_path: Path, bids_session: BidsSession) -> bool:
    """
    Check whether a subject and session pair exists in a BIDS dataset.
    """

    bids_session_dir_path = bids_path / f'sub-{bids_session.subject}' / f'ses-{bids_session.session}'
    return bids_session_dir_path.exists()
