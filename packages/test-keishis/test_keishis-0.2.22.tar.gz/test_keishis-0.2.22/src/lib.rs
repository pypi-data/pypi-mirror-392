#[cfg(feature = "python")]
use pyo3::prelude::*;

fn sum_as_str(a: i64, b: i64) -> String {
    (a + b).to_string()
}

#[cfg(feature = "julia")]
#[unsafe(no_mangle)]
pub extern "C" fn mysum(a: i64, b: i64) -> i64 {
    a + b
}

/// A Python module implemented in Rust.
#[cfg(feature = "python")]
#[pymodule]
#[pyo3(name = "_test_keishis")]
mod test_keishis {
    use super::sum_as_str;
    use pyo3::prelude::*;

    #[pyfunction]
    fn sum_as_string(a: i64, b: i64) -> PyResult<String> {
        Ok(sum_as_str(a, b))
    }
}
