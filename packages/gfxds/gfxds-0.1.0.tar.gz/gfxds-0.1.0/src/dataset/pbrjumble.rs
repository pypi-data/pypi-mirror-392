use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{
    apply_gamma, auto_dequantize, auto_dequantize_centered, inverse_shading, open_image,
    open_image_u16,
};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use ndarray::Array3;
use palette::{Hsv, IntoColor, RgbHue, Srgb};
use rand::rngs::StdRng;
use rand::Rng;
use std::collections::HashMap;
use url::Url;

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct PbrJumble {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub renders: Url,
    pub normalize_depth: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<String>,
}

#[typetag::serde]
impl Dataset for PbrJumble {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let renders_path = ctx.resolve_to_path(&self.renders)?;
        let mut count = 0;
        for dir in renders_path.read_dir().path_context(&renders_path)? {
            let dir = dir?;
            if !dir.file_type()?.is_dir() {
                continue;
            }
            let Some(name) = dir.file_name().to_str().map(str::to_owned) else {
                continue;
            };
            self.found.push(name);
            count += 1;
        }
        self.base.check_count(count)?; // Use check_count from DatasetBase
        self.found.sort();
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
        let name = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let renders_path = ctx.resolve_to_path(&self.renders)?;
        let base = renders_path.join(name);

        // load textures
        for tex in [
            "diffuse",
            "diffuseshading",
            "specular",
            "specularshading",
            "roughness",
            "normals",
            "depth",
            "image",
        ] {
            let mut img = open_image(&base.join(format!("{tex}0000.png")))?;
            match tex {
                "depth" => (), // dequantize later
                "normals" => auto_dequantize_centered(rng, img.view_mut()),
                _ => {
                    auto_dequantize(rng, img.view_mut());
                }
            }
            rows.image(tex, img);
        }

        let depth = rows.get_image_mut("depth"); // Get mutable ref for in-place ops
        let weight = depth.map(|d| match *d == 1.0 {
            true => 0.0,
            false => 1.0,
        });

        if self.normalize_depth {
            let maxdepth = depth
                .iter()
                .copied()
                .filter(|d| *d < 0.999)
                .max_by(|a, b| a.partial_cmp(b).unwrap())
                .unwrap_or(1.0); // Default to 1.0 if no valid depth found
            if maxdepth > 0.0 {
                depth.mapv_inplace(|d| (d / maxdepth).min(1.0));
            }
        }

        if depth.std(1.0) < 0.2 {
            return Err(ErrorKind::SkipSample.into());
        }

        auto_dequantize(rng, depth.view_mut());

        for i in ["roughness", "diffuseshading", "specularshading"] {
            // make the backgrounds white
            rows.get_image_mut(i)
                .zip_mut_with(&weight, |x, w| *x = *x * w + (1.0 - w));
        }
        rows.image("weight", weight);

        let mut residual_r = rows.get_image("image").clone();
        apply_gamma(residual_r.view_mut(), 2.2);
        let mut residual_d = rows.get_image("diffuse").clone();
        apply_gamma(residual_d.view_mut(), 2.2);
        residual_d += 0.03; // so that rough diffuse objects have 0 residual
        let mut residual_ds = rows.get_image("diffuseshading").clone();
        apply_gamma(residual_ds.view_mut(), 2.2);
        if residual_ds.iter().all(|x| *x != 1.0) {
            let mut residual = residual_r - residual_d * residual_ds;
            residual.mapv_inplace(|x| x.clamp(0.0, 1.0));
            apply_gamma(residual.view_mut(), 1.0 / 2.2);
            rows.image("residual", residual);
        }

        let mut albedo_d = rows.get_image("diffuse").to_owned();
        apply_gamma(albedo_d.view_mut(), 2.2);

        let mut albedo_s = rows.get_image("specular").to_owned();
        apply_gamma(albedo_s.view_mut(), 2.2);
        let albedo = albedo_d + albedo_s;

        let render = rows.get_image("image");
        let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), false);
        rows.image("albedo", albedo);
        rows.image("inverseshading", inverseshading);

        // segmentation stuff
        let instances = open_image_u16(&base.join("object0000.png"))?;
        let mut instance_color_map = HashMap::new();
        let mut instance_colors = Array3::zeros((instances.dim().0, instances.dim().1, 3));
        for i in 0..instances.dim().0 {
            for j in 0..instances.dim().1 {
                let rgb: Srgb = *instance_color_map
                    .entry(instances[(i, j, 0)])
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
        rows.image("instancecolors", instance_colors);
        rows.name(format!("pbrjumble_{name}"));

        // TODO: Previous call was process_images(rows, rng.gen_range(0.0..=0.2), rng);
        // This used a random crop value. Current resize_images uses self.base.resize_using_crop.
        self.base.resize_images(rows, rng, ctx)?;

        Ok(())
    }
}
