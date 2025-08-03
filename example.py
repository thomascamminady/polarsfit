#!/usr/bin/env python3
"""
Simple example of reading FIT files with polarsfit.

This example demonstrates basic usage of polarsfit to read FIT files
and optionally compare with CSV data.
"""

import os
import sys

import polars as pl

import polarsfit


def main():
    # Check command line arguments for FIT file path
    if len(sys.argv) < 2:
        print("Usage: python example.py <path_to_fit_file> [path_to_csv_file]")
        print("\nExample:")
        print("  python example.py workout.fit")
        print("  python example.py workout.fit workout.csv")
        return

    fit_file = sys.argv[1]
    csv_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if FIT file exists
    if not os.path.exists(fit_file):
        print(f"Error: FIT file '{fit_file}' does not exist")
        return

    print("=== Reading FIT file ===")
    print(f"File: {fit_file}")

    try:
        # Read FIT file with default field mapping
        df_fit = polarsfit.read_recordmesgs(fit_file)
        print(f"FIT data shape: {df_fit.shape}")
        print(f"FIT columns: {df_fit.columns}")
        print("\nFirst few rows of FIT data:")
        print(df_fit.head())

        print("\n=== Available message types in FIT file ===")
        message_types = polarsfit.get_message_types(fit_file)
        print(f"Message types: {message_types}")

        # Try reading different message types
        print("\n=== Reading different message types ===")
        for msg_type in message_types:
            try:
                data = polarsfit.read_data(fit_file, msg_type)
                print(f"{msg_type}: {data.shape}")
            except Exception as e:
                print(f"{msg_type}: Error - {e}")

        # CSV comparison if provided
        if csv_file:
            print("\n=== Comparing with CSV ===")
            try:
                if not os.path.exists(csv_file):
                    print(f"Warning: CSV file '{csv_file}' does not exist")
                    return

                # Read CSV file for comparison
                df_csv = pl.read_csv(csv_file)
                print(f"CSV data shape: {df_csv.shape}")
                print(f"CSV columns: {df_csv.columns}")

                # Basic comparison
                print("\nShape comparison:")
                print(f"  FIT: {df_fit.shape}")
                print(f"  CSV: {df_csv.shape}")

                # Check if we have any common columns
                common_cols = set(df_fit.columns) & set(df_csv.columns)
                if common_cols:
                    print(f"Common columns: {common_cols}")
                else:
                    print("No common column names found")

            except Exception as e:
                print(f"Could not read CSV file: {e}")

    except Exception as e:
        print(f"Error reading FIT file: {e}")


if __name__ == "__main__":
    main()
