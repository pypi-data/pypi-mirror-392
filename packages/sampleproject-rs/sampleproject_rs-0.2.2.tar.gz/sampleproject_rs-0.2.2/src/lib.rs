use pyo3::prelude::*;

#[pyfunction]
fn main() {
    println!("Call your main application code here");
}

#[pyfunction]
fn add_one(number: i32) -> i32 {
    number + 1
}

#[pymodule]
mod sample {
    use super::*;

    #[pymodule_export]
    use super::main;

    #[pymodule]
    mod simple {
        #[pymodule_export]
        use super::add_one;
    }
}

#[cfg(test)]
mod test_add_one {
    use super::add_one;

    #[test]
    fn 引数に1を加えた数を返す() {
        assert_eq!(add_one(1), 2);
        assert_eq!(add_one(-1), 0);
        assert_eq!(add_one(41), 42);
    }
}
