#!/usr/bin/env python3

import polars as pl

import polarsfit


def test_read_recordmesgs_with_mapping():
    """Test reading record messages with field name mapping."""
    try:
        # Use the existing .fit file in the tests/data directory
        fit_file = "tests/data/30378-142636426.fit"

        print(f"Reading FIT file: {fit_file}")
        df = polarsfit.read_recordmesgs(fit_file)

        print(f"Successfully read DataFrame with shape: {df.shape}")

        # Create a mapping for common FIT record message fields
        # Based on FIT SDK documentation
        field_mapping = {
            "field_253": "timestamp",
            "field_0": "position_lat",  # latitude in semicircles
            "field_1": "position_long",  # longitude in semicircles
            "field_2": "altitude",  # meters
            "field_3": "heart_rate",  # bpm
            "field_4": "cadence",  # rpm
            "field_5": "distance",  # meters
            "field_6": "speed",  # m/s
            "field_7": "power",  # watts
            "field_13": "temperature",  # degrees celsius
        }

        # Rename columns for ones we recognize
        df_renamed = df.select(
            [
                pl.col(old_name).alias(new_name)
                if old_name in df.columns
                else pl.lit(None).alias(new_name)
                for old_name, new_name in field_mapping.items()
            ]
            + [
                pl.col(col)
                for col in df.columns
                if col not in field_mapping.keys()
            ]
        )

        print("\nDataFrame with meaningful column names:")
        print(
            df_renamed.select(
                [
                    "timestamp",
                    "position_lat",
                    "position_long",
                    "distance",
                    "heart_rate",
                    "power",
                ]
            ).head()
        )

        # Convert lat/long from semicircles to degrees
        if (
            "position_lat" in df_renamed.columns
            and "position_long" in df_renamed.columns
        ):
            df_geo = df_renamed.with_columns(
                [
                    (pl.col("position_lat") * 180.0 / 2**31).alias(
                        "latitude_deg"
                    ),
                    (pl.col("position_long") * 180.0 / 2**31).alias(
                        "longitude_deg"
                    ),
                ]
            )

            print("\nWith geographic coordinates converted to degrees:")
            print(
                df_geo.select(
                    [
                        "timestamp",
                        "latitude_deg",
                        "longitude_deg",
                        "distance",
                        "heart_rate",
                        "power",
                    ]
                ).head()
            )

        print(
            f"\nTotal distance: {df.select(pl.col('field_5').max()).item()} meters"
        )
        if "field_3" in df.columns:
            print(
                f"Average heart rate: {df.select(pl.col('field_3').mean()).item():.1f} bpm"
            )
        if "field_7" in df.columns:
            avg_power = df.select(
                pl.col("field_7").filter(pl.col("field_7") > 0).mean()
            ).item()
            if avg_power:
                print(f"Average power: {avg_power:.1f} watts")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_read_recordmesgs_with_mapping()
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")
