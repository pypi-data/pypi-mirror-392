use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::Error;
use crate::{error::ResultExt, ErrorKind};
// Keep for Error::Other construction if needed temporarily
use derivative::Derivative;
use ndarray::{stack, Array2, Array3, Axis};
use rand::rngs::StdRng;
use std::path::Path;
use url::Url;

#[cfg(feature = "hdf5")]
fn open_hdf5_depthrgb(path: impl AsRef<Path>) -> Result<(Array3<f32>, Array2<f32>), Error> {
    let f = hdf5::File::open(path.as_ref()).path_context(path.as_ref())?;
    let rgb: Array3<u8> = f.dataset("rgb")?.read()?;
    let rgb = rgb
        .permuted_axes((2, 1, 0)) // Original is (3, W, H), need (H, W, 3)
        .mapv(|x| x as f32 / 255.0);
    let d: Array2<f32> = f.dataset("depth")?.read()?.permuted_axes((1, 0)); // Original is (W, H), need (H, W)
    Ok((rgb, d))
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_depthrgb(_path: impl AsRef<Path>) -> Result<(Array3<f32>, Array2<f32>), Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct NyuDepth {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub is_train: bool,
    pub normalize_depth: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<(String, String)>,
}

#[typetag::serde]
impl Dataset for NyuDepth {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        for d in dir_path.read_dir().path_context(&dir_path)? {
            let d = d?;
            if !d.file_type()?.is_dir() {
                continue;
            }
            let scene = d.file_name().into_string().unwrap();
            for d in d.path().read_dir().path_context(&d.path())? {
                let d = d?;
                if !d.file_type()?.is_file() {
                    continue;
                }
                let name = d.file_name().into_string().unwrap();
                let Some(name) = name.strip_suffix(".h5") else {
                    continue;
                };
                self.found.push((scene.to_owned(), name.to_owned()));
            }
        }
        self.found.sort();
        self.base.check_count(self.found.len())?;
        Ok(())
    }

    fn count(&self) -> usize {
        self.found.len()
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let (scene, name) = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let dir_path = ctx.resolve_to_path(&self.dir)?;

        let (mut render, mut depth) =
            open_hdf5_depthrgb(dir_path.join(scene).join(format!("{name}.h5")))?;

        if self.normalize_depth {
            let maxdepth = depth
                .iter()
                .copied()
                .filter(|d| *d < 10.0 && *d > 0.0) // NYU Depth v2 depths are in meters
                .max_by(|a, b| a.partial_cmp(b).unwrap())
                .unwrap_or(10.0)
                .max(0.01);
            depth.mapv_inplace(|d| {
                if d <= 0.0 || d > maxdepth || !d.is_finite() {
                    1.0
                } else {
                    d / maxdepth
                }
            });
        }

        let depth = stack![Axis(2), depth.view(), depth.view(), depth.view()];
        render.mapv_inplace(|x| x.clamp(0.0, 1.0)); // Already normalized in open_hdf5_depthrgb

        rows.image("image", render);
        rows.image("depth", depth);
        rows.name(format!("{scene}_{name}"));

        // TODO: Previous call was process_images_careful(rows, crop, vec2(0.0, 12.0), vec2(0.5, 0.5));
        // This forced a specific crop/offset. Current resize_images uses random offsets.
        // Also, the crop value depended on whether it was train or val.
        // let crop = if self.is_train { rng.gen_range(0.0f32..=1.0).powi(2) } else { 0.0 };
        self.base.resize_images(rows, rng, ctx)?;
        Ok(())
    }
}
