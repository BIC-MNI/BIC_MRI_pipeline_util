import importlib.util
import os
from typing import Any

from bic_util.fs import require_readable_file
from bic_util.print import print_error_exit


def load_config_module(file_name: str) -> Any:
    """
    Load a configuration file as a Python module.
    """

    config_fir_path = os.environ.get('CONFIGPATH')
    if config_fir_path is None:
        print_error_exit("Configuration directory path environment variable not found.")

    config_file_path = os.path.join(config_fir_path, file_name)
    if not os.path.exists(config_file_path):
        print_error_exit(f"Configuration file '{file_name}' not found in the configuration directory.")

    require_readable_file(config_file_path)

    specification = importlib.util.spec_from_file_location('config', config_file_path)
    if specification is None or specification.loader is None:
        print_error_exit(f"Cannot get the module specification for configuration file '{file_name}'")

    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module
