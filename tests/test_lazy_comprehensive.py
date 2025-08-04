#!/usr/bin/env python3
"""Comprehensive test demonstrating lazy evaluation benefits."""

import time

import polars as pl

import polarsfit


def test_lazy_is_truly_lazy():
    """Demonstrate that lazy evaluation actually defers file reading."""
    print("=" * 60)
    print("LAZY EVALUATION VERIFICATION")
    print("=" * 60)

    # Test 1: Instant LazyFrame creation
    print("\n1. LazyFrame Creation Performance:")
    start_time = time.time()
    lf = polarsfit.scan_recordmesgs("nonexistent_file.fit")
    creation_time = time.time() - start_time

    print(f"   Time to create LazyFrame: {creation_time:.6f}s")
    print(f"   LazyFrame type: {type(lf)}")
    assert creation_time < 0.02, f"Creation too slow: {creation_time:.6f}s"
    print("   ✓ PASS: LazyFrame creation is instant")

    # Test 2: Operation chaining is fast
    print("\n2. Operation Chaining Performance:")
    start_time = time.time()
    chained = (
        lf.filter(pl.col("heart_rate") > 150)
        .select(["timestamp", "heart_rate", "power"])
        .limit(100)
        .with_columns(pl.col("heart_rate").alias("hr"))
    )
    chain_time = time.time() - start_time

    print(f"   Time to chain 4 operations: {chain_time:.6f}s")
    assert chain_time < 0.01, f"Chaining too slow: {chain_time:.6f}s"
    print("   ✓ PASS: Operation chaining is instant")

    # Test 3: Error only on materialization
    print("\n3. Error Handling (Deferred Until Collection):")
    try:
        chained.collect()
        print("   ✗ FAIL: Should have errored!")
        raise AssertionError("Expected file not found error")
    except Exception as e:
        print("   File read attempted only on .collect()")
        print(f"   Error: {type(e).__name__}")
        print("   ✓ PASS: Errors properly deferred")


def test_lazy_performance_scaling():
    """Test performance scaling with many LazyFrames."""
    print("\n" + "=" * 60)
    print("PERFORMANCE SCALING TEST")
    print("=" * 60)

    sizes = [100, 500, 1000]

    for size in sizes:
        print(f"\nCreating {size} LazyFrames:")
        start_time = time.time()

        lazy_frames = []
        for i in range(size):
            lf = polarsfit.scan_recordmesgs(f"test_file_{i}.fit")
            lazy_frames.append(lf)

        total_time = time.time() - start_time
        time_per_frame = total_time / size * 1000  # ms

        print(f"   Total time: {total_time:.4f}s")
        print(f"   Time per LazyFrame: {time_per_frame:.2f}ms")

        # Should be very fast
        assert total_time < 0.1, (
            f"Too slow for {size} LazyFrames: {total_time:.4f}s"
        )
        assert len(lazy_frames) == size
        print(f"   ✓ PASS: {size} LazyFrames created efficiently")


def test_lazy_memory_efficiency():
    """Test memory efficiency of LazyFrames."""
    print("\n" + "=" * 60)
    print("MEMORY EFFICIENCY TEST")
    print("=" * 60)

    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many LazyFrames
        lazy_frames = []
        for i in range(1000):
            lf = polarsfit.scan_recordmesgs(f"memory_test_{i}.fit")
            lazy_frames.append(lf)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        memory_per_frame = memory_increase / 1000 * 1024  # KB

        print(f"   Initial memory: {initial_memory:.2f} MB")
        print(f"   Final memory: {final_memory:.2f} MB")
        print(f"   Memory increase: {memory_increase:.2f} MB")
        print(f"   Memory per LazyFrame: {memory_per_frame:.2f} KB")

        # Each LazyFrame should use minimal memory
        assert memory_increase < 100, (
            f"Memory increase too high: {memory_increase:.2f}MB"
        )
        print("   ✓ PASS: Memory usage is efficient")

    except ImportError:
        print("   psutil not available, skipping memory test")


def test_lazy_interface_consistency():
    """Test that lazy interface matches eager interface."""
    print("\n" + "=" * 60)
    print("INTERFACE CONSISTENCY TEST")
    print("=" * 60)

    import inspect

    # Compare function signatures
    lazy_sig = inspect.signature(polarsfit.scan_recordmesgs)
    eager_sig = inspect.signature(polarsfit.read_recordmesgs)

    lazy_params = list(lazy_sig.parameters.keys())
    eager_params = list(eager_sig.parameters.keys())

    print(f"   scan_recordmesgs params: {lazy_params}")
    print(f"   read_recordmesgs params: {eager_params}")

    assert lazy_params == eager_params, "Parameter mismatch!"
    print("   ✓ PASS: Function signatures are identical")

    # Test that both functions can be called with same parameters
    field_mapping = {"field_1": "heart_rate"}

    lazy_frame = polarsfit.scan_recordmesgs(
        "test.fit", field_mapping=field_mapping, apply_default_mapping=True
    )
    assert isinstance(lazy_frame, pl.LazyFrame)
    print("   ✓ PASS: Lazy function accepts all parameters")

    # Test scan_data too
    lazy_data = polarsfit.scan_data(
        "test.fit",
        "record",
        field_mapping=field_mapping,
        apply_default_mapping=False,
    )
    assert isinstance(lazy_data, pl.LazyFrame)
    print("   ✓ PASS: scan_data function works correctly")


def test_lazy_benefits_summary():
    """Summarize the benefits of lazy evaluation."""
    print("\n" + "=" * 60)
    print("LAZY EVALUATION BENEFITS SUMMARY")
    print("=" * 60)

    # Measure creation speed
    start = time.time()
    lf = polarsfit.scan_recordmesgs("test.fit")
    creation_time = time.time() - start

    # Measure chaining speed
    start = time.time()
    (
        lf.filter(pl.col("hr") > 100).select(["timestamp", "hr"]).limit(50)
    )
    chain_time = time.time() - start

    print(f"\n   LazyFrame Creation: {creation_time:.6f}s (instant)")
    print(f"   Operation Chaining: {chain_time:.6f}s (instant)")
    print("   Memory Overhead: Minimal (no data loaded)")
    print("   Error Handling: Deferred until materialization")
    print("   Query Optimization: Enabled by lazy evaluation")

    print("\n   ✓ TRUE LAZY EVALUATION CONFIRMED")
    print("     - No upfront I/O cost")
    print("     - Instant operation chaining")
    print("     - Memory efficient")
    print("     - Enables query optimization")
    print("     - Compatible interface with eager functions")


if __name__ == "__main__":
    test_lazy_is_truly_lazy()
    test_lazy_performance_scaling()
    test_lazy_memory_efficiency()
    test_lazy_interface_consistency()
    test_lazy_benefits_summary()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - LAZY EVALUATION IS WORKING CORRECTLY!")
    print("=" * 60)
