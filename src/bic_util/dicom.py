import os
import shutil

import pydicom
import pydicom.misc

from bic_util.fs import count_all_dir_files
from bic_util.print import get_progress_printer


def get_dicom_study_patient_name(dicom_study_path: str) -> str | None:
    """
    Look for a DICOM file in a DICOM study and return the patient name of that file.
    """

    for dir_path, _, file_names in os.walk(dicom_study_path):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)

            if pydicom.misc.is_dicom(file_path):
                ds = pydicom.dcmread(file_path)  # type: ignore
                return str(ds.PatientName)

    return None


def copy_dicom_dir_patch_patient_name(
    src_dicom_dir_path: str,
    dst_dicom_dir_path: str,
    patient_name: str,
) -> None:
    """
    Copy a DICOM directory while renaming its DICOM patient name attribute.
    """

    progress = get_progress_printer(count_all_dir_files(src_dicom_dir_path))

    for src_dir_path, _, src_file_names in os.walk(src_dicom_dir_path):
        dir_rel_path = os.path.relpath(src_dir_path, src_dicom_dir_path)
        dst_dir_path = os.path.join(dst_dicom_dir_path, dir_rel_path)

        # Copy directory structure
        os.makedirs(dst_dir_path)

        # Patch and copy files and DICOMs
        for src_file_name in src_file_names:
            next(progress)
            src_file_path = os.path.join(src_dir_path, src_file_name)
            dst_file_path = os.path.join(dst_dir_path, src_file_name)

            if not pydicom.misc.is_dicom(src_file_path):
                shutil.copyfile(src_file_path, dst_file_path)
                continue

            ds = pydicom.dcmread(src_file_path)  # type: ignore
            ds.PatientName = patient_name
            ds.save_as(dst_file_path)
