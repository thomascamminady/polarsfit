"""
Performance comparison tests for lazy vs eager evaluation.
This creates real scenarios to measure the efficiency gains.
"""

import time

import polars as pl
import pytest

import polarsfit


class TestLazyPerformance:
    """Test performance benefits of lazy evaluation."""

    def test_lazy_creation_vs_eager_simulation(self):
        """Compare lazy LazyFrame creation speed vs simulated eager loading."""
        num_operations = 100

        # Test 1: Lazy LazyFrame creation (should be very fast)
        start_time = time.time()
        lazy_frames = []
        for i in range(num_operations):
            lf = polarsfit.scan_recordmesgs(f"test_file_{i}.fit")
            lazy_frames.append(lf)
        lazy_time = time.time() - start_time

        # Test 2: Simulate eager approach timing
        # (We can't actually test eager loading without real files,
        # but we can test the current eager read_* functions for comparison)
        start_time = time.time()
        eager_attempts = 0
        for i in range(
            min(5, num_operations)
        ):  # Limit to avoid too many errors
            try:
                # This will fail but shows the time cost of attempting file access
                polarsfit.read_recordmesgs(f"test_file_{i}.fit")
            except Exception:
                eager_attempts += 1
                pass
        eager_simulation_time = time.time() - start_time

        # Extrapolate eager time for full operation count
        if eager_attempts > 0:
            estimated_eager_total = (
                eager_simulation_time / eager_attempts
            ) * num_operations
        else:
            estimated_eager_total = 1.0  # Fallback estimate

        print("\nPerformance Comparison:")
        print(f"Lazy {num_operations} LazyFrames: {lazy_time:.4f}s")
        print(
            f"Estimated eager {num_operations} DataFrames: {estimated_eager_total:.4f}s"
        )
        print(f"Speedup: {estimated_eager_total / lazy_time:.1f}x")

        # Assertions
        assert len(lazy_frames) == num_operations
        assert lazy_time < 0.1, (
            f"Lazy creation took {lazy_time:.4f}s, should be < 0.1s"
        )
        assert lazy_time < estimated_eager_total / 5, (
            "Lazy should be at least 5x faster"
        )

    def test_lazy_operation_chaining_performance(self):
        """Test that operation chaining is fast without data access."""
        lf = polarsfit.scan_recordmesgs("performance_test.fit")

        operations = [
            lambda x: x.filter(pl.col("heart_rate") > 120),
            lambda x: x.filter(pl.col("power") > 100),
            lambda x: x.select(["timestamp", "heart_rate", "power"]),
            lambda x: x.with_columns(pl.col("heart_rate").alias("hr")),
            lambda x: x.limit(1000),
            lambda x: x.filter(pl.col("hr") < 180),
            lambda x: x.with_columns(
                (pl.col("power") * 1.1).alias("adjusted_power")
            ),
            lambda x: x.sort("timestamp"),
        ]

        # Time the chaining of many operations
        start_time = time.time()
        result_lf = lf
        for operation in operations * 10:  # Repeat operations multiple times
            result_lf = operation(result_lf)
        chaining_time = time.time() - start_time

        print(
            f"Chained {len(operations) * 10} operations in {chaining_time:.4f}s"
        )

        assert isinstance(result_lf, pl.LazyFrame)
        assert chaining_time < 0.1, (
            f"Operation chaining took {chaining_time:.4f}s, should be < 0.1s"
        )

    def test_memory_efficiency_lazy_vs_eager(self):
        """Test memory usage difference between lazy and eager approaches."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many lazy frames
        lazy_frames = []
        for i in range(500):
            lf = polarsfit.scan_recordmesgs(f"memory_test_{i}.fit")
            lazy_frames.append(lf)

        # Measure memory after lazy creation
        lazy_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = lazy_memory - initial_memory

        print("\nMemory Usage:")
        print(f"Initial memory: {initial_memory:.2f} MB")
        print(f"After 500 LazyFrames: {lazy_memory:.2f} MB")
        print(f"Memory increase: {memory_increase:.2f} MB")
        print(f"Memory per LazyFrame: {memory_increase / 500 * 1024:.2f} KB")

        # Each LazyFrame should use minimal memory
        assert memory_increase < 50, (
            f"Memory increase of {memory_increase:.2f}MB too high"
        )
        assert len(lazy_frames) == 500

    def test_query_optimization_potential(self):
        """Test that lazy evaluation enables query optimization."""
        lf = polarsfit.scan_recordmesgs("optimization_test.fit")

        # Create a query that could benefit from predicate pushdown and column pruning
        optimized_query = (
            lf.select(
                ["timestamp", "heart_rate", "power", "cadence"]
            )  # Column pruning
            .filter(pl.col("heart_rate") > 140)  # Early filter
            .filter(pl.col("power") > 200)  # Multiple filters
            .limit(100)
        )  # Limit pushdown

        # Check that the query plan contains optimizations
        plan = optimized_query.explain()
        print(f"Query plan (first 300 chars):\n{plan[:300]}...")

        # The plan should contain evidence of optimizations
        plan_lower = plan.lower()
        assert "filter" in plan_lower or "selection" in plan_lower
        assert isinstance(optimized_query, pl.LazyFrame)

    def test_error_handling_performance(self):
        """Test that error handling doesn't impact lazy creation performance."""
        # Create LazyFrames with various invalid file paths
        invalid_paths = [
            "/non/existent/path.fit",
            "file_with_spaces in name.fit",
            "file-with-special-chars!@#$.fit",
            "",
            "a" * 1000 + ".fit",  # Very long filename
        ]

        start_time = time.time()
        lazy_frames = []
        for path in invalid_paths * 20:  # Test 100 invalid paths
            lf = polarsfit.scan_recordmesgs(path)
            lazy_frames.append(lf)
        creation_time = time.time() - start_time

        print(
            f"Created {len(lazy_frames)} LazyFrames with invalid paths in {creation_time:.4f}s"
        )

        assert len(lazy_frames) == len(invalid_paths) * 20
        assert creation_time < 0.1, (
            "Even with invalid paths, creation should be fast"
        )

        # All should fail when we try to collect
        for lf in lazy_frames[:3]:  # Test a few
            with pytest.raises((FileNotFoundError, OSError, Exception)):
                lf.collect()

    def test_scalability_many_lazy_frames(self):
        """Test that creating many LazyFrames scales linearly."""
        batch_sizes = [100, 500, 1000]
        times = []

        for batch_size in batch_sizes:
            start_time = time.time()
            lazy_frames = [
                polarsfit.scan_recordmesgs(f"scale_test_{i}.fit")
                for i in range(batch_size)
            ]
            batch_time = time.time() - start_time
            times.append(batch_time)

            print(
                f"Created {batch_size} LazyFrames in {batch_time:.4f}s "
                f"({batch_time / batch_size * 1000:.2f}ms per LazyFrame)"
            )

            assert len(lazy_frames) == batch_size

        # Check that time scales roughly linearly (not quadratically)
        time_per_frame_100 = times[0] / batch_sizes[0]
        time_per_frame_1000 = times[2] / batch_sizes[2]

        # Time per frame shouldn't increase dramatically with scale
        assert time_per_frame_1000 < time_per_frame_100 * 2, (
            "Scaling should be roughly linear"
        )

    def test_concurrent_lazy_operations(self):
        """Test performance of concurrent lazy operations."""
        import queue
        import threading

        def create_lazy_frames(num_frames, result_queue):
            start_time = time.time()
            frames = []
            for i in range(num_frames):
                lf = polarsfit.scan_recordmesgs(f"concurrent_test_{i}.fit")
                frames.append(lf)
            end_time = time.time()
            result_queue.put((len(frames), end_time - start_time))

        # Test concurrent creation
        result_queue = queue.Queue()
        threads = []
        num_threads = 4
        frames_per_thread = 50

        start_time = time.time()
        for i in range(num_threads):
            thread = threading.Thread(
                target=create_lazy_frames,
                args=(frames_per_thread, result_queue),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Collect results
        total_frames = 0
        thread_times = []
        while not result_queue.empty():
            frames, thread_time = result_queue.get()
            total_frames += frames
            thread_times.append(thread_time)

        print("\nConcurrent Test:")
        print(f"Total frames created: {total_frames}")
        print(f"Total time: {total_time:.4f}s")
        print(
            f"Average thread time: {sum(thread_times) / len(thread_times):.4f}s"
        )

        assert total_frames == num_threads * frames_per_thread
        assert total_time < 1.0, "Concurrent creation should be fast"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
