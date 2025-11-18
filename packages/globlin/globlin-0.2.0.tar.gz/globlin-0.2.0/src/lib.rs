// SPDX-FileCopyrightText: 2025 László Vaskó <opensource@vlaci.email.com>
//
// SPDX-License-Identifier: EUPL-1.2
mod glob;

#[pyo3::pymodule]
mod globlin {
    use pyo3::prelude::*;
    use pyo3::types::PyTuple;

    #[pyfunction]
    #[pyo3(signature = (pattern, value, *flags))]
    fn fnmatch(pattern: &str, value: &str, flags: &Bound<'_, PyTuple>) -> PyResult<bool> {
        let mut glob_flags = if flags.is_empty() {
            crate::glob::flags::DEFAULT
        } else {
            crate::glob::flags::EMPTY
        };
        for flag in flags.iter() {
            let flag = flag.extract::<Flag>()?;
            match flag {
                Flag::EMPTY => glob_flags |= crate::glob::flags::EMPTY,
                Flag::GLOB_STAR => glob_flags |= crate::glob::flags::GLOB_STAR,
                Flag::BRACKET_EXPANSION => glob_flags |= crate::glob::flags::BRACKET_EXPANSION,
                Flag::BRACE_EXPANSION => glob_flags |= crate::glob::flags::BRACE_EXPANSION,
                Flag::NEGATE => glob_flags |= crate::glob::flags::NEGATE,
                Flag::ESCAPE => glob_flags |= crate::glob::flags::ESCAPE,
                Flag::NO_PATH => glob_flags |= crate::glob::flags::NO_PATH,
            }
        }
        Ok(crate::glob::glob_match(pattern, value, glob_flags))
    }

    #[allow(non_camel_case_types)]
    #[allow(clippy::upper_case_acronyms)]
    #[pyclass(eq)]
    #[derive(Clone, PartialEq)]
    enum Flag {
        EMPTY,
        GLOB_STAR,
        BRACKET_EXPANSION,
        BRACE_EXPANSION,
        NEGATE,
        ESCAPE,
        NO_PATH,
    }

    #[cfg(test)]
    mod test {
        use super::*;

        #[test]
        fn test_python_api() {
            Python::initialize();

            Python::attach(|py| {
                assert!(fnmatch("foo*", "foobar", &PyTuple::empty(py)).unwrap());
            })
        }
    }
}
