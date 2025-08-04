# Documentation

This directory contains comprehensive documentation for the polarsfit lazy evaluation implementation.

## Files

- **[LAZYFRAME_IMPLEMENTATION.md](LAZYFRAME_IMPLEMENTATION.md)** - Technical details of the LazyFrame implementation
- **[USAGE.md](USAGE.md)** - Usage guide and examples
- **[CSV_PERFORMANCE_RESULTS.md](CSV_PERFORMANCE_RESULTS.md)** - CSV performance comparison test results
- **[FIT_PERFORMANCE_RESULTS.md](FIT_PERFORMANCE_RESULTS.md)** - FIT file performance comparison results
- **[LAZY_TEST_RESULTS.md](LAZY_TEST_RESULTS.md)** - Comprehensive lazy evaluation test results

## Performance Summary

The lazy evaluation implementation provides dramatic performance improvements:

- **6813x faster** for scan vs read operations on FIT files
- **25x faster** for CSV scan vs read operations
- **1940x faster** for lazy operations with filtering
- **Sub-millisecond performance** for LazyFrame creation

## Key Features

- True lazy evaluation with deferred execution
- Polars query optimization support
- Memory efficient processing
- Compatible with existing polarsfit API
