import importlib.util
import os
from typing import Any

from bic_util.print import print_error_exit


def load_config_module(file_name: str) -> Any:
    """
    Load a configuration file as a Python module.
    """

    file_path = os.path.join(os.environ['CONFIGPATH'], file_name)
    specification = importlib.util.spec_from_file_location('config', file_path)
    if specification is None or specification.loader is None:
        print_error_exit(f'Cannot get the module specification for configuration file \'{file_name}\'')

    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module
