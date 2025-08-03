"""Type stubs for the internal Rust module."""


import polars as pl

def read_recordmesgs(file_path: str) -> pl.DataFrame:
    """Read record messages from a FIT file.

    Args:
        file_path: Path to the FIT file to read

    Returns
    -------
        Polars DataFrame containing the record messages
    """
    ...
