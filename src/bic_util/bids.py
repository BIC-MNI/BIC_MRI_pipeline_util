import csv
import os
import re
import shutil
from dataclasses import dataclass


@dataclass
class BidsSession:
    """
    A pair of subject and session labels found in a BIDS dataset.
    """

    subject: str
    session: str


def get_bids_sessions(bids_path: str) -> list[BidsSession]:
    """
    Get the list of subject and session pairs present in a BIDS dataset.
    """

    bids_sessions: list[BidsSession] = []

    for file_1 in os.scandir(bids_path):
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

            bids_sessions.append(BidsSession(
                subject = subject_match.group(1),
                session = session_match.group(1),
            ))

    return bids_sessions


def copy_bids_sessions(input_bids_path: str, output_bids_path: str, bids_sessions: list[BidsSession]):
    """
    Copy a BIDS dataset while filtering the acquisition files that do not belong to the specified
    subject and session pairs.
    """

    for file_1 in os.scandir(input_bids_path):
        subject_match = re.search(r'sub-(.+)', file_1.name)
        if subject_match:
            subject_label = subject_match.group(1)
            if not any(subject_label == bids_session.subject for bids_session in bids_sessions):
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
                if not any(session_label == bids_session.session for bids_session in bids_sessions):
                    continue

            file_2_output_path = os.path.join(output_bids_path, file_1.name, file_2.name)

            if not os.path.isdir(file_2.path):
                shutil.copy(file_2.path, file_2_output_path)
                continue

            shutil.copytree(file_2.path, file_2_output_path)

    copy_bids_participants_tsv_sessions(input_bids_path, output_bids_path, bids_sessions)


def copy_bids_participants_tsv_sessions(input_bids_path: str, output_bids_path: str, bids_sessions: list[BidsSession]):
    """
    Copy a BIDS `participants.tsv` file while retaining only the subjects that are specified in the
    given BIDS subject and session pairs.
    """

    bids_subject_labels = list(map(lambda bids_session: bids_session.subject, bids_sessions))

    input_participants_path  = os.path.join(input_bids_path,  'participants.tsv')
    output_participants_path = os.path.join(output_bids_path, 'participants.tsv')

    if not os.path.exists(input_participants_path):
        return

    with open(input_participants_path) as input_participants_file:
        reader = csv.DictReader(input_participants_file.readlines(), delimiter='\t')

    if reader.fieldnames is None:
        return

    if 'participant_id' not in reader.fieldnames:
        return

    with open(output_participants_path, 'w') as output_participants_file:
        writer = csv.DictWriter(output_participants_file, fieldnames=reader.fieldnames, delimiter='\t')
        writer.writeheader()
        for row in reader:
            bids_subject_label = re.sub(r'^sub-', '', row['participant_id'])
            if bids_subject_label in bids_subject_labels:
                writer.writerow(row)


def has_bids_session(bids_path: str, bids_session: BidsSession) -> bool:
    """
    Check whether a subject and session pair exists in a BIDS dataset.
    """

    bids_session_dir_path = os.path.join(bids_path, f'sub-{bids_session.subject}', f'ses-{bids_session.session}')
    return os.path.exists(bids_session_dir_path)
