#!/usr/bin/env python3
"""
Strict multi-file FIT vs CSV comparison tests.

Tests all available FIT/CSV pairs with exact matching and proper alignment.
"""

from pathlib import Path
from typing import List, Tuple

import polars as pl
import pytest

import polarsfit


class TestStrictMultiFileComparison:
    """Test all FIT files against their CSV counterparts with strict validation."""

    @classmethod
    def setup_class(cls):
        """Discover and set up all available FIT/CSV file pairs."""
        cls.data_dir = Path("tests/data")
        cls.file_pairs = cls._discover_file_pairs()

        if not cls.file_pairs:
            pytest.skip("No FIT/CSV file pairs found for testing")

        print(f"\n🔍 Found {len(cls.file_pairs)} FIT/CSV file pairs:")
        for fit_file, csv_file in cls.file_pairs:
            print(f"   • {fit_file.name} ↔ {csv_file.name}")

    @classmethod
    def _discover_file_pairs(cls) -> List[Tuple[Path, Path]]:
        """Discover all FIT/CSV file pairs in the data directory."""
        pairs = []
        data_dir = Path("tests/data")

        # Find all FIT files
        fit_files = list(data_dir.glob("*.fit"))

        for fit_file in fit_files:
            # Extract activity ID from FIT filename
            fit_stem = fit_file.stem
            if "-" in fit_stem:
                activity_id = fit_stem.split("-")[-1]

                # Find matching CSV file
                csv_pattern = f"*{activity_id}.csv"
                csv_files = list(data_dir.glob(csv_pattern))

                if csv_files:
                    pairs.append((fit_file, csv_files[0]))

        return pairs

    def test_discover_all_file_pairs(self):
        """Test that we can discover file pairs correctly."""
        assert len(self.file_pairs) >= 4, (
            f"Expected at least 4 file pairs, found {len(self.file_pairs)}"
        )

        for fit_file, csv_file in self.file_pairs:
            assert fit_file.exists(), f"FIT file missing: {fit_file}"
            assert csv_file.exists(), f"CSV file missing: {csv_file}"

    def test_strict_gps_coordinates_all_files(self):
        """Test GPS coordinates with strict matching for all files."""
        for fit_file, csv_file in self.file_pairs:
            print(f"\n🧪 Testing GPS coordinates: {fit_file.name}")

            # Load data
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select(
                [col for col in df_csv.columns if col.strip()]
            )

            # Get GPS data
            fit_lat = df_fit.select("field_0").to_series().to_list()
            fit_lon = df_fit.select("field_1").to_series().to_list()
            csv_lat = df_csv.select("Latitude").to_series().to_list()
            csv_lon = df_csv.select("Longitude").to_series().to_list()

            # Find best alignment
            best_offset = self._find_gps_alignment(
                fit_lat, fit_lon, csv_lat, csv_lon
            )
            print(f"   Best alignment offset: {best_offset}")

            # Test with very strict tolerance
            exact_matches = 0
            test_count = min(
                100,
                len(fit_lat) - abs(best_offset),
                len(csv_lat) - abs(best_offset),
            )

            for i in range(test_count):
                fit_idx = i + max(0, best_offset)
                csv_idx = i + max(0, -best_offset)

                if fit_idx >= len(fit_lat) or csv_idx >= len(csv_lat):
                    break

                lat_diff = abs(fit_lat[fit_idx] - csv_lat[csv_idx])
                lon_diff = abs(fit_lon[fit_idx] - csv_lon[csv_idx])

                # Extremely strict tolerance (GPS should be nearly identical)
                if lat_diff < 0.000001 and lon_diff < 0.000001:
                    exact_matches += 1

            match_ratio = exact_matches / test_count if test_count > 0 else 0
            print(
                f"   Exact GPS matches: {exact_matches}/{test_count} ({match_ratio:.1%})"
            )

            assert match_ratio > 0.95, (
                f"{fit_file.name}: GPS should match >95%, got {match_ratio:.1%}"
            )

    def test_strict_distance_all_files(self):
        """Test distance values with exact conversion for all files."""
        for fit_file, csv_file in self.file_pairs:
            print(f"\n📏 Testing distance: {fit_file.name}")

            # Load data
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select(
                [col for col in df_csv.columns if col.strip()]
            )

            # Get distance data (FIT in centimeters, CSV in km)
            fit_distance_cm = df_fit.select("field_5").to_series().to_list()
            csv_distance_km = df_csv.select("Distance").to_series().to_list()

            # Convert FIT to km with exact precision
            fit_distance_km = [d / 100000.0 for d in fit_distance_cm]

            # Find alignment based on distance progression
            best_offset = self._find_distance_alignment(
                fit_distance_km, csv_distance_km
            )
            print(f"   Distance alignment offset: {best_offset}")

            # Test exact matches with proper alignment
            exact_matches = 0
            close_matches = 0
            test_count = min(
                100,
                len(fit_distance_km) - abs(best_offset),
                len(csv_distance_km) - abs(best_offset),
            )

            for i in range(test_count):
                fit_idx = i + max(0, best_offset)
                csv_idx = i + max(0, -best_offset)

                if fit_idx >= len(fit_distance_km) or csv_idx >= len(
                    csv_distance_km
                ):
                    break

                fit_val = fit_distance_km[fit_idx]
                csv_val = csv_distance_km[csv_idx]

                # Check for exact match (within floating point precision)
                if abs(fit_val - csv_val) < 0.0000001:
                    exact_matches += 1
                # Check for very close match (within 0.00001%)
                elif (
                    csv_val > 0 and abs(fit_val - csv_val) / csv_val < 0.0000001
                ):
                    close_matches += 1

            exact_ratio = exact_matches / test_count if test_count > 0 else 0
            close_ratio = (
                (exact_matches + close_matches) / test_count
                if test_count > 0
                else 0
            )

            print(
                f"   Exact distance matches: {exact_matches}/{test_count} ({exact_ratio:.1%})"
            )
            print(
                f"   Close distance matches: {exact_matches + close_matches}/{test_count} ({close_ratio:.1%})"
            )

            assert close_ratio > 0.98, (
                f"{fit_file.name}: Distance should match >98%, got {close_ratio:.1%}"
            )

    def test_heart_rate_all_files(self):
        """Test heart rate matching for all files."""
        for fit_file, csv_file in self.file_pairs:
            print(f"\n💓 Testing heart rate: {fit_file.name}")

            # Load data
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select(
                [col for col in df_csv.columns if col.strip()]
            )

            if "field_3" not in df_fit.columns:
                print(f"   ⏭️  No heart rate data in {fit_file.name}")
                continue

            # Get heart rate data
            fit_hr = df_fit.select("field_3").to_series().to_list()
            csv_hr = df_csv.select("HeartRate").to_series().to_list()

            # Filter valid heart rate values
            fit_valid = [hr for hr in fit_hr if 50 <= hr <= 220]
            csv_valid = [hr for hr in csv_hr if 50 <= hr <= 220]

            if len(fit_valid) < 10 or len(csv_valid) < 10:
                print(f"   ⏭️  Insufficient heart rate data in {fit_file.name}")
                continue

            # Find alignment for heart rate
            best_offset = self._find_heart_rate_alignment(fit_hr, csv_hr)
            print(f"   Heart rate alignment offset: {best_offset}")

            # Test exact heart rate matches
            exact_matches = 0
            test_count = min(
                50,
                len(fit_hr) - abs(best_offset),
                len(csv_hr) - abs(best_offset),
            )

            for i in range(test_count):
                fit_idx = i + max(0, best_offset)
                csv_idx = i + max(0, -best_offset)

                if fit_idx >= len(fit_hr) or csv_idx >= len(csv_hr):
                    break

                fit_val = fit_hr[fit_idx]
                csv_val = csv_hr[csv_idx]

                # Skip invalid values
                if not (50 <= fit_val <= 220) or not (50 <= csv_val <= 220):
                    continue

                # Heart rate should match exactly (integer values)
                if fit_val == csv_val:
                    exact_matches += 1

            valid_tests = sum(
                1
                for i in range(test_count)
                if (
                    i + max(0, best_offset) < len(fit_hr)
                    and i + max(0, -best_offset) < len(csv_hr)
                    and 50 <= fit_hr[i + max(0, best_offset)] <= 220
                    and 50 <= csv_hr[i + max(0, -best_offset)] <= 220
                )
            )

            if valid_tests > 0:
                match_ratio = exact_matches / valid_tests
                print(
                    f"   Heart rate exact matches: {exact_matches}/{valid_tests} ({match_ratio:.1%})"
                )
                assert match_ratio > 0.8, (
                    f"{fit_file.name}: Heart rate should match >80%, got {match_ratio:.1%}"
                )

    def _find_gps_alignment(
        self,
        fit_lat: List[float],
        fit_lon: List[float],
        csv_lat: List[float],
        csv_lon: List[float],
    ) -> int:
        """Find the best alignment offset for GPS coordinates."""
        best_offset = 0
        best_score = 0

        for offset in range(-5, 6):
            score = 0
            test_count = min(
                50, len(fit_lat) - abs(offset), len(csv_lat) - abs(offset)
            )

            for i in range(test_count):
                fit_idx = i + max(0, offset)
                csv_idx = i + max(0, -offset)

                if fit_idx >= len(fit_lat) or csv_idx >= len(csv_lat):
                    break

                lat_diff = abs(fit_lat[fit_idx] - csv_lat[csv_idx])
                lon_diff = abs(fit_lon[fit_idx] - csv_lon[csv_idx])

                if lat_diff < 0.00001 and lon_diff < 0.00001:
                    score += 1

            if score > best_score:
                best_score = score
                best_offset = offset

        return best_offset

    def _find_distance_alignment(
        self, fit_dist: List[float], csv_dist: List[float]
    ) -> int:
        """Find the best alignment offset for distance values."""
        best_offset = 0
        best_score = 0

        for offset in range(-5, 6):
            score = 0
            test_count = min(
                50, len(fit_dist) - abs(offset), len(csv_dist) - abs(offset)
            )

            for i in range(test_count):
                fit_idx = i + max(0, offset)
                csv_idx = i + max(0, -offset)

                if fit_idx >= len(fit_dist) or csv_idx >= len(csv_dist):
                    break

                if csv_dist[csv_idx] > 0:
                    diff_percent = (
                        abs(fit_dist[fit_idx] - csv_dist[csv_idx])
                        / csv_dist[csv_idx]
                    )
                    if diff_percent < 0.000001:
                        score += 1

            if score > best_score:
                best_score = score
                best_offset = offset

        return best_offset

    def _find_heart_rate_alignment(
        self, fit_hr: List[int], csv_hr: List[int]
    ) -> int:
        """Find the best alignment offset for heart rate values."""
        best_offset = 0
        best_score = 0

        for offset in range(-3, 4):
            score = 0
            test_count = min(
                30, len(fit_hr) - abs(offset), len(csv_hr) - abs(offset)
            )

            for i in range(test_count):
                fit_idx = i + max(0, offset)
                csv_idx = i + max(0, -offset)

                if fit_idx >= len(fit_hr) or csv_idx >= len(csv_hr):
                    break

                if (
                    50 <= fit_hr[fit_idx] <= 220
                    and 50 <= csv_hr[csv_idx] <= 220
                    and fit_hr[fit_idx] == csv_hr[csv_idx]
                ):
                    score += 1

            if score > best_score:
                best_score = score
                best_offset = offset

        return best_offset


if __name__ == "__main__":
    # Direct execution for testing
    test_instance = TestStrictMultiFileComparison()
    test_instance.setup_class()

    print("🧪 Running strict multi-file FIT vs CSV comparison tests...")
    print("=" * 70)

    try:
        test_instance.test_discover_all_file_pairs()
        test_instance.test_strict_gps_coordinates_all_files()
        test_instance.test_strict_distance_all_files()
        test_instance.test_heart_rate_all_files()

        print("\n✅ All strict multi-file tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
