# polarsfit - A Polars Plugin for Reading FIT Files

polarsfit is a Polars plugin that provides fast, efficient reading of FIT (Flexible and Interoperable Data Transfer) files commonly used by fitness devices and sports applications.

## Installation

```bash
pip install polarsfit
```

## Quick Start

```python
import polarsfit
import polars as pl

# Read record messages from a FIT file
df = polarsfit.read_recordmesgs("path/to/your/file.fit")

print(f"Shape: {df.shape}")
print(f"Columns: {df.columns}")
print(df.head())
```

## Example: Processing GPS Fitness Data

```python
import polarsfit
import polars as pl

# Read the FIT file
df = polarsfit.read_recordmesgs("workout.fit")

# Map common field numbers to meaningful names
field_mapping = {
    'field_253': 'timestamp',     # Unix timestamp
    'field_0': 'position_lat',    # Latitude in semicircles
    'field_1': 'position_long',   # Longitude in semicircles
    'field_2': 'altitude',        # Altitude in meters
    'field_3': 'heart_rate',      # Heart rate in BPM
    'field_4': 'cadence',         # Cadence in RPM
    'field_5': 'distance',        # Distance in meters
    'field_6': 'speed',           # Speed in m/s
    'field_7': 'power',           # Power in watts
    'field_13': 'temperature',    # Temperature in Celsius
}

# Select and rename known columns
df_clean = df.select([
    pl.col(old_name).alias(new_name)
    for old_name, new_name in field_mapping.items()
    if old_name in df.columns
])

# Convert coordinates from semicircles to degrees
df_geo = df_clean.with_columns([
    (pl.col('position_lat') * 180.0 / 2**31).alias('latitude'),
    (pl.col('position_long') * 180.0 / 2**31).alias('longitude')
])

# Calculate some statistics
stats = df_geo.select([
    pl.col('distance').max().alias('total_distance_m'),
    pl.col('heart_rate').mean().alias('avg_heart_rate_bpm'),
    pl.col('power').filter(pl.col('power') > 0).mean().alias('avg_power_watts'),
    (pl.col('timestamp').max() - pl.col('timestamp').min()).alias('duration_seconds')
])

print("Workout Statistics:")
print(stats)
```

## Current Features

-   ✅ **Read record messages**: Extract GPS tracks, heart rate, power, and other sensor data
-   ✅ **Fast performance**: Built with Rust for optimal speed
-   ✅ **Native Polars integration**: Returns polars DataFrames directly
-   ✅ **Type safety**: Proper data type handling for all FIT data types

## Planned Features

-   🔄 **Additional message types**: Support for lap messages, split messages, device info, etc.
-   🔄 **Lazy evaluation**: Integration with Polars lazy frames for even better performance
-   🔄 **Field name resolution**: Automatic mapping of field numbers to meaningful names
-   🔄 **Multi-file support**: Read multiple FIT files into a single DataFrame

## Data Types

The plugin automatically handles all FIT data types:

-   **Numeric types**: UInt8, UInt16, UInt32, UInt64, Int8, Int16, Int32, Int64, Float32, Float64
-   **String types**: String data and enum values converted to strings
-   **Time types**: Timestamps as UInt32 values
-   **Array types**: Converted to string representations for now

## Common FIT Field Numbers

Here are some common field numbers you'll encounter in record messages:

| Field Number | Name          | Unit        | Description        |
| ------------ | ------------- | ----------- | ------------------ |
| 253          | timestamp     | s           | Unix timestamp     |
| 0            | position_lat  | semicircles | Latitude position  |
| 1            | position_long | semicircles | Longitude position |
| 2            | altitude      | m           | Altitude           |
| 3            | heart_rate    | bpm         | Heart rate         |
| 4            | cadence       | rpm         | Cadence            |
| 5            | distance      | m           | Distance           |
| 6            | speed         | m/s         | Speed              |
| 7            | power         | watts       | Power              |
| 13           | temperature   | °C          | Temperature        |

To convert coordinates from semicircles to degrees: `degrees = semicircles * 180.0 / 2^31`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
