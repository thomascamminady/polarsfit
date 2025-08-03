#!/usr/bin/env python3
"""Performance benchmarks for polarsfit."""

import os
import time
from pathlib import Path

import psutil

import polarsfit


def test_benchmark_read_performance():
    """Benchmark read performance of polarsfit."""
    test_file = Path("tests/data/30378-142636426.fit")

    if not test_file.exists():
        print("❌ Test file not found for benchmarking")
        return

    # Get file size
    file_size = test_file.stat().st_size
    print(f"📊 Benchmarking file: {test_file.name} ({file_size:,} bytes)")

    # Measure memory before
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss / 1024 / 1024  # MB

    # Time the read operation
    start_time = time.time()
    df = polarsfit.read_recordmesgs(str(test_file))
    end_time = time.time()

    # Measure memory after
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    memory_used = memory_after - memory_before

    # Calculate metrics
    read_time = end_time - start_time
    records_per_second = df.shape[0] / read_time
    bytes_per_second = file_size / read_time

    print(f"⏱️  Read time: {read_time:.3f} seconds")
    print(f"🔢 Records: {df.shape[0]:,}")
    print(f"📈 Columns: {df.shape[1]}")
    print(f"🚀 Performance: {records_per_second:,.0f} records/sec")
    print(f"💾 Throughput: {bytes_per_second / 1024 / 1024:.1f} MB/sec")
    print(f"🧠 Memory used: {memory_used:.1f} MB")

    return {
        "read_time": read_time,
        "records": df.shape[0],
        "columns": df.shape[1],
        "records_per_second": records_per_second,
        "memory_used_mb": memory_used,
        "file_size_bytes": file_size,
    }


def test_benchmark_multiple_reads():
    """Test consistency of multiple read operations."""
    test_file = Path("tests/data/30378-142636426.fit")

    if not test_file.exists():
        print("❌ Test file not found for benchmarking")
        return

    print("🔄 Running multiple read benchmark...")

    times = []
    for i in range(5):
        start_time = time.time()
        df = polarsfit.read_recordmesgs(str(test_file))
        end_time = time.time()

        read_time = end_time - start_time
        times.append(read_time)
        print(f"   Read {i + 1}: {read_time:.3f}s ({df.shape[0]} records)")

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"📊 Average: {avg_time:.3f}s")
    print(f"📊 Min: {min_time:.3f}s")
    print(f"📊 Max: {max_time:.3f}s")
    print(
        f"📊 Std dev: {(sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5:.3f}s"
    )


if __name__ == "__main__":
    print("🏃‍♂️ Running polarsfit performance benchmarks...")
    print("=" * 50)

    test_benchmark_read_performance()
    print()
    test_benchmark_multiple_reads()

    print("=" * 50)
    print("✅ Benchmarking complete!")
