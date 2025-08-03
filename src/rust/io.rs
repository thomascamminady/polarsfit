use std::path::PathBuf;
use pyo3::prelude::*;
use pyo3_polars::PyDataFrame;
use polars::prelude::*;
use fit::{Fit, Value};
use std::collections::HashMap;

/// Read record messages from a .fit file and return as a Polars DataFrame
#[pyfunction]
pub fn read_recordmesgs(file_path: &str) -> PyResult<PyDataFrame> {
    let path = PathBuf::from(file_path);

    // Parse the FIT file
    let fit = Fit::new(&path);

    // Prepare data structures for DataFrame construction
    let mut columns: HashMap<String, Vec<AnyValue>> = HashMap::new();
    let mut column_order = Vec::new();

    // Process each message in the FIT file
    for message in fit {
        // Only process record messages (typical for activity data)
        if format!("{:?}", message.kind).to_lowercase() == "record" {

            // Iterate through all data fields in this record message
            for field in &message.values {
                let field_name = format!("field_{}", field.field_num);

                // Initialize column if not exists
                if !columns.contains_key(&field_name) {
                    columns.insert(field_name.clone(), Vec::new());
                    column_order.push(field_name.clone());
                }

                // Convert field value to AnyValue
                let any_value = match &field.value {
                    Value::U8(v) => AnyValue::UInt32(*v as u32),
                    Value::U16(v) => AnyValue::UInt32(*v as u32),
                    Value::U32(v) => AnyValue::UInt32(*v),
                    Value::U64(v) => AnyValue::UInt64(*v),
                    Value::I8(v) => AnyValue::Int32(*v as i32),
                    Value::I16(v) => AnyValue::Int32(*v as i32),
                    Value::I32(v) => AnyValue::Int32(*v),
                    Value::I64(v) => AnyValue::Int64(*v),
                    Value::F32(v) => AnyValue::Float32(*v),
                    Value::F64(v) => AnyValue::Float64(*v),
                    Value::String(v) => AnyValue::StringOwned(v.clone().into()),
                    Value::Enum(v) => AnyValue::StringOwned(v.to_string().into()),
                    Value::Time(v) => AnyValue::UInt32(*v), // Time is represented as u32
                    Value::ArrU8(v) => {
                        // Convert array to string representation for now
                        let array_str = v.iter()
                            .map(|x| x.to_string())
                            .collect::<Vec<_>>()
                            .join(",");
                        AnyValue::StringOwned(format!("[{}]", array_str).into())
                    },
                    Value::ArrU16(v) => {
                        // Convert array to string representation for now
                        let array_str = v.iter()
                            .map(|x| x.to_string())
                            .collect::<Vec<_>>()
                            .join(",");
                        AnyValue::StringOwned(format!("[{}]", array_str).into())
                    },
                    Value::ArrU32(v) => {
                        // Convert array to string representation for now
                        let array_str = v.iter()
                            .map(|x| x.to_string())
                            .collect::<Vec<_>>()
                            .join(",");
                        AnyValue::StringOwned(format!("[{}]", array_str).into())
                    },
                };

                columns.get_mut(&field_name).unwrap().push(any_value);
            }
        }
    }

    // Ensure all columns have the same length (fill with nulls if necessary)
    let max_len = columns.values().map(|v| v.len()).max().unwrap_or(0);
    for (_, column_data) in columns.iter_mut() {
        while column_data.len() < max_len {
            column_data.push(AnyValue::Null);
        }
    }

    // Create DataFrame
    let mut df_columns = Vec::new();
    for col_name in &column_order {
        if let Some(data) = columns.get(col_name) {
            let series = Series::from_any_values(col_name.as_str().into(), data, true)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create series: {}", e)))?;
            df_columns.push(series.into());
        }
    }

    let df = DataFrame::new(df_columns)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to create DataFrame: {}", e)))?;

    Ok(PyDataFrame(df))
}
