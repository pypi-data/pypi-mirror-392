use crate::warp::{self, CropInfo};
use crate::{Error, ErrorKind};
use cgmath::vec2;
use ndarray::{s, Array3};
use rand::rngs::StdRng;
use rand::Rng;
use serde::de::Error as _;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::path::PathBuf;
use toml::Value;
use url::Url;

mod arap;
mod beyondrgb;
mod cgintrinsics;
mod cromo;
mod deeppolimage;
mod hypersim;
mod imagefolder;
mod infinigen;
mod interiorverse;
mod matfusion;
mod matfusiongi;
mod mid;
mod ntire;
mod nyudepth;
mod pbrjumble;
mod pixelprose;

#[derive(Debug, Clone)]
pub struct ImageRow {
    pub image: Array3<f32>,
    pub crop: Option<CropInfo>,
}

#[derive(Debug, Clone)]
pub enum RelatedIndex {
    OtherViewpoint(usize),
}

#[derive(Debug, Clone, Default)]
pub struct Rows {
    pub dataset_id: String,
    pub name: Option<String>,
    pub caption: Option<String>,
    pub images: HashMap<String, ImageRow>,
    pub related: Vec<RelatedIndex>,
}

impl Rows {
    pub fn image(&mut self, component: impl Into<String>, image: Array3<f32>) {
        self.images
            .insert(component.into(), ImageRow { image, crop: None });
    }

    pub fn caption(&mut self, caption: impl Into<String>) {
        self.caption = Some(caption.into());
    }

    pub fn name(&mut self, name: impl Into<String>) {
        self.name = Some(name.into());
    }

    pub fn other_viewpoint(&mut self, index: usize) {
        self.related.push(RelatedIndex::OtherViewpoint(index))
    }

    pub fn get_image(&self, component: &str) -> &Array3<f32> {
        &self
            .images
            .get(component)
            .unwrap_or_else(|| panic!("Image '{component}' not found in sample {:?}", self.name))
            .image
    }

    pub fn get_image_mut(&mut self, component: &str) -> &mut Array3<f32> {
        &mut self
            .images
            .get_mut(component)
            .unwrap_or_else(|| panic!("Image '{component}' not found in sample {:?}", self.name))
            .image
    }
}

fn default_crop() -> f32 {
    0.0
}

fn default_resize_using_crop() -> f32 {
    0.0
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(deny_unknown_fields)]
pub struct DatasetBase {
    #[serde(default = "default_crop")]
    pub center_crop: f32,
    #[serde(default = "default_resize_using_crop")]
    pub resize_using_crop: f32,
    pub resize: Option<(usize, usize)>,
    pub expected_count: Option<usize>,
}

impl DatasetBase {
    pub fn check_count(&self, actual: usize) -> Result<(), Error> {
        if let Some(expected) = self.expected_count {
            if expected != actual {
                return Err(ErrorKind::ExpectedCount {
                    expected,
                    found: actual,
                }
                .into());
            }
        }
        Ok(())
    }

    pub fn resize_images(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
    ) -> Result<(), Error> {
        let offsetx: f32 = rng.gen();
        let offsety: f32 = rng.gen();
        for row in &mut rows.images.values_mut() {
            let (source_height, source_width, chan) = row.image.dim();
            if self.center_crop > 0.0 {
                let margin_r = (source_height as f32 * self.center_crop * 0.5).round() as usize;
                let margin_c = (source_width as f32 * self.center_crop * 0.5).round() as usize; // Use width for horizontal margin
                if source_height > 2 * margin_r && source_width > 2 * margin_c {
                    row.image = row
                        .image
                        .slice(s![
                            margin_r..source_height - margin_r,
                            margin_c..source_width - margin_c,
                            ..
                        ])
                        .to_owned();
                } else {
                    // Handle cases where crop is too large
                    eprintln!(
                        "Warning: Center crop ({}) too large for image dimensions ({}x{}). Skipping crop.",
                        self.center_crop, source_height, source_width
                    );
                }
            }
            if let Some((height, width)) = ctx.resize_override.or(self.resize) {
                // Check if image is already the target size
                if row.image.dim().0 == height && row.image.dim().1 == width {
                    row.crop = Some(CropInfo {
                        source_h: source_height as f32, // Original height before potential crop
                        source_w: source_width as f32,  // Original width before potential crop
                        offset_y: 0.0, // Assuming no offset if already correct size
                        offset_x: 0.0, // Assuming no offset if already correct size
                    });
                    continue;
                }

                let mut dest = Array3::zeros([height, width, chan]);
                let cinfo = warp::resize_and_crop(
                    row.image.view(),
                    dest.view_mut(),
                    self.resize_using_crop,
                    vec2(offsetx, offsety),
                );
                row.image = dest;
                row.crop = Some(cinfo);
            } else {
                // If no resize is specified, still record original dimensions in crop info
                row.crop = Some(CropInfo {
                    source_h: source_height as f32,
                    source_w: source_width as f32,
                    offset_y: 0.0, // Assuming no offset if not resizing
                    offset_x: 0.0, // Assuming no offset if not resizing
                });
            }
        }
        Ok(())
    }
}

pub struct DatasetContext {
    pub root: PathBuf,
    pub config: HashMap<String, Value>,
    pub resize_override: Option<(usize, usize)>,
}

impl DatasetContext {
    pub fn resolve_to_path(&self, url: &Url) -> Result<PathBuf, Error> {
        match url.scheme() {
            "datasets" => Ok(self
                .root
                .join(url.path().strip_prefix('/').unwrap_or(url.path()))),
            _ => Err(ErrorKind::ResolvingUrlToPath(url.clone()).into()),
        }
    }

    pub fn dataset_from_config(&self, config: Value) -> Result<Box<dyn Dataset>, Error> {
        match config {
            Value::Array(_) => Ok(Box::new(Multi {
                datasets: config.try_into()?,
                cumsum: Default::default(),
            })),
            Value::Table(mut map) => {
                let mut inherits = Vec::new();
                while let Some(inherit) = map.remove("inherit") {
                    match inherit {
                        Value::String(s) => inherits.push(s),
                        Value::Array(a) => {
                            for v in a {
                                inherits.push(v.try_into()?);
                            }
                        }
                        _ => {
                            return Err(toml::de::Error::custom(
                                "expected inherit to be string or array of strings",
                            )
                            .into())
                        }
                    }
                }
                // Apply inherits in reverse order so earlier ones override later ones
                for inherit in inherits.into_iter().rev() {
                    let Value::Table(other_map) = self
                        .config
                        .get(&inherit)
                        .ok_or_else(|| ErrorKind::UnknownDataset(inherit.clone()))?
                        .clone()
                    else {
                        return Err(toml::de::Error::custom(format!(
                            "expected table for inherited config {inherit:?}"
                        ))
                        .into());
                    };
                    for (key, value) in other_map {
                        if let toml::map::Entry::Vacant(entry) = map.entry(key) {
                            entry.insert(value);
                        }
                    }
                }
                return Ok(map.try_into()?);
            }
            _ => Err(
                toml::de::Error::custom("expected a table or array but found {config:?}").into(),
            ),
        }
    }

    pub fn dataset_from_id(&self, id: &str) -> Result<Box<dyn Dataset>, Error> {
        self.dataset_from_config(
            self.config
                .get(id)
                .ok_or_else(|| ErrorKind::UnknownDataset(id.to_string()))?
                .clone(),
        )
    }

    pub fn default_config_toml() -> &'static str {
        include_str!("../../datasets.toml")
    }

    pub fn default_config() -> HashMap<String, Value> {
        toml::from_str(DatasetContext::default_config_toml()).unwrap()
    }
}

impl Default for DatasetContext {
    fn default() -> Self {
        DatasetContext {
            root: PathBuf::from("."),
            config: Self::default_config(),
            resize_override: None,
        }
    }
}

#[test]
fn datasets_toml_is_valid() {
    let ctx = DatasetContext::default();
    for id in ctx.config.keys() {
        ctx.dataset_from_id(id)
            .unwrap_or_else(|e| panic!("deserializing {id}: {e}"));
    }
}

#[typetag::serde(tag = "kind")]
pub trait Dataset: Sync + Send + fmt::Debug {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error>;

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error>;

    fn count(&self) -> usize;

    fn weights(&self) -> Option<Vec<f64>> {
        None
    }
}

fn default_weight() -> f64 {
    1.0
}

#[derive(Deserialize, Serialize, Debug)]
pub struct SubDataset {
    pub id: String,
    #[serde(default = "default_weight")]
    pub weight: f64,
    pub dataset: Option<Box<dyn Dataset>>,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct Multi {
    pub datasets: Vec<SubDataset>,
    #[serde(skip)]
    pub cumsum: Vec<usize>,
}

#[typetag::serde]
impl Dataset for Multi {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.cumsum.clear();
        let mut sum = 0;
        for sub in &mut self.datasets {
            let instance = match &mut sub.dataset {
                None => sub.dataset.get_or_insert(ctx.dataset_from_id(&sub.id)?),
                Some(instance) => instance,
            };
            instance.start(ctx)?;
            self.cumsum.push(sum);
            sum += instance.count();
        }
        self.cumsum.push(sum);
        Ok(())
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let dataset_idx = match self.cumsum.binary_search(&index) {
            Ok(i) => i,
            Err(i) => i - 1,
        };
        let base_idx = self.cumsum[dataset_idx];
        let sub_idx = index - base_idx;
        let dataset = self
            .datasets
            .get(dataset_idx)
            .ok_or(ErrorKind::IllegalIndex)?;
        rows.dataset_id = dataset.id.clone(); // Set the dataset ID on the rows
        dataset
            .dataset
            .as_ref()
            .expect("not started")
            .get(rows, rng, ctx, sub_idx)?;
        for r in &mut rows.related {
            match r {
                RelatedIndex::OtherViewpoint(idx) => *idx += base_idx,
            }
        }
        Ok(())
    }

    fn count(&self) -> usize {
        *self.cumsum.last().unwrap()
    }

    fn weights(&self) -> Option<Vec<f64>> {
        let total_count = self.count();
        if total_count == 0 {
            return Some(vec![]);
        }
        let mut weight = vec![1.0; total_count];
        for (dataset, base_idx) in self.datasets.iter().zip(self.cumsum.iter().copied()) {
            let instance = dataset.dataset.as_ref().expect("not started");
            let instance_count = instance.count();
            if instance_count == 0 {
                continue;
            }
            let mult = dataset.weight * total_count as f64 / instance_count as f64;
            for sub_idx in 0..instance_count {
                weight[base_idx + sub_idx] *= mult;
            }
            if let Some(sub_weights) = instance.weights() {
                let mean: f64 = sub_weights.iter().sum::<f64>() / sub_weights.len() as f64;
                for (sub_idx, sub_weight) in sub_weights.iter().copied().enumerate() {
                    weight[base_idx + sub_idx] *= sub_weight / mean;
                }
            }
        }
        Some(weight)
    }
}
