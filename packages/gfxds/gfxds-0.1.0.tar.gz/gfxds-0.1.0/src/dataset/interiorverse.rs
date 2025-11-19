use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{
    apply_gamma, auto_dequantize, auto_dequantize_centered, decide_whitepoint, inverse_shading,
    open_image,
};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use ndarray::{s, stack, Array2, Axis};
use rand::rngs::StdRng;
use std::collections::HashMap;
use url::Url;

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct Interiorverse {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub split: String,
    pub fov: f32,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<(String, String)>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub scenes: HashMap<String, Vec<usize>>,
}

#[typetag::serde]
impl Dataset for Interiorverse {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        let list_path = dir.join(format!("{}.txt", self.split));
        let list_contents = std::fs::read_to_string(&list_path).path_context(&list_path)?;

        for scene in list_contents.split_whitespace() {
            let scene_path = dir.join(scene);
            for d in scene_path.read_dir().path_context(&scene_path)? {
                let d = d?;
                let name = d.file_name().into_string().unwrap();
                let Some(name) = name.strip_suffix("_im.exr") else {
                    continue;
                };
                self.found.push((scene.to_owned(), name.to_owned()));
            }
        }

        self.found.sort();
        self.found.dedup();
        self.base.check_count(self.found.len())?;

        for (i, (scene, _)) in self.found.iter().enumerate() {
            self.scenes.entry(scene.clone()).or_default().push(i);
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
        let (scene, name) = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let base = ctx.resolve_to_path(&self.dir)?.join(scene);
        let fov = self.fov;

        let mut render = open_image(&base.join(format!("{name}_im.exr")))?;
        let mut normals = open_image(&base.join(format!("{name}_normal.exr")))?;
        let material = open_image(&base.join(format!("{name}_material.exr")))?;
        let mut albedo = open_image(&base.join(format!("{name}_albedo.exr")))?;
        let depth = open_image(&base.join(format!("{name}_depth.exr")))?;

        let whitepoint = decide_whitepoint(render.view());
        render.mapv_inplace(|x| x / whitepoint);

        let roughness = material.slice(s![.., .., 0]);
        let mut roughness = stack![Axis(2), roughness, roughness, roughness];
        let metallic = material.slice(s![.., .., 1]);
        let metallic = stack![Axis(2), metallic, metallic, metallic];

        auto_dequantize(rng, roughness.view_mut());
        auto_dequantize(rng, albedo.view_mut());
        auto_dequantize(rng, render.view_mut());

        let specular_base = (1.0 - metallic.clone()) * 0.04;
        let albedo_base = albedo.clone() - &specular_base;
        let mut diffuse = (1.0 - metallic.clone()) * &albedo_base;
        apply_gamma(diffuse.view_mut(), 1.0 / 2.2);
        let mut specular = metallic.clone() * &albedo_base + &specular_base;
        apply_gamma(specular.view_mut(), 1.0 / 2.2);

        apply_gamma(render.view_mut(), 1.0 / 2.2);
        let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), false);
        render.mapv_inplace(|x| x.clamp(0.0, 1.0));

        let mut depth = depth.slice(s![.., .., 0]).to_owned();
        let maxdepth = depth
            .iter()
            .copied()
            .filter(|d| *d < 100_000.0)
            .max_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(100_000.0)
            .max(0.01);
        depth.mapv_inplace(|d| {
            if d == 0.0 || d > maxdepth || !d.is_finite() {
                1.0
            } else {
                d / maxdepth
            }
        });
        let mut depth = stack![Axis(2), depth, depth, depth];

        let mut weight = Array2::<f32>::zeros((normals.dim().0, normals.dim().1));
        for i in 0..normals.dim().0 {
            for j in 0..normals.dim().1 {
                let normal = normals.slice_mut(s![i, j, ..]);
                if normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2] > 0.1 {
                    weight[(i, j)] = 1.0;
                }
            }
        }
        let weight = stack![Axis(2), weight, weight, weight];

        auto_dequantize_centered(rng, normals.view_mut());

        // interiorverse may have unreliable normals, check if a normal is facing the camera and flip if it is not
        let projection = (fov / 2.0).to_radians().tan();
        for i in 0..normals.dim().0 {
            for j in 0..normals.dim().1 {
                let h = normals.dim().0 as f32;
                let w = normals.dim().1 as f32;
                let x = (2.0 * j as f32 - w + 0.5) / w * projection;
                let y = (h - 2.0 * i as f32 - 0.5) / w * projection;
                let z = -1.0;
                let normal = normals.slice_mut(s![i, j, ..]);
                if normal[0] * x + normal[1] * y + normal[2] * z > 0.0 {
                    for v in normal {
                        *v *= -1.0;
                    }
                }
            }
        }

        auto_dequantize(rng, depth.view_mut());
        normals.mapv_inplace(|x| if x.is_finite() { x * 0.5 + 0.5 } else { 0.5 });

        rows.image("image", render);
        rows.image("albedo", albedo);
        rows.image("diffuse", diffuse);
        rows.image("specular", specular);
        rows.image("metalness", metallic);
        rows.image("roughness", roughness);
        rows.image("inverseshading", inverseshading);
        rows.image("normals", normals);
        rows.image("depth", depth);
        rows.image("weight", weight);
        self.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization
        rows.name(format!("interiorverse_{scene}_{name}_{fov:.0}"));

        Ok(())
    }

    fn weights(&self) -> Option<Vec<f64>> {
        let mut counts = HashMap::<_, usize>::new();
        for (scene, _) in &self.found {
            let count = counts.entry(scene.clone()).or_default();
            *count += 1;
        }
        Some(
            self.found
                .iter()
                .map(|(scene, _)| 1.0 / counts[scene] as f64)
                .collect(),
        )
    }
}
