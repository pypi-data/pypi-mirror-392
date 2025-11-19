use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{apply_gamma, decide_whitepoint};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use ndarray::{s, stack, Array2, Array3, Axis};
use rand::rngs::StdRng;
use regex::Regex;
use serde::Deserialize;
use std::fs;
use std::path::{Path, PathBuf};
use url::Url;

#[cfg(feature = "hdf5")]
fn open_hdf5_image3(path: impl AsRef<Path>, key: &str) -> Result<Array3<f32>, Error> {
    let f = hdf5::File::open(path.as_ref()).path_context(path.as_ref())?;
    let d = f.dataset(key)?;
    Ok(d.read()?)
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_image3(_path: impl AsRef<Path>, _key: &str) -> Result<Array3<f32>, Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

#[cfg(feature = "hdf5")]
fn open_hdf5_image2(path: impl AsRef<Path>, key: &str) -> Result<Array2<f32>, Error> {
    let f = hdf5::File::open(path.as_ref()).path_context(path.as_ref())?;
    let d = f.dataset(key)?;
    Ok(d.read()?)
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_image2(_path: impl AsRef<Path>, _key: &str) -> Result<Array2<f32>, Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct BeyondRgb {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub root: Url,
    pub split: String,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<PathBuf>,
    pub groups: Vec<[usize; 3]>,
}

#[derive(Deserialize)]
struct CCMeta {
    /*chart_type: usize,
    patch_1: CCPatch,
    patch_2: CCPatch,
    patch_3: CCPatch,
    patch_4: CCPatch,
    patch_5: CCPatch,
    patch_6: CCPatch,
    patch_7: CCPatch,
    patch_8: CCPatch,
    patch_9: CCPatch,
    patch_10: CCPatch,
    patch_11: CCPatch,
    patch_12: CCPatch,
    patch_13: CCPatch,
    patch_14: CCPatch,
    patch_15: CCPatch,
    patch_16: CCPatch,
    patch_17: CCPatch,
    patch_18: CCPatch,*/
    patch_19: CCPatch,
    patch_20: CCPatch,
    patch_21: CCPatch,
    patch_22: CCPatch,
    patch_23: CCPatch,
    patch_24: CCPatch,
    /*image_height: usize,
    image_width: usize,*/
}

impl CCMeta {
    fn grey(self) -> [CCPatch; 6] {
        return [
            self.patch_19,
            self.patch_20,
            self.patch_21,
            self.patch_22,
            self.patch_23,
            self.patch_24,
        ];
    }
}

#[derive(Deserialize)]
struct CCPatch {
    //id: usize,
    corners: [(f32, f32); 4],
}

fn open_ms_image(path: &Path) -> Result<Array3<f32>, Error> {
    let img = open_hdf5_image2(path, "MIS")?;
    let (w, h) = img.dim();
    let img = img.to_shape([w / 4, 4, h / 4, 4])?;
    let img = img.permuted_axes([0, 2, 1, 3]);
    let img = img.to_shape([w / 4, h / 4, 16])?;
    let img = img.as_standard_layout().to_owned();
    Ok(img)
}

fn adjust_whitepoint_from_cc(
    source: &Array3<f32>,
    dest: &mut Array3<f32>,
    cc: &Path,
    scale: f32,
) -> Result<(), Error> {
    let (h, w, c) = source.dim();
    let ms_ccmeta: CCMeta =
        serde_json::from_reader(fs::File::open(cc).path_context(cc)?).path_context(cc)?;
    let mut ratio_sums = vec![(0.0, 0); c];
    for patch in ms_ccmeta.grey() {
        let x: f32 = patch.corners.iter().map(|(_, x)| *x / (scale * 4.0)).sum();
        let y: f32 = patch.corners.iter().map(|(y, _)| *y / (scale * 4.0)).sum();
        for x in [x - 1.0, x, x + 1.0] {
            for y in [y - 1.0, y, y + 1.0] {
                if x <= 0.0 || x >= w as f32 || y <= 0.0 || y >= h as f32 {
                    continue;
                }
                let x = x as usize;
                let y = y as usize;
                //dest.slice_mut(s![x, y, ..]).mapv_inplace(|_| 0.0);
                let p = source.slice(s![x, y, ..]);
                let mut chan_sum = (0.0, 0);
                for &x in p {
                    if x < 1.0 {
                        chan_sum.0 += x;
                        chan_sum.1 += 1;
                    }
                }
                if chan_sum.1 == 0 {
                    continue;
                }
                let avg = chan_sum.0 / chan_sum.1 as f32;
                for (i, &x) in p.into_iter().enumerate() {
                    if x < 1.0 && x > 0.005 {
                        ratio_sums[i].0 += avg / x;
                        ratio_sums[i].1 += 1;
                    }
                }
            }
        }
    }
    let ratios: Vec<f32> = ratio_sums
        .into_iter()
        .map(|sum| sum.0 / sum.1 as f32)
        .collect();
    if !ratios.iter().all(|x| x.is_finite()) {
        // Using Error::Other for simplicity, could define a more specific variant
        return Err(Error::other(
            "bad attempt to calibrate whitepoint: ratios contain non-finite values",
        )
        .into());
    }

    for i in 0..c {
        dest.slice_mut(s![.., .., i]).mapv_inplace(|x| {
            if x > 0.99 {
                f32::INFINITY
            } else {
                x * ratios[i]
            }
        });
    }
    let wp = decide_whitepoint(dest.view()).recip();
    for i in 0..c {
        dest.slice_mut(s![.., .., i])
            .mapv_inplace(|x| (x * wp).clamp(0.0, 1.0));
    }

    Ok(())
}

#[typetag::serde]
impl Dataset for BeyondRgb {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let root_path = ctx.resolve_to_path(&self.root)?;
        let list_path = root_path.join(format!("{}_dataset_paper_git.txt", self.split));
        let list = fs::read_to_string(&list_path).path_context(&list_path)?;
        let parse = Regex::new(r"^(clb/[A-Z]+_[a-z]+|outdoor)(_[\d-]+)?/(\w+)$").unwrap();
        for line in list.trim().split_whitespace() {
            let Some(parsed) = parse.captures(line) else {
                continue;
            };
            let dir_str = format!(
                "{}/{}",
                parsed.get(1).unwrap().as_str(),
                parsed.get(3).unwrap().as_str()
            );
            let dir_path = ctx.resolve_to_path(&self.root)?.join(&dir_str);
            if !dir_path.exists() {
                eprintln!(
                    "expected beyondrgb image directory at {}",
                    dir_path.display()
                );
                continue;
            }
            self.found.push(dir_path);
        }
        self.base.check_count(self.found.len())?;
        Ok(())
    }

    fn count(&self) -> usize {
        self.found.len()
    }

    fn get(
        &self,
        rows: &mut Rows,
        _rng: &mut StdRng, // rng is unused now, but keep for signature consistency
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let dir = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;

        let wt_perm = open_ms_image(&dir.join("WT/MIS.h5"))?;
        let mut nt_perm = open_ms_image(&dir.join("NT/MIS.h5"))?;
        adjust_whitepoint_from_cc(
            &wt_perm,
            &mut nt_perm,
            &dir.join("WT/MIS_cc_detection.json"),
            4.0,
        )?;

        let mut nt = Array3::zeros(nt_perm.dim());
        for (i, j) in [9, 11, 13, 15, 8, 10, 12, 14, 1, 3, 5, 7, 0, 2, 4, 6]
            .into_iter()
            .enumerate()
        {
            nt.slice_mut(s![.., .., j])
                .assign(&nt_perm.slice(s![.., .., i]));
        }

        for [r, g, b] in self.groups.iter().copied() {
            let mut rgb = stack![
                Axis(2),
                nt.slice(s![.., .., r]),
                nt.slice(s![.., .., g]),
                nt.slice(s![.., .., b]),
            ];
            apply_gamma(rgb.view_mut(), 2.2f32.recip());
            rows.image(&format!("spectrum_{r:x}{g:x}{b:x}"), rgb);
        }

        let mut rgb = stack![
            Axis(2),
            nt.slice(s![.., .., 9]),
            nt.slice(s![.., .., 5]),
            nt.slice(s![.., .., 2]),
        ];
        apply_gamma(rgb.view_mut(), 2.2f32.recip());
        rows.image("image", rgb);

        /*
        let wt = open_hdf5_image3(&dir.join("WT/samsung.h5"), "samsung")?;
        let mut nt = open_hdf5_image3(&dir.join("NT/samsung.h5"), "samsung")?;
        adjust_whitepoint_from_cc(&wt, &mut nt, &dir.join("WT/samsung_cc_detection.json"), 1.0)?;
        apply_gamma(nt.view_mut(), 2.2f32.recip());
        rows.image("samsung", nt);
        */

        // TODO: Previous call was process_images(rows, 0.0, rng);
        // This forced a specific crop/offset. Current resize_images uses random offsets.
        self.base.resize_images(rows, _rng, ctx)?;
        rows.name(
            dir.file_name()
                .ok_or_else(|| Error::other("directory url has no filename"))?
                .to_string_lossy(),
        );

        Ok(())
    }
}
