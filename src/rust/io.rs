use std::path::PathBuf;
use pyo3::prelude::*;
use pyo3_polars::{PyDataFrame, PyLazyFrame};
use polars::prelude::*;
use fit::{Fit, Value};
use std::collections::HashMap;

/// Read record messages from a .fit file and return as a Polars DataFrame
/// with optional field mapping
#[pyfunction]
#[pyo3(signature = (file_path, field_mapping = None))]
pub fn read_recordmesgs(file_path: &str, field_mapping: Option<HashMap<String, String>>) -> PyResult<PyDataFrame> {
    read_generic_messages(file_path, "record", field_mapping)
}

/// Scan record messages from a .fit file and return as a Polars LazyFrame
/// Note: File reading occurs immediately, but operations are lazy
#[pyfunction]
#[pyo3(signature = (file_path, field_mapping = None))]
pub fn scan_recordmesgs(file_path: &str, field_mapping: Option<HashMap<String, String>>) -> PyResult<PyLazyFrame> {
    let df = read_generic_messages(file_path, "record", field_mapping)?;
    Ok(PyLazyFrame(df.0.lazy()))
}

/// Get all available message types in a FIT file
#[pyfunction]
pub fn get_message_types(file_path: &str) -> PyResult<Vec<String>> {
    let path = PathBuf::from(file_path);
    let fit = Fit::new(&path);

    let mut message_types = std::collections::HashSet::new();

    for message in fit {
        let msg_type = format!("{:?}", message.kind).to_lowercase();
        message_types.insert(msg_type);
    }

    let mut result: Vec<String> = message_types.into_iter().collect();
    result.sort();
    Ok(result)
}

/// Read messages of a specific type from a .fit file and return as a Polars DataFrame
/// with optional field mapping
#[pyfunction]
#[pyo3(signature = (file_path, message_type, field_mapping = None))]
pub fn read_data(file_path: &str, message_type: &str, field_mapping: Option<HashMap<String, String>>) -> PyResult<PyDataFrame> {
    read_generic_messages(file_path, message_type, field_mapping)
}

/// Scan messages of a specific type from a .fit file and return as a Polars LazyFrame
/// Note: File reading occurs immediately, but operations are lazy
#[pyfunction]
#[pyo3(signature = (file_path, message_type, field_mapping = None))]
pub fn scan_data(file_path: &str, message_type: &str, field_mapping: Option<HashMap<String, String>>) -> PyResult<PyLazyFrame> {
    let df = read_generic_messages(file_path, message_type, field_mapping)?;
    Ok(PyLazyFrame(df.0.lazy()))
}

/// Internal function to read generic messages from a FIT file
fn read_generic_messages(file_path: &str, message_type: &str, field_mapping: Option<HashMap<String, String>>) -> PyResult<PyDataFrame> {
    let path = PathBuf::from(file_path);

    // Parse the FIT file
    let fit = Fit::new(&path);

    // Prepare data structures for DataFrame construction
    let mut columns: HashMap<String, Vec<AnyValue>> = HashMap::new();
    let mut column_order = Vec::new();

    // Process each message in the FIT file
    for message in fit {
        // Only process messages of the specified type
        if format!("{:?}", message.kind).to_lowercase() == message_type.to_lowercase() {

            // Iterate through all data fields in this message
            for field in &message.values {
                let raw_field_name = format!("field_{}", field.field_num);

                // Apply field mapping if provided
                let field_name = if let Some(ref mapping) = field_mapping {
                    mapping.get(&raw_field_name).cloned().unwrap_or(raw_field_name)
                } else {
                    raw_field_name
                };

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
