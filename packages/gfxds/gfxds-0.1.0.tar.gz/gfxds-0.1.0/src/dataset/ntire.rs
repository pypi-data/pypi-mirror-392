use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{apply_gamma, auto_dequantize, open_image};
use crate::{Error, ErrorKind};
use anyhow::anyhow;
use derivative::Derivative;
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use rand::Rng;
use std::cmp::Ordering;
use std::fmt;
use url::Url;

#[derive(Debug, PartialOrd, Ord, PartialEq, Eq, Clone)]
struct Entry {
    image: String,
    tempurature: String,
    direction: String,
}

impl fmt::Display for Entry {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let Entry {
            image,
            tempurature,
            direction,
        } = self;
        write!(f, "{image}_{tempurature}_{direction}.png")
    }
}

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct Ntire {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url, // For train: dir of images. For val: dir containing input/ and guide/
    pub gt_dir: Option<Url>, // Only used if is_train is false
    pub is_train: bool,
    pub apply_gamma: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    found_by_image: Vec<Entry>, // Only used if is_train is true
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    found_by_lighting: Vec<Entry>, // Only used if is_train is true
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    val_count: usize, // Only used if is_train is false
}

impl Ntire {
    fn matching_image(&self, image: &str) -> &[Entry] {
        let Err(start_index) = self
            .found_by_image
            .binary_search_by(|x| x.image.as_str().cmp(image).then(Ordering::Greater))
        else {
            unreachable!()
        };
        let Err(end_index) = self
            .found_by_image
            .binary_search_by(|x| x.image.as_str().cmp(image).then(Ordering::Less))
        else {
            unreachable!()
        };
        &self.found_by_image[start_index..end_index]
    }

    fn matching_lighting(&self, tempurature: &str, direction: &str) -> &[Entry] {
        let Err(start_index) = self.found_by_lighting.binary_search_by(|x| {
            (x.tempurature.as_str(), x.direction.as_str())
                .cmp(&(tempurature, direction))
                .then(Ordering::Greater)
        }) else {
            unreachable!()
        };
        let Err(end_index) = self.found_by_lighting.binary_search_by(|x| {
            (x.tempurature.as_str(), x.direction.as_str())
                .cmp(&(tempurature, direction))
                .then(Ordering::Less)
        }) else {
            unreachable!()
        };
        &self.found_by_lighting[start_index..end_index]
    }
}

#[typetag::serde]
impl Dataset for Ntire {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        if self.is_train {
            let mut found = Vec::new();
            for dir_entry in dir_path.read_dir().path_context(&dir_path)? {
                let dir_entry = dir_entry?;
                if !dir_entry.file_type()?.is_file() {
                    continue;
                }
                let Some(name) = dir_entry.file_name().to_str().map(str::to_owned) else {
                    continue;
                };
                let Some(name) = name.strip_suffix(".png") else {
                    continue;
                };
                let Some((image, name)) = name.split_once("_") else {
                    continue;
                };
                let Some((tempurature, direction)) = name.split_once("_") else {
                    continue;
                };
                found.push(Entry {
                    image: image.to_owned(),
                    tempurature: tempurature.to_owned(),
                    direction: direction.to_owned(),
                });
            }
            self.found_by_image = found.clone();
            self.found_by_lighting = found;
            self.found_by_image.sort_by(|a, b| a.image.cmp(&b.image));
            self.found_by_lighting.sort_by(|a, b| {
                (&a.tempurature, &a.direction).cmp(&(&b.tempurature, &b.direction))
            });
            self.base.check_count(self.found_by_image.len())?;
        } else {
            // Validation set - count files in input/
            let input_dir = dir_path.join("input");
            self.val_count = input_dir
                .read_dir()
                .path_context(&input_dir)?
                .filter_map(Result::ok)
                .filter(|e| e.path().is_file() && e.path().extension() == Some("png".as_ref()))
                .count();
            self.base.check_count(self.val_count)?;
            if self.gt_dir.is_none() {
                return Err(anyhow!("gt_dir must be set for non-train Ntire dataset").into());
            }
        }
        Ok(())
    }

    fn count(&self) -> usize {
        if self.is_train {
            self.found_by_image.len()
        } else {
            self.val_count
        }
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        let crop;

        if self.is_train {
            let entry = self
                .found_by_image
                .get(index)
                .ok_or(ErrorKind::IllegalIndex)?;
            let other_lighting = self.matching_image(&entry.image).choose(rng).unwrap();
            let other_image = self
                .matching_lighting(&other_lighting.tempurature, &other_lighting.direction)
                .choose(rng)
                .unwrap();

            rows.image("image", open_image(&dir_path.join(&entry.to_string()))?);
            rows.image(
                "relightingguide",
                open_image(&dir_path.join(&other_image.to_string()))?,
            );
            rows.image(
                "relighting",
                open_image(&dir_path.join(&other_lighting.to_string()))?,
            );
            rows.name(format!(
                "{}_{}_{}",
                entry.image, entry.tempurature, entry.direction
            ));
            crop = rng.gen_range(0.0..0.2);
        } else {
            if index >= self.val_count {
                return Err(ErrorKind::IllegalIndex.into());
            }
            let gt_dir_path = ctx.resolve_to_path(self.gt_dir.as_ref().unwrap())?;
            let name = format!("Pair{index:03}.png");

            rows.image("image", open_image(&dir_path.join("input").join(&name))?);
            rows.image(
                "relightingguide",
                open_image(&dir_path.join("guide").join(&name))?,
            );
            rows.image("relighting", open_image(&gt_dir_path.join(&name))?);
            rows.name(format!("pair{index:03}"));
            crop = 0.0;
        }

        for row in rows.images.values_mut() {
            auto_dequantize(rng, row.image.view_mut());
            if self.apply_gamma {
                apply_gamma(row.image.view_mut(), 1.0 / 2.2);
            }
        }

        // TODO: Previous call was process_images(rows, crop, rng);
        // This used a specific crop value. Current resize_images uses self.base.resize_using_crop.
        // We need a way to pass the dynamic `crop` value calculated above.
        // For now, using the base config value, which might be incorrect for training.
        let _ = crop;
        self.base.resize_images(rows, rng, ctx)?;
        Ok(())
    }
}
