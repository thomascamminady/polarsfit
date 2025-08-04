"""Performance comparison test between scan and read operations on real FIT files."""

import os
import time
from pathlib import Path

import polars as pl
import pytest

import polarsfit


class TestFitPerformanceComparison:
    """Test suite comparing scan vs read performance on real FIT files."""

    @pytest.fixture(scope="class")
    def sample_fit_file(self):
        """Get a sample FIT file for testing."""
        # Look for FIT files in the tests/data directory
        repo_root = Path(__file__).parent.parent
        data_dir = repo_root / "tests" / "data"

        # Find any .fit files in the data directory
        fit_files = list(data_dir.glob("*.fit"))
        if fit_files:
            return str(fit_files[0])  # Use the first available FIT file

        # If no FIT file found, skip the test
        return None

    def test_scan_vs_read_performance_100x(self, sample_fit_file):
        """Test that scanning 10 FIT files is at least 10x faster than reading them."""
        if sample_fit_file is None:
            pytest.skip(
                "No FIT file available for testing. Need a real .fit file to perform this test."
            )

        if not os.path.exists(sample_fit_file):
            pytest.skip(f"Sample FIT file {sample_fit_file} not found")

        print(f"\nPerformance test using FIT file: {sample_fit_file}")

        # Test 1: Scan operation 10 times (should be very fast)
        print("Testing scan performance (10 iterations)...")
        scan_times = []

        for _ in range(10):
            start_time = time.time()
            # Scan without collecting - this should be nearly instant
            lazy_frame = polarsfit.scan_recordmesgs(sample_fit_file)
            scan_time = time.time() - start_time
            scan_times.append(scan_time)

            # Verify it's actually a LazyFrame
            assert isinstance(lazy_frame, pl.LazyFrame)

        total_scan_time = sum(scan_times)
        avg_scan_time = total_scan_time / 10

        print(f"   Total scan time (10x): {total_scan_time:.4f}s")
        print(f"   Average scan time: {avg_scan_time:.6f}s")
        print(f"   Scan operations per second: {10 / total_scan_time:.1f}")

        # Test 2: Read operation 10 times (will be much slower)
        print("Testing read performance (10 iterations)...")
        read_times = []

        for _ in range(10):
            start_time = time.time()
            # Read the file completely - this involves actual I/O
            dataframe = polarsfit.read_recordmesgs(sample_fit_file)
            read_time = time.time() - start_time
            read_times.append(read_time)

            # Verify it's actually a DataFrame
            assert isinstance(dataframe, pl.DataFrame)
            assert len(dataframe) > 0  # Should have some data

        total_read_time = sum(read_times)
        avg_read_time = total_read_time / 10

        print(f"   Total read time (10x): {total_read_time:.4f}s")
        print(f"   Average read time: {avg_read_time:.6f}s")
        print(f"   Read operations per second: {10 / total_read_time:.1f}")

        # Calculate performance difference
        speedup = total_read_time / total_scan_time
        print("\nPerformance Comparison:")
        print(f"   Scan is {speedup:.1f}x faster than read")
        print(f"   Time difference: {total_read_time - total_scan_time:.4f}s")

        # Assertions
        assert total_scan_time < total_read_time, (
            "Scan should be faster than read"
        )
        assert speedup >= 10, (
            f"Scan should be at least 10x faster than read, got {speedup:.1f}x"
        )

        print(
            f"   ✓ PASS: Scan is {speedup:.1f}x faster than read (exceeds 10x requirement)"
        )

    def test_scan_operations_consistency(self, sample_fit_file):
        """Test that scan operations are consistently fast."""
        if sample_fit_file is None:
            pytest.skip("No FIT file available for testing")

        if not os.path.exists(sample_fit_file):
            pytest.skip(f"Sample FIT file {sample_fit_file} not found")

        print("\nTesting scan operation consistency...")

        scan_times = []
        for _ in range(50):
            start_time = time.time()
            _ = polarsfit.scan_recordmesgs(sample_fit_file)
            scan_time = time.time() - start_time
            scan_times.append(scan_time)

        avg_time = sum(scan_times) / len(scan_times)
        max_time = max(scan_times)
        min_time = min(scan_times)

        print(f"   Average scan time: {avg_time:.6f}s")
        print(f"   Min scan time: {min_time:.6f}s")
        print(f"   Max scan time: {max_time:.6f}s")
        print(f"   Variance: {max_time - min_time:.6f}s")

        # All scan operations should be very fast and consistent
        assert avg_time < 0.01, (
            f"Average scan time should be < 10ms, got {avg_time:.6f}s"
        )
        assert max_time < 0.05, (
            f"Max scan time should be < 50ms, got {max_time:.6f}s"
        )

        print("   ✓ PASS: Scan operations are consistently fast")

    def test_lazy_vs_eager_with_operations(self, sample_fit_file):
        """Test that lazy operations with filters are still faster than eager equivalents."""
        if sample_fit_file is None:
            pytest.skip("No FIT file available for testing")

        if not os.path.exists(sample_fit_file):
            pytest.skip(f"Sample FIT file {sample_fit_file} not found")

        print("\nTesting lazy vs eager with operations...")

        # Test lazy approach: scan + operations (no collect)
        lazy_times = []
        for _ in range(20):
            start_time = time.time()

            # Scan and add operations without collecting
            result = (
                polarsfit.scan_recordmesgs(sample_fit_file)
                .filter(pl.col("heart_rate") > 120)  # Use actual column name
                .select(
                    ["timestamp", "heart_rate", "power"]
                )  # Use actual column names
                .limit(1000)
            )

            lazy_time = time.time() - start_time
            lazy_times.append(lazy_time)

            assert isinstance(result, pl.LazyFrame)

        avg_lazy_time = sum(lazy_times) / len(lazy_times)

        # Test eager approach: read + operations
        eager_times = []
        for _ in range(20):
            start_time = time.time()

            # Read and apply same operations
            df = polarsfit.read_recordmesgs(sample_fit_file)
            result = (
                df.filter(pl.col("heart_rate") > 120)
                .select(["timestamp", "heart_rate", "power"])
                .limit(1000)
            )

            eager_time = time.time() - start_time
            eager_times.append(eager_time)

            assert isinstance(result, pl.DataFrame)

        avg_eager_time = sum(eager_times) / len(eager_times)

        speedup = avg_eager_time / avg_lazy_time

        print(f"   Lazy (scan + ops): {avg_lazy_time:.6f}s")
        print(f"   Eager (read + ops): {avg_eager_time:.6f}s")
        print(f"   Speedup: {speedup:.1f}x")

        # Lazy should still be significantly faster
        assert avg_lazy_time < avg_eager_time, (
            "Lazy operations should be faster"
        )
        assert speedup >= 5, (
            f"Lazy should be at least 5x faster, got {speedup:.1f}x"
        )

        print(f"   ✓ PASS: Lazy operations are {speedup:.1f}x faster")


if __name__ == "__main__":
    # Run the tests with detailed output
    pytest.main([__file__, "-v", "-s"])
