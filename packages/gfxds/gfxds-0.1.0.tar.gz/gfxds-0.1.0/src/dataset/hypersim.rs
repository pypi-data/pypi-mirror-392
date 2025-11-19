use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{apply_gamma, auto_dequantize, auto_dequantize_centered, decide_whitepoint};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use ndarray::{s, stack, Array2, Array3, Axis};
use palette::{Hsv, IntoColor, RgbHue, Srgb};
use rand::rngs::StdRng;
use rand::Rng;
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use url::Url;

#[cfg(feature = "hdf5")]
fn open_hdf5_image3(path: impl AsRef<Path>) -> Result<Array3<f32>, Error> {
    use hdf5::File;
    let path_ref = path.as_ref();
    let f = File::open(path_ref).path_context(path_ref)?;
    let d = f.dataset("dataset")?;
    Ok(d.read()?)
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_image3(_: impl AsRef<Path>) -> Result<Array3<f32>, Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

#[cfg(feature = "hdf5")]
fn open_hdf5_image2(path: impl AsRef<Path>) -> Result<Array2<f32>, Error> {
    use hdf5::File;
    let path_ref = path.as_ref();
    let f = File::open(path_ref).path_context(path_ref)?;
    let d = f.dataset("dataset")?;
    Ok(d.read()?)
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_image2(_: impl AsRef<Path>) -> Result<Array2<f32>, Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

#[cfg(feature = "hdf5")]
fn open_hdf5_image2i(path: impl AsRef<Path>) -> Result<Array2<i32>, Error> {
    use hdf5::File;
    let path_ref = path.as_ref();
    let f = File::open(path_ref).path_context(path_ref)?;
    let d = f.dataset("dataset")?;
    Ok(d.read()?)
}

#[cfg(not(feature = "hdf5"))]
fn open_hdf5_image2i(_: impl AsRef<Path>) -> Result<Array2<i32>, Error> {
    Err(ErrorKind::NotCompiledWithFeature("hdf5").into())
}

fn deseralize_cap_bool<'de, D: serde::Deserializer<'de>>(d: D) -> Result<bool, D::Error> {
    let s: &str = serde::Deserialize::deserialize(d)?;
    match s {
        "False" => Ok(false),
        "True" => Ok(true),
        _ => Err(serde::de::Error::custom("bool is not True or False")),
    }
}

#[derive(Debug, serde::Deserialize, PartialEq, Eq)]
pub struct MetadataRow {
    scene_name: String,
    camera_name: String,
    frame_id: usize,
    #[serde(deserialize_with = "deseralize_cap_bool")]
    included_in_public_release: bool,
    split_partition_name: String,
}

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct Hypersim {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub split: String,
    pub normalize_depth: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<MetadataRow>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub scenes: HashMap<String, Vec<usize>>,
}

impl Hypersim {
    fn sort_found(&mut self) {
        self.found.sort_by(|a, b| {
            a.scene_name
                .cmp(&b.scene_name)
                .then(a.camera_name.cmp(&b.camera_name))
                .then(a.frame_id.cmp(&b.frame_id))
        });
    }
}

#[typetag::serde]
impl Dataset for Hypersim {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        let meta_path = dir.join("metadata_images_split_scene_v1.csv");
        let mut meta_reader =
            csv::Reader::from_reader(fs::File::open(&meta_path).path_context(&meta_path)?);
        for row in meta_reader.deserialize() {
            let row: MetadataRow = row?;
            if row.split_partition_name != self.split {
                continue;
            }
            if !row.included_in_public_release {
                continue;
            }
            self.found.push(row);
        }

        self.sort_found();
        self.found.dedup();

        for (i, r) in self.found.iter().enumerate() {
            self.scenes.entry(r.scene_name.clone()).or_default().push(i);
        }
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
        let dir = ctx.resolve_to_path(&self.dir)?;
        let row = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;

        let scene = &row.scene_name;
        let cam = &row.camera_name;
        let frame = row.frame_id;
        let base_camera = dir.join(scene).join("_detail").join(cam);
        let base_final = dir
            .join(scene)
            .join("images")
            .join(format!("scene_{cam}_final_hdf5"));
        let base_geo = dir
            .join(scene)
            .join("images")
            .join(format!("scene_{cam}_geometry_hdf5"));

        let camera_position = open_hdf5_image2(base_camera.join("camera_keyframe_positions.hdf5"))?
            .slice_move(s![frame, ..]);

        let mut render = open_hdf5_image3(base_final.join(format!("frame.{frame:04}.color.hdf5")))?;
        let whitepoint = decide_whitepoint(render.view());
        render.mapv_inplace(|x| x / whitepoint);
        auto_dequantize(rng, render.view_mut());
        let mut diffuse = open_hdf5_image3(
            base_final.join(format!("frame.{frame:04}.diffuse_reflectance.hdf5")),
        )?;
        auto_dequantize(rng, diffuse.view_mut());
        let mut diffuse_shading = open_hdf5_image3(
            base_final.join(format!("frame.{frame:04}.diffuse_illumination.hdf5")),
        )?;
        diffuse_shading.mapv_inplace(|x| x / whitepoint);
        auto_dequantize(rng, diffuse_shading.view_mut());
        let mut residual =
            open_hdf5_image3(base_final.join(format!("frame.{frame:04}.residual.hdf5")))?;
        residual.mapv_inplace(|x| x / whitepoint);
        auto_dequantize(rng, residual.view_mut());
        let mut depth =
            open_hdf5_image2(base_geo.join(format!("frame.{frame:04}.depth_meters.hdf5")))?;
        let mut normals =
            open_hdf5_image3(base_geo.join(format!("frame.{frame:04}.normal_cam.hdf5")))?;
        let normals_world =
            open_hdf5_image3(base_geo.join(format!("frame.{frame:04}.normal_world.hdf5")))?;
        let position = open_hdf5_image3(base_geo.join(format!("frame.{frame:04}.position.hdf5")))?;

        if self.normalize_depth {
            let maxdepth = depth
                .iter()
                .copied()
                .filter(|d| *d < 1000.0)
                .max_by(|a, b| a.partial_cmp(b).unwrap())
                .unwrap_or(1000.0)
                .max(0.01);
            depth.mapv_inplace(|d| {
                if d == 0.0 || d > maxdepth || !d.is_finite() {
                    1.0
                } else {
                    d / maxdepth
                }
            });
        }

        let mut depth = stack![Axis(2), depth, depth, depth];

        let weight = normals.map_axis(Axis(2), |d| match d.iter().all(|x| x.is_finite()) {
            true => 1.0,
            false => 0.0,
        });
        let weight = stack![Axis(2), weight, weight, weight];

        // hypersim has unreliable normals, check if a normal is facing the camera and flip if it is not
        let view_vector = position.clone() - camera_position;
        for i in 0..normals.dim().0 {
            for j in 0..normals.dim().1 {
                let world_view = view_vector.slice(s![i, j, ..]);
                let world_normal = normals_world.slice(s![i, j, ..]);
                if world_view.dot(&world_normal) > 0.0 {
                    let normal = normals.slice_mut(s![i, j, ..]);
                    for v in normal {
                        *v *= -1.0;
                    }
                }
            }
        }

        normals.mapv_inplace(|x| if x.is_finite() { x * 0.5 + 0.5 } else { 0.5 });

        auto_dequantize(rng, depth.view_mut());
        auto_dequantize_centered(rng, normals.view_mut());

        render.mapv_inplace(|x| x.clamp(0.0, 1.0));
        apply_gamma(render.view_mut(), 1.0 / 2.2);
        diffuse_shading.mapv_inplace(|x| x.clamp(0.0, 1.0));
        apply_gamma(diffuse_shading.view_mut(), 1.0 / 2.2);
        residual.mapv_inplace(|x| x.clamp(0.0, 1.0));
        apply_gamma(residual.view_mut(), 1.0 / 2.2);

        // segmentation stuff
        let instances =
            open_hdf5_image2i(base_geo.join(format!("frame.{frame:04}.semantic_instance.hdf5")))?;
        let mut instance_color_map = HashMap::new();
        let mut instance_colors = Array3::zeros((instances.dim().0, instances.dim().1, 3));
        for i in 0..instances.dim().0 {
            for j in 0..instances.dim().1 {
                let rgb: Srgb = *instance_color_map
                    .entry(instances[(i, j)])
                    .or_insert_with(|| {
                        Hsv::new_srgb(
                            RgbHue::from_degrees(rng.gen_range(0.0..360.0)),
                            rng.gen_range(0.5..1.0),
                            rng.gen(),
                        )
                        .into_color()
                    });
                instance_colors[(i, j, 0)] = rgb.red;
                instance_colors[(i, j, 1)] = rgb.green;
                instance_colors[(i, j, 2)] = rgb.blue;
            }
        }

        rows.image("image", render);
        rows.image("diffuse", diffuse);
        rows.image("diffuseshading", diffuse_shading);
        rows.image("residual", residual);
        rows.image("depth", depth);
        rows.image("weight", weight);
        rows.image("instancecolors", instance_colors);
        rows.image("normals", normals);
        rows.image("position", position);
        self.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization
        rows.name(format!("hypersim_{scene}_{cam}_{frame}"));

        Ok(())
    }

    fn weights(&self) -> Option<Vec<f64>> {
        let mut counts = HashMap::<_, usize>::new();
        for row in &self.found {
            let count = counts.entry(row.scene_name.clone()).or_default();
            *count += 1;
        }
        Some(
            self.found
                .iter()
                .map(|row| 1.0 / counts[&row.scene_name] as f64)
                .collect(),
        )
    }
}
