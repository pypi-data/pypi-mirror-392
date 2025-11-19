#[pyo3::pymodule]
mod gfxds {
    use ::gfxds::dataset::DatasetContext;
    use ::gfxds::loader::Loader;
    use ::gfxds::warp;
    use ::gfxds::{imgutil, rast};
    use anyhow::{anyhow, bail, Error};
    use futures_lite::future::block_on;
    use gfxds::dataset::Rows;
    use image::{DynamicImage, ImageFormat};
    use numpy::{PyArray3, PyArrayMethods};
    use once_cell::sync::OnceCell;
    use pyo3::prelude::*;
    use pyo3::types::{PyBytes, PyDict};
    use pythonize::{depythonize, pythonize};
    use std::collections::HashMap;
    use std::fs;
    use std::io::Cursor;
    use std::path::{Path, PathBuf};

    #[pyo3::pyfunction]
    #[pyo3(name = "save_image", signature = (path, arr, int16=true, ext=None))]
    fn save_image_py<'py>(
        py: Python<'py>,
        path: PathBuf,
        arr: Bound<'py, PyArray3<f32>>,
        int16: bool,
        ext: Option<&str>,
    ) -> Result<Option<Bound<'py, PyBytes>>, Error> {
        let ext = ext.or(path.extension().map(|s| s.to_str().unwrap()));
        let arr = arr.to_owned_array();
        let img: DynamicImage = match (ext, int16) {
            (Some("exr"), _) => imgutil::array2rgbf(arr).into(),
            (_, true) => imgutil::array2rgb16(arr).into(),
            (_, false) => imgutil::array2rgb8(arr).into(),
        };
        if path.as_path() == Path::new("-") {
            let mut buf = Vec::new();
            if int16 {
                img.write_to(
                    &mut Cursor::new(&mut buf),
                    ImageFormat::from_extension(ext.unwrap_or("png")).unwrap(),
                )?;
            };
            return Ok(Some(PyBytes::new(py, &buf)));
        }
        if let Some(parent) = path.parent() {
            let _ = fs::create_dir_all(parent);
        }
        img.save(path)?;
        Ok(None)
    }

    #[pyo3::pyfunction]
    #[pyo3(name = "open_image")]
    fn open_image_py<'py>(
        py: Python<'py>,
        path: PathBuf,
    ) -> Result<Bound<'py, PyArray3<f32>>, Error> {
        let img = imgutil::open_image(&path)?;
        Ok(PyArray3::from_owned_array(py, img))
    }

    #[pyo3::pyfunction]
    #[pyo3(name = "open_svbrdf", signature = (base, name=None, /))]
    fn open_svbrdf_py<'py>(
        py: Python<'py>,
        base: PathBuf,
        name: Option<String>,
    ) -> Result<Bound<'py, PyArray3<f32>>, Error> {
        use imgutil::open_image;
        use ndarray::{concatenate, s, Axis};
        let name = name.as_ref();

        let mut diffuse: Option<PathBuf> = None;
        let mut specular: Option<PathBuf> = None;
        let mut roughness: Option<PathBuf> = None;
        let mut normals: Option<PathBuf> = None;

        for e in fs::read_dir(&base)? {
            let e = e?;
            let Ok(name) = e.file_name().into_string() else {
                continue;
            };

            if name.contains("diffuse")
                && !name.contains(".in.")
                && !name.contains(".mask.")
                && !name.ends_with("_error")
            {
                if let Some(prev) = &diffuse {
                    bail!(
                        "found multiple diffuse maps: {} and {}",
                        prev.display(),
                        e.path().display()
                    );
                }
                diffuse = Some(e.path());
            }
            if name.contains("specular")
                && !name.contains(".in.")
                && !name.contains(".mask.")
                && !name.ends_with("_error")
            {
                if let Some(prev) = &specular {
                    bail!(
                        "found multiple specular maps: {} and {}",
                        prev.display(),
                        e.path().display()
                    );
                }
                specular = Some(e.path());
            }
            if name.contains("roughness")
                && !name.contains(".in.")
                && !name.contains(".mask.")
                && !name.ends_with("_error")
            {
                if let Some(prev) = &roughness {
                    bail!(
                        "found multiple roughness maps: {} and {}",
                        prev.display(),
                        e.path().display()
                    );
                }
                roughness = Some(e.path());
            }
            if name.contains("normals")
                && !name.contains(".in.")
                && !name.contains(".mask.")
                && !name.ends_with("_error")
            {
                if let Some(prev) = &normals {
                    bail!(
                        "found multiple normal maps: {} and {}",
                        prev.display(),
                        e.path().display()
                    );
                }
                normals = Some(e.path());
            }
        }

        let base_d = base.display();
        let mut diffuse = diffuse.ok_or(anyhow!("missing diffuse in {base_d}"))?;
        let mut specular = specular.ok_or(anyhow!("missing specular in {base_d}"))?;
        let mut roughness = roughness.ok_or(anyhow!("missing roughness in {base_d}"))?;
        let mut normals = normals.ok_or(anyhow!("missing normals in {base_d}"))?;

        if diffuse.is_dir() && name.is_some() {
            diffuse = diffuse.join(format!("{}_diffuse.png", name.unwrap()));
        }
        if specular.is_dir() && name.is_some() {
            specular = specular.join(format!("{}_specular.png", name.unwrap()));
        }
        if roughness.is_dir() && name.is_some() {
            roughness = roughness.join(format!("{}_roughness.png", name.unwrap()));
        }
        if normals.is_dir() && name.is_some() {
            normals = normals.join(format!("{}_normals.png", name.unwrap()));
        }

        let diffuse = open_image(&diffuse)?;
        let specular = open_image(&specular)?;
        let roughness = open_image(&roughness)?;
        let normals = open_image(&normals)?;
        let svbrdf = concatenate(
            Axis(2),
            &[
                diffuse.view(),
                specular.view(),
                roughness.slice(s![.., .., ..1]),
                normals.view(),
            ],
        )?;
        Ok(PyArray3::from_owned_array(py, svbrdf))
    }

    #[pyo3::pyfunction]
    #[pyo3(name = "rasterize", signature = (svbrdf, **kwargs))]
    fn py_rasterize<'py>(
        py: Python<'py>,
        svbrdf: Bound<'py, PyArray3<f32>>,
        kwargs: Option<Bound<'py, PyAny>>,
    ) -> Result<Bound<'py, PyArray3<f32>>, Error> {
        use ndarray::Array3;

        let args: rast::RenderArgs =
            depythonize(&kwargs.ok_or(anyhow!("must provide arguments"))?)?;
        let svbrdf = svbrdf.to_owned_array();
        let mut output = Array3::zeros([svbrdf.dim().0, svbrdf.dim().1, 6]);
        rast::render_any(svbrdf.view(), output.view_mut(), args);
        Ok(PyArray3::from_owned_array(py, output))
    }

    #[pyo3::pyfunction]
    #[pyo3(name = "resize_and_crop", signature = (source, width, height=None, crop=0.0, offset=(0.5, 0.5), with_cropinfo=None))]
    fn py_resize_and_crop<'py>(
        py: Python<'py>,
        source: Bound<'py, PyArray3<f32>>,
        width: usize,
        height: Option<usize>,
        crop: f32,
        offset: (f32, f32),
        with_cropinfo: Option<Bound<'py, PyAny>>,
    ) -> Result<Bound<'py, PyArray3<f32>>, Error> {
        use cgmath::vec2;
        use ndarray::Array3;

        let source = source.to_owned_array();
        let mut dest = Array3::zeros([height.unwrap_or(width), width, source.dim().2]);
        let cropinfo = warp::resize_and_crop(
            source.view(),
            dest.view_mut(),
            crop,
            vec2(offset.0, offset.1),
        );
        if let Some(with_cropinfo) = with_cropinfo {
            with_cropinfo.call1(([
                cropinfo.source_w,
                cropinfo.source_h,
                cropinfo.offset_x,
                cropinfo.offset_y,
                dest.dim().0 as f32,
                dest.dim().1 as f32,
            ],))?;
        }
        Ok(PyArray3::from_owned_array(py, dest))
    }

    #[pyo3::pyfunction]
    fn default_config<'py>(py: Python<'py>) -> Result<Bound<'py, PyAny>, PyErr> {
        Ok(pythonize(py, &DatasetContext::default_config())?)
    }
    #[pyo3::pyfunction]
    fn default_config_toml() -> &'static str {
        DatasetContext::default_config_toml()
    }

    #[pyo3::pyclass(name = "Loader")]
    pub struct PyLoader {
        inner: Loader,
    }

    #[pyo3::pymethods]
    impl PyLoader {
        #[new]
        #[pyo3(signature = (root, dataset, seed=None, concurrent=4, replacement=false, epocs=1, limit=None, offset=0, stride=1, resize=None, configs=HashMap::new()))]
        pub fn new<'py>(
            root: PathBuf,
            dataset: Bound<'py, PyAny>,
            seed: Option<u64>,
            concurrent: usize,
            replacement: bool,
            epocs: usize,
            limit: Option<usize>,
            offset: usize,
            stride: usize,
            resize: Option<(usize, usize)>,
            configs: HashMap<String, Bound<'py, PyAny>>,
        ) -> Result<Self, Error> {
            let mut ctx = DatasetContext::default();
            ctx.root = root;
            ctx.resize_override = resize;
            for (id, overloads) in configs {
                ctx.config.insert(id, depythonize(&overloads)?);
            }
            let seed = match seed {
                Some(s) => s,
                None => getrandom::u64().map_err(|_| {
                    anyhow!("could not generate seed from entropy, please provide it")
                })?,
            };
            let mut inner = if let Ok(id) = dataset.extract::<&str>() {
                Loader::new_with_id(seed, ctx, id)?
            } else {
                Loader::new(seed, ctx, depythonize(&dataset)?)?
            };
            inner.replacement = replacement;
            inner.concurrent = concurrent;
            inner.remaining_epocs = epocs;
            inner.sample_limit = limit;
            inner.offset = offset;
            inner.stride = stride;
            Ok(PyLoader { inner })
        }

        #[getter]
        pub fn resolved_config<'py>(&self, py: Python<'py>) -> Result<Bound<'py, PyAny>, PyErr> {
            Ok(pythonize(py, &*self.inner.dataset)?)
        }

        pub fn start(&mut self) -> Result<(), Error> {
            self.inner.start()?;
            Ok(())
        }

        pub fn __getitem__<'py>(
            &self,
            py: Python<'py>,
            index: usize,
        ) -> Result<Bound<'py, PyAny>, PyErr> {
            let rows = match self.inner.get(index) {
                Ok(rows) => rows,
                Err(err) => return Err(Error::from(err).into()),
            };
            Ok(make_rows(py, rows)?)
        }

        pub fn __len__(&self) -> Result<usize, PyErr> {
            if self.inner.started() {
                Ok(self.inner.total())
            } else {
                Err(pyo3::exceptions::PyValueError::new_err(
                    "data loader not started",
                ))
            }
        }

        pub fn __iter__<'py>(mut this: PyRefMut<'py, Self>) -> Result<PyRefMut<'py, Self>, Error> {
            this.inner.start()?;
            Ok(this)
        }

        pub fn __next__<'py>(&mut self, py: Python<'py>) -> Result<Bound<'py, PyAny>, PyErr> {
            let rows = match block_on(self.inner.next()) {
                Some(Ok(r)) => r,
                Some(Err(err)) => return Err(Error::from(err).into()),
                None => {
                    return Err(pyo3::exceptions::PyStopIteration::new_err(
                        "no more samples",
                    ))
                }
            };
            Ok(make_rows(py, rows)?)
        }
    }

    static IMAGE_ROW: OnceCell<Py<PyAny>> = OnceCell::new();
    static ROWS: OnceCell<Py<PyAny>> = OnceCell::new();

    fn make_rows<'py>(py: Python<'py>, rows: Rows) -> Result<Bound<'py, PyAny>, PyErr> {
        let images = PyDict::new(py);
        let image_row_cls = IMAGE_ROW.get().unwrap().bind(py);
        for (component, image) in rows.images {
            let kwargs = PyDict::new(py);
            kwargs.set_item("image", PyArray3::from_owned_array(py, image.image))?;
            kwargs.set_item("crop", None::<()>)?;
            images.set_item(component, image_row_cls.call((), Some(&kwargs))?)?;
        }
        let rows_cls = ROWS.get().unwrap().bind(py);
        let kwargs = PyDict::new(py);
        kwargs.set_item("name", rows.name)?;
        kwargs.set_item("caption", rows.caption)?;
        kwargs.set_item("images", images)?;
        Ok(rows_cls.call((), Some(&kwargs))?)
    }

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        let make_dataclass = m.py().import("dataclasses")?.getattr("make_dataclass")?;
        let _ = IMAGE_ROW.set(
            make_dataclass
                .call1(("ImageRow", ["image", "crop"]))?
                .unbind(),
        );
        m.add("ImageRow", IMAGE_ROW.get().unwrap())?;
        let _ = ROWS.set(
            make_dataclass
                .call1(("Rows", ["name", "caption", "images"]))?
                .unbind(),
        );
        m.add("Rows", ROWS.get().unwrap())?;
        Ok(())
    }
}
