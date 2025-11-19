use std::backtrace::Backtrace;
use std::fmt;
use std::path::{Path, PathBuf};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ErrorKind {
    #[error("empty dataset")]
    EmptyDataset,
    #[error("the sample at the given index should be ignored")]
    SkipSample,
    #[error("the given index is not valid for the dataset")]
    IllegalIndex,
    #[error("the thread paniced and did not produce a sample")]
    Paniced,
    #[error("expected to find {expected} samples but found {found}")]
    ExpectedCount { expected: usize, found: usize },
    #[error("dataset {0:?} is not defined by datasets.toml")]
    UnknownDataset(String),
    #[error("could not resolve {0} to a concrete path")]
    ResolvingUrlToPath(url::Url),
    #[error(transparent)]
    Io(#[from] std::io::Error),
    #[error(transparent)]
    Ureq(#[from] ureq::Error),
    #[error(transparent)]
    Image(#[from] image::ImageError),
    #[cfg(feature = "hdf5")]
    #[error(transparent)]
    Hdf5(#[from] hdf5::Error),
    #[error(transparent)]
    Parquet(#[from] parquet::errors::ParquetError),
    #[error(transparent)]
    Toml(#[from] toml::de::Error),
    #[error(transparent)]
    Json(#[from] serde_json::Error),
    #[error(transparent)]
    Regex(#[from] regex::Error),
    #[error(transparent)]
    Csv(#[from] csv::Error),
    #[error(transparent)]
    ShapeError(#[from] ndarray::ShapeError),
    #[error(transparent)]
    ReadNpyError(#[from] ndarray_npy::ReadNpyError),
    #[error(transparent)]
    ReadNpzError(#[from] ndarray_npy::ReadNpzError),
    #[error("gfxds was not compiled with feature {0:?}")]
    NotCompiledWithFeature(&'static str),
    #[error(transparent)]
    Other(#[from] anyhow::Error),
}

impl<E> From<E> for Error
where
    ErrorKind: From<E>,
{
    fn from(value: E) -> Self {
        Error {
            kind: value.into(),
            path: None,
            backtrace: Backtrace::capture(),
        }
    }
}

#[derive(Debug)]
pub struct Error {
    pub kind: ErrorKind,
    pub path: Option<PathBuf>,
    pub backtrace: Backtrace,
}

impl Error {
    pub fn other(msg: impl fmt::Display + fmt::Debug + Sync + Send + 'static) -> Self {
        Error {
            kind: ErrorKind::Other(anyhow::Error::msg(msg)),
            path: None,
            backtrace: Backtrace::capture(),
        }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if let Some(path) = &self.path {
            write!(f, "{} in {}\n{}", self.kind, path.display(), self.backtrace)
        } else {
            write!(f, "{}\n{}", self.kind, self.backtrace)
        }
    }
}

impl std::error::Error for Error {}

pub trait ResultExt<T, E> {
    fn path_context(self, path: &Path) -> Result<T, Error>;
}

impl<T, E> ResultExt<T, E> for Result<T, E>
where
    Error: From<E>,
{
    fn path_context(self, path: &Path) -> Result<T, Error> {
        let mut res = self.map_err(Error::from);
        if let Err(err) = &mut res {
            err.path = Some(path.to_owned());
        }
        res
    }
}

/*
impl From<Error> for PyErr {
    fn from(value: Error) -> Self {
        use Error::*;
        let text = value.to_string();
        match value {
            EmptyDataset | SkipSample | IllegalIndex => PyValueError::new_err(text),
            Io(error) => error.into(),
            WithPath(error, ref path) => match *error {
                Io(error) => PyErr::from(error),
                _ => PyRuntimeError::new_err(text),
            },
            _ => PyRuntimeError::new_err(text),
        }
    }
}
*/
