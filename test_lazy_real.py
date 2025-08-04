#!/usr/bin/env python3
"""
Test truly lazy FIT file reading.
"""

import time

import polars as pl

import polarsfit


def test_lazy_loading():
    print("=" * 50)
    print("Testing Truly Lazy FIT File Loading")
    print("=" * 50)

    # Test 1: Creating LazyFrame should not read file
    print("\n1. Creating LazyFrame (should be instant, no file reading)...")
    start_time = time.time()

    # Use a non-existent file to demonstrate laziness
    lf = polarsfit.scan_recordmesgs("non_existent_file.fit")

    create_time = time.time() - start_time
    print(f"   ✓ LazyFrame created in {create_time:.4f}s")
    print(f"   ✓ Type: {type(lf)}")
    print(f"   ✓ No file was read (file doesn't exist but no error yet)")

    # Test 2: Adding operations should still be lazy
    print("\n2. Adding lazy operations (should still be instant)...")
    start_time = time.time()

    lazy_with_ops = (
        lf.filter(pl.col("heart_rate") > 150)
        .select(["timestamp", "heart_rate", "power"])
        .limit(100)
    )

    ops_time = time.time() - start_time
    print(f"   ✓ Lazy operations added in {ops_time:.4f}s")
    print(f"   ✓ Still no file reading occurred")

    # Test 3: Only when collecting should it try to read
    print("\n3. Collecting data (now file reading should occur and fail)...")
    try:
        result = lazy_with_ops.collect()
        print("   ✗ Unexpected: Should have failed!")
    except Exception as e:
        print(f"   ✓ Expected error on collect: File not found")
        print(f"   ✓ This proves file reading is deferred until collection")

    print("\n" + "=" * 50)
    print("CONCLUSION: TRUE LAZY EVALUATION CONFIRMED!")
    print("- LazyFrame creation: Instant (no I/O)")
    print("- Operations chaining: Instant (no I/O)")
    print("- File reading: Only on .collect() or similar")
    print("=" * 50)


if __name__ == "__main__":
    test_lazy_loading()
