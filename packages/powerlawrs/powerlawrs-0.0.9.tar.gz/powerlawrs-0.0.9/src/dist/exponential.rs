// Copyright (c) 2025 Adam Ulichny
//
// This source code is licensed under the MIT OR Apache-2.0 license
// that can be found in the LICENSE-MIT or LICENSE-APACHE files
// at the root of this source tree.

//! PyO3 wrappers for the Exponential distribution from the `powerlaw` crate.
//! This file provides thin wrappers that call the functionality from the `powerlaw` crate.

use powerlaw::dist::{exponential::Exponential, Distribution};
use pyo3::prelude::*;

/// A Python-compatible wrapper for the `Exponential` struct from the `powerlaw` crate.
///
/// This class represents an Exponential distribution.
/// It does not contain any logic itself, but calls the underlying Rust implementation.
#[pyclass(name = "Exponential")]
struct PyExponential {
    inner: Exponential,
}

#[pymethods]
impl PyExponential {
    /// Creates a new Exponential distribution instance.
    ///
    /// Args:
    ///     lambda (float): The rate parameter of the distribution. Must be > 0.
    #[new]
    fn new(lambda: f64) -> PyResult<Self> {
        if lambda <= 0.0 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "lambda must be positive.",
            ));
        }
        // This creates an instance of the original Exponential struct from the `powerlaw` crate.
        Ok(PyExponential {
            inner: Exponential { lambda },
        })
    }

    /// Calls the underlying `pdf` method from the `powerlaw` crate.
    #[pyo3(text_signature = "($self, x)")]
    fn pdf(&self, x: f64) -> f64 {
        self.inner.pdf(x)
    }

    /// Calls the underlying `cdf` method from the `powerlaw` crate.
    #[pyo3(text_signature = "($self, x)")]
    fn cdf(&self, x: f64) -> f64 {
        self.inner.cdf(x)
    }

    /// Calls the underlying `ccdf` method from the `powerlaw` crate.
    #[pyo3(text_signature = "($self, x)")]
    fn ccdf(&self, x: f64) -> f64 {
        self.inner.ccdf(x)
    }

    /// Calls the underlying `rv` method from the `powerlaw` crate.
    ///
    /// Args:
    ///     u (float): A random number from a Uniform(0, 1) distribution.
    #[pyo3(text_signature = "($self, u)")]
    fn rv(&self, u: f64) -> f64 {
        self.inner.rv(u)
    }

    #[getter]
    fn lambda(&self) -> f64 {
        self.inner.lambda
    }
}

/// Creates the 'exponential' Python submodule.
pub fn create_module(py: Python<'_>) -> PyResult<Bound<'_, PyModule>> {
    let m = PyModule::new(py, "exponential")?;
    m.add_class::<PyExponential>()?;
    Ok(m)
}
