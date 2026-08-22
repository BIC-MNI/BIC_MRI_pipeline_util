import shutil
from pathlib import Path

import pydicom
import pydicom.misc

from bic_util.fs import count_all_dir_files
from bic_util.print import get_progress_printer


def get_dicom_study_patient_name(dicom_study_path: Path) -> str | None:
    """
    Look for a DICOM file in a DICOM study and return the patient name of that file.
    """

    for file_path in dicom_study_path.rglob('*'):
        if not file_path.is_file():
            continue

        if pydicom.misc.is_dicom(file_path):
            ds = pydicom.dcmread(file_path)  # type: ignore
            return str(ds.PatientName)

    return None


def copy_dicom_dir_patch_patient_name(
    src_dicom_dir_path: Path,
    dst_dicom_dir_path: Path,
    patient_name: str,
):
    """
    Copy a DICOM directory while renaming its DICOM patient name attribute.
    """

    progress = get_progress_printer(count_all_dir_files(src_dicom_dir_path))

    for src_file_path in src_dicom_dir_path.rglob('*'):
        if not src_file_path.is_file():
            continue

        next(progress)

        rel_path = src_file_path.relative_to(src_dicom_dir_path)
        dst_file_path = dst_dicom_dir_path / rel_path

        # Create parent directory if it doesn't exist
        dst_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Get relative path and construct destination
        rel_path = src_file_path.relative_to(src_dicom_dir_path)
        dst_file_path = dst_dicom_dir_path / rel_path

        # Create parent directory if it doesn't exist
        dst_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Patch and copy files and DICOMs
        if not pydicom.misc.is_dicom(str(src_file_path)):
            shutil.copyfile(src_file_path, dst_file_path)
            continue

        ds = pydicom.dcmread(src_file_path)  # type: ignore
        ds.PatientName = patient_name
        ds.save_as(dst_file_path)
