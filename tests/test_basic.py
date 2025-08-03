#!/usr/bin/env python3

import polars as pl

import polarsfit


def test_read_recordmesgs():
    """Test reading record messages from a .fit file"""
    try:
        # Use the existing .fit file in the tests/data directory
        fit_file = "tests/data/30378-142636426.fit"

        print(f"Reading FIT file: {fit_file}")
        df = polarsfit.read_recordmesgs(fit_file)

        print(f"Successfully read DataFrame with shape: {df.shape}")
        print(f"Columns: {df.columns}")
        print("\nFirst few rows:")
        print(df.head())

        print("\nColumn types:")
        print(df.dtypes)

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_read_recordmesgs()
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")
