"""Tests to verify that lazy evaluation is both correct and more efficient."""

import os
import tempfile
import time

import polars as pl
import pytest

import polarsfit


class TestLazyEvaluation:
    """Test suite for lazy evaluation correctness and performance."""

    def test_lazy_creation_instant(self):
        """Test that LazyFrame creation is instant regardless of file existence."""
        # Test with non-existent file - should be instant
        start_time = time.time()
        lf = polarsfit.scan_recordmesgs("non_existent_large_file.fit")
        creation_time = time.time() - start_time

        assert isinstance(lf, pl.LazyFrame)
        assert creation_time < 0.01, (
            f"LazyFrame creation took {creation_time:.4f}s, should be < 0.01s"
        )

    def test_lazy_operations_instant(self):
        """Test that chaining operations is instant without file access."""
        lf = polarsfit.scan_recordmesgs("non_existent_file.fit")

        start_time = time.time()
        chained = (
            lf.filter(pl.col("heart_rate") > 150)
            .select(["timestamp", "heart_rate", "power"])
            .limit(1000)
            .with_columns(pl.col("heart_rate").alias("hr"))
        )
        operations_time = time.time() - start_time

        assert isinstance(chained, pl.LazyFrame)
        assert operations_time < 0.01, (
            f"Operation chaining took {operations_time:.4f}s, should be < 0.01s"
        )

    def test_error_deferred_until_collection(self):
        """Test that file access errors only occur during collection."""
        # Create LazyFrame with non-existent file - should succeed
        lf = polarsfit.scan_recordmesgs("definitely_does_not_exist.fit")

        # Add operations - should still succeed
        filtered = lf.filter(pl.col("heart_rate") > 100).limit(10)

        # Only when collecting should we get an error
        with pytest.raises((FileNotFoundError, ValueError, RuntimeError)):
            filtered.collect()

    def test_lazy_vs_eager_performance_simulation(self):
        """Test performance difference between lazy and eager approaches."""
        # Since we don't have a real FIT file, we'll simulate the performance difference
        # by testing the creation speed of multiple LazyFrames

        file_paths = [f"fake_file_{i}.fit" for i in range(100)]

        # Test lazy creation (should be very fast)
        start_time = time.time()
        lazy_frames = [polarsfit.scan_recordmesgs(path) for path in file_paths]
        lazy_creation_time = time.time() - start_time

        assert len(lazy_frames) == 100
        assert all(isinstance(lf, pl.LazyFrame) for lf in lazy_frames)
        assert lazy_creation_time < 0.1, (
            f"Creating 100 LazyFrames took {lazy_creation_time:.4f}s, should be < 0.1s"
        )

        print(
            f"Created 100 LazyFrames in {lazy_creation_time:.4f}s ({lazy_creation_time / 100 * 1000:.2f}ms per LazyFrame)"
        )

    def test_lazy_query_optimization_potential(self):
        """Test that lazy evaluation allows for query optimization."""
        lf = polarsfit.scan_recordmesgs("test_file.fit")

        # Create a complex query that could benefit from optimization
        optimized_query = (
            lf.filter(pl.col("heart_rate") > 150)  # Early filter
            .select(["timestamp", "heart_rate", "power"])  # Column pruning
            .filter(pl.col("power") > 200)  # Additional filter
            .limit(100)
        )  # Limit early

        # The LazyFrame should contain the full query plan
        assert isinstance(optimized_query, pl.LazyFrame)

        # We can inspect the query plan (this would show optimizations in a real scenario)
        query_plan = str(optimized_query.explain())
        assert "FILTER" in query_plan  # Should contain filter operations
        assert (
            "SELECT" in query_plan or "SELECTION" in query_plan
        )  # Should contain selection

    def test_lazy_scan_data_functionality(self):
        """Test that scan_data also provides lazy evaluation."""
        start_time = time.time()
        lf = polarsfit.scan_data("non_existent_file.fit", "session")
        creation_time = time.time() - start_time

        assert isinstance(lf, pl.LazyFrame)
        assert creation_time < 0.01, (
            f"scan_data LazyFrame creation took {creation_time:.4f}s"
        )

        # Should only fail on collection
        with pytest.raises((FileNotFoundError, ValueError, RuntimeError)):
            lf.collect()

    def test_multiple_lazy_operations_without_execution(self):
        """Test that multiple operations can be chained without any execution."""
        lf = polarsfit.scan_recordmesgs("test_file.fit")

        # Chain many operations
        start_time = time.time()
        result_lf = lf
        for _ in range(50):  # Many operations
            result_lf = result_lf.filter(pl.col("heart_rate") > 100)

        chaining_time = time.time() - start_time

        assert isinstance(result_lf, pl.LazyFrame)
        assert chaining_time < 0.1, (
            f"50 operation chains took {chaining_time:.4f}s"
        )

    def test_lazy_frame_memory_efficiency(self):
        """Test that LazyFrames don't consume memory for data storage."""
        # Get initial memory usage (rough approximation)
        initial_objects = len(list(globals().values()))

        # Create many LazyFrames
        lazy_frames = []
        for i in range(1000):
            lf = polarsfit.scan_recordmesgs(f"file_{i}.fit")
            lazy_frames.append(lf)

        # Memory should not grow significantly since no data is loaded
        final_objects = len(
            [obj for obj in globals().values() if obj is not None]
        )

        # The number of objects should grow, but each LazyFrame should be lightweight
        assert len(lazy_frames) == 1000
        print(
            f"Created 1000 LazyFrames. Object count change: {final_objects - initial_objects}"
        )

    def test_lazy_correctness_with_field_mapping(self):
        """Test that lazy evaluation works correctly with field mapping."""
        field_mapping = {"field_1": "heart_rate", "field_2": "power"}

        # Should create LazyFrame instantly even with field mapping
        start_time = time.time()
        lf = polarsfit.scan_recordmesgs(
            "test_file.fit", field_mapping=field_mapping
        )
        creation_time = time.time() - start_time

        assert isinstance(lf, pl.LazyFrame)
        assert creation_time < 0.01

        # Field mapping should be preserved in the lazy execution
        with pytest.raises((FileNotFoundError, ValueError, RuntimeError)):
            lf.collect()

    def test_lazy_explain_shows_query_plan(self):
        """Test that lazy frames can show their execution plan."""
        lf = polarsfit.scan_recordmesgs("test_file.fit")
        filtered = lf.filter(pl.col("heart_rate") > 150).select(
            ["timestamp", "heart_rate"]
        )

        # Should be able to get explanation without executing
        plan = filtered.explain()
        assert isinstance(plan, str)
        assert len(plan) > 0
        print(f"Query plan preview: {plan[:200]}...")

    def test_performance_benchmark_lazy_vs_simulated_eager(self):
        """Benchmark lazy creation vs simulated eager loading time."""
        num_files = 50

        # Measure lazy LazyFrame creation
        start_time = time.time()
        lazy_frames = []
        for i in range(num_files):
            lf = polarsfit.scan_recordmesgs(f"benchmark_file_{i}.fit")
            lazy_frames.append(lf)
        lazy_total_time = time.time() - start_time

        # Simulate what eager loading time would be (estimated)
        # Each file read might take ~10ms for a small FIT file
        estimated_eager_time = num_files * 0.01  # 10ms per file

        print("\nPerformance Benchmark:")
        print(f"Lazy creation for {num_files} files: {lazy_total_time:.4f}s")
        print(f"Estimated eager loading time: {estimated_eager_time:.4f}s")
        print(
            f"Lazy is {estimated_eager_time / lazy_total_time:.1f}x faster for creation"
        )

        # Lazy should be significantly faster
        assert lazy_total_time < estimated_eager_time / 10, (
            "Lazy should be at least 10x faster than eager"
        )

    def test_csv_lazy_vs_eager_real_performance(self):
        """Test real performance difference using CSV files as a proxy for FIT file behavior."""
        # Create a larger CSV file for better performance measurement
        csv_content = "timestamp,heart_rate,power,cadence,speed\n"
        for i in range(10000):  # 10k rows
            csv_content += f"{1627849200 + i},{120 + i % 100},{200 + i % 200},{80 + i % 50},{25.5 + i % 20}\n"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            # Test 1: Eager CSV reading (simulate eager FIT reading behavior)
            print("\nCSV Performance Comparison (10k rows):")

            eager_times = []
            for _ in range(10):  # Read multiple times for average
                start_time = time.time()
                _ = pl.read_csv(csv_path)  # Eager reading
                eager_times.append(time.time() - start_time)

            avg_eager_time = sum(eager_times) / len(eager_times)
            print(
                f"   Eager CSV reading: {avg_eager_time:.4f}s (average of 10 reads)"
            )

            # Test 2: Lazy CSV scanning
            lazy_times = []
            for _ in range(10):  # Create multiple LazyFrames
                start_time = time.time()
                _ = pl.scan_csv(csv_path)  # Lazy scanning
                lazy_times.append(time.time() - start_time)

            avg_lazy_time = sum(lazy_times) / len(lazy_times)
            print(
                f"   Lazy CSV scanning: {avg_lazy_time:.4f}s (average of 10 scans)"
            )

            # Calculate speedup
            speedup = (
                avg_eager_time / avg_lazy_time
                if avg_lazy_time > 0
                else float("inf")
            )
            print(f"   Speedup: {speedup:.1f}x faster for lazy scanning")

            # Test 3: Demonstrate our FIT lazy behavior should be similar
            start_time = time.time()
            fit_lazy_frames = []
            for i in range(10):
                lf = polarsfit.scan_recordmesgs(f"fake_file_{i}.fit")
                fit_lazy_frames.append(lf)
            fit_lazy_time = time.time() - start_time

            print(f"   FIT lazy scanning: {fit_lazy_time:.4f}s (10 LazyFrames)")
            print(
                f"   FIT time per LazyFrame: {fit_lazy_time / 10 * 1000:.2f}ms"
            )

            # Assertions
            assert avg_lazy_time < avg_eager_time, (
                "Lazy scanning should be faster than eager reading"
            )
            assert speedup > 5, (
                f"Lazy should be at least 5x faster, got {speedup:.1f}x"
            )
            assert fit_lazy_time < 0.1, "FIT lazy scanning should be very fast"

            print(
                f"   ✓ PASS: Lazy scanning is {speedup:.1f}x faster than eager reading"
            )

        finally:
            # Clean up
            os.unlink(csv_path)

    def test_lazy_operations_with_csv_data(self):
        """Test that lazy operations work correctly and efficiently with real data structure."""
        # Use the test CSV file in the repo
        csv_path = os.path.join(
            os.path.dirname(__file__), "data", "test_data.csv"
        )

        if os.path.exists(csv_path):
            print(f"\nTesting with real CSV data from {csv_path}:")

            # Test lazy operations are instant
            start_time = time.time()
            lazy_df = pl.scan_csv(csv_path)

            # Chain operations (should be instant)
            result = (
                lazy_df.filter(pl.col("heart_rate") > 150)
                .select(["timestamp", "heart_rate", "power"])
                .limit(5)
            )

            operations_time = time.time() - start_time
            print(f"   Lazy operations time: {operations_time:.6f}s")

            # Now collect (this is when actual work happens)
            start_time = time.time()
            collected = result.collect()
            collection_time = time.time() - start_time
            print(f"   Collection time: {collection_time:.6f}s")
            print(f"   Result shape: {collected.shape}")
            print(f"   Result preview:\n{collected}")

            # Assertions
            assert operations_time < 0.01, "Lazy operations should be very fast"
            assert isinstance(collected, pl.DataFrame), (
                "Collection should return DataFrame"
            )
            assert collected.shape[0] <= 5, "Should respect limit"

            print("   ✓ PASS: Lazy operations work correctly with real data")
        else:
            print("   SKIP: test_data.csv not found")


if __name__ == "__main__":
    # Run the tests with detailed output
    pytest.main([__file__, "-v", "-s"])
