use pyo3::prelude::*;
use uuid::Uuid;

#[pyfunction]
fn uuid4() -> PyResult<String> {
    Ok(Uuid::new_v4().to_string())
}

#[pymodule]
fn ruuid4(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(uuid4, m)?)?;
    Ok(())
}