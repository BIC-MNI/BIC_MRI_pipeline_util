def format_file_size(file_size: int) -> str:
    """
    Convert a file size in bytes to a string in gigabytes with two decimal places.
    """

    gigabytes = file_size / 1_000_000_000
    return f"{gigabytes:.2f} GB"
