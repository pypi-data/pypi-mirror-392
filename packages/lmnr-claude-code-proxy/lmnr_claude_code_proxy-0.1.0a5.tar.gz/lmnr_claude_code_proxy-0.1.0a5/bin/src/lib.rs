mod anthropic;
mod proto;
mod proxy;
mod python_interface;
mod server;
mod spans;
mod state;

use pyo3::prelude::PyModuleMethods;

use python_interface::{run, stop};

/// Python module definition
#[pyo3::prelude::pymodule]
fn lmnr_claude_code_proxy(
    m: &pyo3::Bound<'_, pyo3::prelude::PyModule>,
) -> pyo3::prelude::PyResult<()> {
    m.add_function(pyo3::wrap_pyfunction!(run, m)?)?;
    m.add_function(pyo3::wrap_pyfunction!(stop, m)?)?;
    Ok(())
}
