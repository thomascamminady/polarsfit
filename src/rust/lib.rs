use pyo3::prelude::*;

mod expressions;
mod io;

use io::{read_recordmesgs, get_message_types, read_data, scan_recordmesgs, scan_data};

#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(read_recordmesgs, m)?)?;
    m.add_function(wrap_pyfunction!(get_message_types, m)?)?;
    m.add_function(wrap_pyfunction!(read_data, m)?)?;
    m.add_function(wrap_pyfunction!(scan_recordmesgs, m)?)?;
    m.add_function(wrap_pyfunction!(scan_data, m)?)?;
    Ok(())
}
