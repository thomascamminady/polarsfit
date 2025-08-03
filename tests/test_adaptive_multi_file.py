#!/usr/bin/env python3
"""
Adaptive multi-file FIT vs CSV comparison tests.

Tests all available FIT/CSV pairs with appropriate validation based on available data.
"""

from pathlib import Path
from typing import List, Tuple, Optional

import polars as pl
import pytest

import polarsfit


class TestAdaptiveMultiFileComparison:
    """Test all FIT files against their CSV counterparts with adaptive validation."""

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
        
        fit_files = list(data_dir.glob("*.fit"))
        
        for fit_file in fit_files:
            fit_stem = fit_file.stem
            if "-" in fit_stem:
                activity_id = fit_stem.split("-")[-1]
                csv_pattern = f"*{activity_id}.csv"
                csv_files = list(data_dir.glob(csv_pattern))
                
                if csv_files:
                    pairs.append((fit_file, csv_files[0]))
        
        return pairs

    def test_all_file_pairs_basic_integrity(self):
        """Test basic data integrity for all file pairs."""
        for fit_file, csv_file in self.file_pairs:
            print(f"\n🔍 Testing basic integrity: {fit_file.name}")
            
            # Load data
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select([col for col in df_csv.columns if col.strip()])
            
            # Basic integrity checks
            assert df_fit.shape[0] > 0, f"FIT file {fit_file.name} has no records"
            assert df_csv.shape[0] > 0, f"CSV file {csv_file.name} has no records"
            
            # Core FIT fields should exist
            assert 'field_253' in df_fit.columns, f"Missing timestamp in {fit_file.name}"
            
            print(f"   ✅ FIT: {df_fit.shape[0]} records, {df_fit.shape[1]} fields")
            print(f"   ✅ CSV: {df_csv.shape[0]} records, {df_csv.shape[1]} fields")

    def test_gps_coordinates_when_available(self):
        """Test GPS coordinates for files that have GPS data."""
        for fit_file, csv_file in self.file_pairs:
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select([col for col in df_csv.columns if col.strip()])
            
            # Skip if no GPS data in CSV
            if 'Latitude' not in df_csv.columns or 'Longitude' not in df_csv.columns:
                print(f"\n⏭️  No GPS data in CSV: {fit_file.name}")
                continue
            
            print(f"\n🗺️  Testing GPS coordinates: {fit_file.name}")
            
            # Get GPS data
            fit_lat = df_fit.select('field_0').to_series().to_list()
            fit_lon = df_fit.select('field_1').to_series().to_list()
            csv_lat = df_csv.select('Latitude').to_series().to_list()
            csv_lon = df_csv.select('Longitude').to_series().to_list()
            
            # Test close matches (allowing for precision differences)
            close_matches = 0
            test_count = min(50, len(fit_lat), len(csv_lat))
            
            for i in range(test_count):
                lat_diff = abs(fit_lat[i] - csv_lat[i])
                lon_diff = abs(fit_lon[i] - csv_lon[i])
                
                # Allow for reasonable GPS precision differences (about 1 meter)
                if lat_diff < 0.00001 and lon_diff < 0.00001:
                    close_matches += 1
            
            match_ratio = close_matches / test_count if test_count > 0 else 0
            print(f"   GPS close matches: {close_matches}/{test_count} ({match_ratio:.1%})")
            
            # GPS should be reasonably close (allowing for export precision differences)
            assert match_ratio > 0.8, f"{fit_file.name}: GPS should match >80%, got {match_ratio:.1%}"

    def test_distance_when_available(self):
        """Test distance values for files that have distance data."""
        for fit_file, csv_file in self.file_pairs:
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select([col for col in df_csv.columns if col.strip()])
            
            # Skip if no distance data in CSV
            if 'Distance' not in df_csv.columns:
                print(f"\n⏭️  No distance data in CSV: {fit_file.name}")
                continue
            
            print(f"\n📏 Testing distance: {fit_file.name}")
            
            # Get distance data (FIT in centimeters, CSV in km)
            fit_distance_cm = df_fit.select('field_5').to_series().to_list()
            csv_distance_km = df_csv.select('Distance').to_series().to_list()
            
            # Convert FIT to km
            fit_distance_km = [d / 100000.0 for d in fit_distance_cm]
            
            # Test distance matches
            close_matches = 0
            test_count = min(50, len(fit_distance_km), len(csv_distance_km))
            
            for i in range(test_count):
                fit_val = fit_distance_km[i]
                csv_val = csv_distance_km[i]
                
                # Allow for very small rounding differences
                if csv_val > 0:
                    diff_percent = abs(fit_val - csv_val) / csv_val * 100
                    if diff_percent < 0.001:  # 0.001% tolerance
                        close_matches += 1
                elif abs(fit_val - csv_val) < 0.000001:  # Absolute tolerance for zero values
                    close_matches += 1
            
            match_ratio = close_matches / test_count if test_count > 0 else 0
            print(f"   Distance close matches: {close_matches}/{test_count} ({match_ratio:.1%})")
            
            assert match_ratio > 0.95, f"{fit_file.name}: Distance should match >95%, got {match_ratio:.1%}"

    def test_heart_rate_when_available(self):
        """Test heart rate values for files that have heart rate data."""
        for fit_file, csv_file in self.file_pairs:
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select([col for col in df_csv.columns if col.strip()])
            
            # Skip if no heart rate data
            if 'field_3' not in df_fit.columns or 'HeartRate' not in df_csv.columns:
                print(f"\n⏭️  No heart rate data: {fit_file.name}")
                continue
            
            print(f"\n💓 Testing heart rate: {fit_file.name}")
            
            # Get heart rate data
            fit_hr = df_fit.select('field_3').to_series().to_list()
            csv_hr = df_csv.select('HeartRate').to_series().to_list()
            
            # Filter out None/null values and invalid heart rates
            valid_comparisons = 0
            exact_matches = 0
            close_matches = 0
            
            test_count = min(50, len(fit_hr), len(csv_hr))
            
            for i in range(test_count):
                fit_val = fit_hr[i]
                csv_val = csv_hr[i]
                
                # Skip None values or invalid heart rates
                if (fit_val is None or csv_val is None or 
                    not isinstance(fit_val, (int, float)) or 
                    not isinstance(csv_val, (int, float)) or
                    fit_val <= 30 or fit_val >= 250 or 
                    csv_val <= 30 or csv_val >= 250):
                    continue
                
                valid_comparisons += 1
                
                # Check for exact match
                if fit_val == csv_val:
                    exact_matches += 1
                # Check for close match (±1 BPM)
                elif abs(fit_val - csv_val) <= 1:
                    close_matches += 1
            
            if valid_comparisons > 10:
                exact_ratio = exact_matches / valid_comparisons
                close_ratio = (exact_matches + close_matches) / valid_comparisons
                
                print(f"   Heart rate exact matches: {exact_matches}/{valid_comparisons} ({exact_ratio:.1%})")
                print(f"   Heart rate close matches: {exact_matches + close_matches}/{valid_comparisons} ({close_ratio:.1%})")
                
                # Allow for timing differences and sensor variations
                assert close_ratio > 0.7, f"{fit_file.name}: Heart rate should match >70%, got {close_ratio:.1%}"
            else:
                print(f"   ⏭️  Insufficient valid heart rate data: {valid_comparisons} comparisons")

    def test_comprehensive_field_analysis(self):
        """Analyze all fields present in FIT files and their potential CSV mappings."""
        print(f"\n📊 Comprehensive field analysis across all files:")
        
        all_fit_fields = set()
        all_csv_fields = set()
        
        for fit_file, csv_file in self.file_pairs:
            df_fit = polarsfit.read_recordmesgs(str(fit_file))
            df_csv = pl.read_csv(str(csv_file))
            df_csv = df_csv.select([col for col in df_csv.columns if col.strip()])
            
            all_fit_fields.update(df_fit.columns)
            all_csv_fields.update(df_csv.columns)
        
        print(f"\n   All FIT fields found: {sorted(all_fit_fields)}")
        print(f"\n   All CSV fields found: {sorted(all_csv_fields)}")
        
        # Known field mappings
        known_mappings = {
            'field_253': 'timestamp/Duration',
            'field_0': 'Latitude',
            'field_1': 'Longitude', 
            'field_5': 'Distance',
            'field_3': 'HeartRate',
            'field_4': 'Cadence',
            'field_7': 'PowerOriginal',
            'field_13': 'Temperature',
            'field_78': 'AltitudeOriginal',
        }
        
        print(f"\n   Known field mappings:")
        for fit_field, csv_field in known_mappings.items():
            if fit_field in all_fit_fields:
                print(f"     ✅ {fit_field} → {csv_field}")
            else:
                print(f"     ❌ {fit_field} → {csv_field} (not found)")


if __name__ == "__main__":
    # Direct execution for testing
    test_instance = TestAdaptiveMultiFileComparison()
    test_instance.setup_class()
    
    print("🧪 Running adaptive multi-file FIT vs CSV comparison tests...")
    print("=" * 70)
    
    try:
        test_instance.test_all_file_pairs_basic_integrity()
        test_instance.test_gps_coordinates_when_available()
        test_instance.test_distance_when_available() 
        test_instance.test_heart_rate_when_available()
        test_instance.test_comprehensive_field_analysis()
        
        print("\n✅ All adaptive multi-file tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
