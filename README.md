# polarsfit

A fast Polars plugin for reading FIT (Flexible and Interoperable Data Transfer) files.

## Features

-   ✅ **Read FIT record messages** - Extract GPS tracks, heart rate, power, and sensor data
-   ✅ **Native Polars integration** - Returns polars DataFrames directly
-   ✅ **High performance** - Built with Rust for optimal speed
-   ✅ **Type safety** - Proper handling of all FIT data types

## Installation

```bash
pip install polarsfit
```

## Quick Start

```python
import polarsfit

# Read record messages from a FIT file
df = polarsfit.read_recordmesgs("path/to/your/file.fit")

print(f"Shape: {df.shape}")
print(df.head())
```

## Example Output

```
Shape: (1639, 26)
┌────────────┬───────────┬──────────┬─────────┬────────────┬───────┐
│ timestamp  ┆ latitude  ┆ longitude┆ distance┆ heart_rate ┆ power │
│ ---        ┆ ---       ┆ ---      ┆ ---     ┆ ---        ┆ ---   │
│ u32        ┆ f32       ┆ f32      ┆ u32     ┆ u32        ┆ u32   │
╞════════════╪═══════════╪══════════╪═════════╪════════════╪═══════╡
│ 1754121245 ┆ 50.709087 ┆ 7.150512 ┆ 84      ┆ 94         ┆ 318   │
│ 1754121246 ┆ 50.709072 ┆ 7.150495 ┆ 285     ┆ 94         ┆ 325   │
│ 1754121247 ┆ 50.709057 ┆ 7.150484 ┆ 498     ┆ 93         ┆ 312   │
└────────────┴───────────┴──────────┴─────────┴────────────┴───────┘
```

See [USAGE.md](USAGE.md) for detailed documentation and examples.

## Roadmap

-   🔄 Additional message types (laps, splits, device info)
-   🔄 Lazy evaluation support
-   🔄 Automatic field name mapping
-   🔄 Multi-file batch processing

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run python test_polarsfit.py

# Advanced example
uv run python test_advanced.py
```

## License

MIT License - see LICENSE file for details.

plf.read_recordmesgs(file)

```

Under the hood, this uses `fitparse-rs` to parse `.fit` files.

## Info

Find this repository on [Github](https://github.com/thomascamminady/polarsfit) or check out the [documentation](https://thomascamminady.github.io/polarsfit).

## Development

Set up the full project by running `make`.

## Documentation

Go to `Settings->Pages` and set `Source` (under `Build and deployment`) to `Github Actions`.

## Credits

This package was created with [`cookiecutter`](https://github.com/audreyr/cookiecutter) and [`thomascamminady/cookiecutter-pypackage`](https://github.com/thomascamminady/cookiecutter-pypackage), a fork of [`audreyr/cookiecutter-pypackage`](https://github.com/audreyr/cookiecutter-pypackage).
```
