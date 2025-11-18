mod expr;
mod function;

pub use expr::PyExpr;
pub use function::PyFunctionCall;

#[pyo3::pyfunction]
#[pyo3(signature=(arg1, *args))]
pub fn all(
    arg1: pyo3::Bound<'_, PyExpr>,
    args: &pyo3::Bound<'_, pyo3::types::PyTuple>,
) -> pyo3::PyResult<pyo3::Py<pyo3::PyAny>> {
    let py = arg1.py();
    let mut expr = arg1.unbind();

    for m in args {
        let m = m.cast_into_exact::<PyExpr>()?;

        let result = sea_query::ExprTrait::and(expr.get().inner.clone(), m.get().inner.clone());
        expr = pyo3::Py::new(py, PyExpr { inner: result })?;
    }

    Ok(expr.into_any())
}

#[pyo3::pyfunction]
#[pyo3(signature=(arg1, *args))]
pub fn any(
    arg1: pyo3::Bound<'_, PyExpr>,
    args: &pyo3::Bound<'_, pyo3::types::PyTuple>,
) -> pyo3::PyResult<pyo3::Py<pyo3::PyAny>> {
    let py = arg1.py();
    let mut expr = arg1.unbind();

    for m in args {
        let m = m.cast_into_exact::<PyExpr>()?;

        let result = sea_query::ExprTrait::or(expr.get().inner.clone(), m.get().inner.clone());
        expr = pyo3::Py::new(py, PyExpr { inner: result })?;
    }

    Ok(expr.into_any())
}

#[pyo3::pyfunction]
pub fn not_(arg: &pyo3::Bound<'_, PyExpr>) -> PyExpr {
    sea_query::ExprTrait::not(arg.get().inner.clone()).into()
}
