#!/usr/bin/env python3
"""
Comprehensive test comparing FIT and CSV data.

Tests that the FIT file parsing matches the corresponding CSV export.
"""

from pathlib import Path

import polars as pl
import pytest

import polarsfit


class TestFitCsvComparison:
    """Test class for comparing FIT parsing with CSV data."""

    @classmethod
    def setup_class(cls):
        """Set up test files and data."""
        cls.fit_file = Path("tests/data/30378-142636426.fit")
        cls.csv_file = Path(
            "tests/data/30378-Activity_2025-08-02_09-54_142636426.csv"
        )

        # Verify files exist
        if not cls.fit_file.exists():
            pytest.skip(f"FIT test file not found: {cls.fit_file}")
        if not cls.csv_file.exists():
            pytest.skip(f"CSV test file not found: {cls.csv_file}")

        # Load both datasets
        cls.df_fit = polarsfit.read_recordmesgs(str(cls.fit_file))
        cls.df_csv = pl.read_csv(str(cls.csv_file))

        # Clean up CSV data (remove empty trailing column)
        cls.df_csv = cls.df_csv.select(
            [col for col in cls.df_csv.columns if col.strip()]
        )

        # Define field mappings based on FIT SDK and data analysis
        cls.field_mapping = {
            "field_253": "timestamp",  # timestamp in FIT format
            "field_0": "Latitude",  # position_lat (semicircles to degrees)
            "field_1": "Longitude",  # position_long (semicircles to degrees)
            "field_5": "Distance",  # distance (centimeters to km conversion needed)
            "field_3": "HeartRate",  # heart_rate
            "field_4": "Cadence",  # cadence
            "field_7": "PowerOriginal",  # power
            "field_13": "Temperature",  # temperature
            "field_78": "AltitudeOriginal",  # enhanced_altitude
        }

    def test_file_existence(self):
        """Test that both test files exist."""
        assert self.fit_file.exists(), f"FIT file missing: {self.fit_file}"
        assert self.csv_file.exists(), f"CSV file missing: {self.csv_file}"

    def test_data_shapes(self):
        """Test that datasets have reasonable shapes."""
        print(f"FIT shape: {self.df_fit.shape}")
        print(f"CSV shape: {self.df_csv.shape}")

        # Both should have similar number of records (±2 records difference is acceptable)
        fit_rows, csv_rows = self.df_fit.shape[0], self.df_csv.shape[0]
        assert abs(fit_rows - csv_rows) <= 2, (
            f"Row count mismatch: FIT {fit_rows}, CSV {csv_rows}"
        )

        # FIT should have more columns (raw fields) than CSV (processed fields)
        assert self.df_fit.shape[1] >= self.df_csv.shape[1] - 5, (
            "FIT should have comparable or more fields"
        )

    def test_latitude_longitude_comparison(self):
        """Test that GPS coordinates match between FIT and CSV."""
        # FIT coordinates are already in degrees
        fit_lat = self.df_fit.select("field_0").to_series()
        fit_lon = self.df_fit.select("field_1").to_series()

        # CSV coordinates are in degrees
        csv_lat = self.df_csv.select("Latitude").to_series()
        csv_lon = self.df_csv.select("Longitude").to_series()

        # Compare first few records (allow small floating point differences)
        min_records = min(len(fit_lat), len(csv_lat))
        test_records = min(10, min_records)

        for i in range(test_records):
            lat_diff = abs(fit_lat[i] - csv_lat[i])
            lon_diff = abs(fit_lon[i] - csv_lon[i])

            # Allow for small precision differences
            assert lat_diff < 0.0001, (
                f"Latitude mismatch at record {i}: FIT {fit_lat[i]}, CSV {csv_lat[i]}"
            )
            assert lon_diff < 0.0001, (
                f"Longitude mismatch at record {i}: FIT {fit_lon[i]}, CSV {csv_lon[i]}"
            )

        print(f"✅ GPS coordinates match for {test_records} test records")

    def test_distance_comparison(self):
        """Test that distance values are consistent."""
        # FIT distance is in centimeters (1/100th meters)
        fit_distance_cm = self.df_fit.select("field_5").to_series()

        # CSV distance is in km
        csv_distance_km = self.df_csv.select("Distance").to_series()

        # Convert FIT centimeters to km for comparison: cm -> m -> km
        fit_distance_km = fit_distance_cm / 100000.0  # cm to km conversion

        # Compare a few middle records (avoid potential start/end differences)
        min_records = min(len(fit_distance_km), len(csv_distance_km))
        start_idx = min_records // 4
        test_records = min(10, min_records - start_idx)

        for i in range(start_idx, start_idx + test_records):
            fit_val = fit_distance_km[i]
            csv_val = csv_distance_km[i]

            # Allow for conversion precision differences (0.5% tolerance for distance)
            diff_percent = abs(fit_val - csv_val) / max(csv_val, 0.001) * 100
            assert diff_percent < 0.5, (
                f"Distance mismatch at record {i}: FIT {fit_val:.6f}km, CSV {csv_val:.6f}km"
            )

        print(f"✅ Distance values match for {test_records} test records")

    def test_heart_rate_comparison(self):
        """Test that heart rate values match."""
        if "field_3" not in self.df_fit.columns:
            pytest.skip("Heart rate field not found in FIT data")

        fit_hr = self.df_fit.select("field_3").to_series()
        csv_hr = self.df_csv.select("HeartRate").to_series()

        # Find records where both have heart rate data
        min_records = min(len(fit_hr), len(csv_hr))
        matches = 0

        for i in range(min_records):
            fit_val = fit_hr[i]
            csv_val = csv_hr[i]

            # Skip records where either is null/zero
            if fit_val == 0 or csv_val == 0:
                continue

            # Heart rate should match exactly or very closely
            assert abs(fit_val - csv_val) <= 1, (
                f"Heart rate mismatch at record {i}: FIT {fit_val}, CSV {csv_val}"
            )
            matches += 1

            if matches >= 10:  # Test first 10 valid records
                break

        assert matches > 0, "No valid heart rate records found for comparison"
        print(f"✅ Heart rate values match for {matches} test records")

    def test_temperature_comparison(self):
        """Test that temperature values are consistent."""
        if "field_13" not in self.df_fit.columns:
            pytest.skip("Temperature field not found in FIT data")

        fit_temp = self.df_fit.select("field_13").to_series()
        csv_temp = self.df_csv.select("Temperature").to_series()

        # Find records with temperature data
        min_records = min(len(fit_temp), len(csv_temp))
        matches = 0

        for i in range(min_records):
            fit_val = fit_temp[i]
            csv_val = csv_temp[i]

            # Skip if either is missing
            if fit_val == 0 or csv_val == 0:
                continue

            # Temperature should match exactly
            assert fit_val == csv_val, (
                f"Temperature mismatch at record {i}: FIT {fit_val}, CSV {csv_val}"
            )
            matches += 1

            if matches >= 5:  # Test first 5 valid records
                break

        if matches > 0:
            print(f"✅ Temperature values match for {matches} test records")
        else:
            print("⚠️ No temperature data found for comparison")

    def test_data_type_consistency(self):
        """Test that data types are appropriate."""
        # Test key fields have correct types
        expected_numeric_fields = ["field_0", "field_1", "field_5", "field_3"]

        for field in expected_numeric_fields:
            if field in self.df_fit.columns:
                dtype = self.df_fit[field].dtype
                assert dtype in [
                    pl.Float32,
                    pl.Float64,
                    pl.UInt32,
                    pl.Int32,
                    pl.UInt64,
                    pl.Int64,
                ], f"Field {field} should be numeric, got {dtype}"

        print("✅ Data types are appropriate")

    def test_timestamp_progression(self):
        """Test that timestamps progress logically."""
        if "field_253" not in self.df_fit.columns:
            pytest.skip("Timestamp field not found in FIT data")

        timestamps = self.df_fit.select("field_253").to_series()

        # Check that timestamps are generally increasing
        increasing_count = 0
        for i in range(1, min(100, len(timestamps))):
            if timestamps[i] >= timestamps[i - 1]:
                increasing_count += 1

        # Most timestamps should be increasing (allow for some irregularities)
        assert increasing_count > len(timestamps[:100]) * 0.9, (
            "Timestamps should generally increase"
        )
        print("✅ Timestamps progress logically")

    def test_field_coverage(self):
        """Test that mapped fields exist in FIT data."""
        missing_fields = []
        for fit_field, _csv_field in self.field_mapping.items():
            if fit_field not in self.df_fit.columns:
                missing_fields.append(fit_field)

        if missing_fields:
            print(f"⚠️ Missing fields in FIT data: {missing_fields}")

        # At least core fields should exist
        core_fields = ["field_253", "field_0", "field_1", "field_5"]
        for field in core_fields:
            assert field in self.df_fit.columns, (
                f"Core field {field} missing from FIT data"
            )

        print("✅ Core fields present in FIT data")

    def test_value_ranges(self):
        """Test that values are in reasonable ranges."""
        # Test GPS coordinates are in reasonable range
        if (
            "field_0" in self.df_fit.columns
            and "field_1" in self.df_fit.columns
        ):
            lat_series = self.df_fit.select("field_0").to_series()
            lon_series = self.df_fit.select("field_1").to_series()

            # Check latitude range (should be around 50 degrees for this data)
            lat_valid = lat_series.filter(lat_series != 0)
            if len(lat_valid) > 0:
                assert lat_valid.min() > 49 and lat_valid.max() < 52, (
                    "Latitude should be around 50°"
                )

            # Check longitude range (should be around 7 degrees for this data)
            lon_valid = lon_series.filter(lon_series != 0)
            if len(lon_valid) > 0:
                assert lon_valid.min() > 6 and lon_valid.max() < 8, (
                    "Longitude should be around 7°"
                )

        # Test heart rate is reasonable
        if "field_3" in self.df_fit.columns:
            hr_series = self.df_fit.select("field_3").to_series()
            hr_valid = hr_series.filter((hr_series > 0) & (hr_series < 255))
            if len(hr_valid) > 0:
                assert hr_valid.min() > 60 and hr_valid.max() < 200, (
                    "Heart rate should be between 60-200 bpm"
                )

        print("✅ Values are in reasonable ranges")


if __name__ == "__main__":
    # Run tests directly
    test_instance = TestFitCsvComparison()
    test_instance.setup_class()

    print("🧪 Running FIT vs CSV comparison tests...")
    print("=" * 50)

    try:
        test_instance.test_file_existence()
        test_instance.test_data_shapes()
        test_instance.test_latitude_longitude_comparison()
        test_instance.test_distance_comparison()
        test_instance.test_heart_rate_comparison()
        test_instance.test_temperature_comparison()
        test_instance.test_data_type_consistency()
        test_instance.test_timestamp_progression()
        test_instance.test_field_coverage()
        test_instance.test_value_ranges()

        print("=" * 50)
        print("✅ All FIT vs CSV comparison tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
