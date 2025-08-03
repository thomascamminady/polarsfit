use pyo3::prelude::*;

mod expressions;
mod io;

use io::read_recordmesgs;

#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(read_recordmesgs, m)?)?;
    Ok(())
}
