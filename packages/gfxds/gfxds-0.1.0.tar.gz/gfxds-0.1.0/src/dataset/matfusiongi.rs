use super::matfusion::{MatfusionBase, MatfusionBaseData};
use super::{Dataset, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{apply_gamma, decide_whitepoint, inverse_shading, open_image};
use crate::warp::transform_normal_map;
use crate::{rast, warp, Error, ErrorKind};
use cgmath::Vector2;
use ndarray::{s, Array3};
use rand::rngs::StdRng;
use rand::seq::IteratorRandom as _;
use rand::Rng;
use std::collections::HashMap;
use std::fs::File;
use std::path::{Path, PathBuf};
use url::Url;

#[derive(serde::Serialize, serde::Deserialize, Debug)]
pub enum LightingMode {
    Flash,
    Env,
    FlashNoFlash,
}

impl LightingMode {
    pub fn flash_weights(&self, rng: &mut impl Rng) -> (f32, Option<f32>) {
        use LightingMode::*;
        match self {
            Flash => (1.0, None),
            Env => (0.0, None),
            FlashNoFlash => (0.0, Some(rng.gen_range(0.02f32.ln()..1.5f32.ln()).exp())),
        }
    }
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
pub struct MatfusionGi {
    #[serde(flatten)]
    pub base: MatfusionBase,
    pub renders: Url,
    pub lighting: LightingMode,
}

impl MatfusionGi {
    pub fn form_render(
        &self,
        root: &Path,
        id: &str,
        rng: &mut impl Rng,
        rows: &mut Rows,
    ) -> Result<(), Error> {
        let (flash, other_flash) = self.lighting.flash_weights(rng);

        // Load metadata.
        let meta_path = root.join(format!("{id}.json"));
        let meta: RenderMeta =
            serde_json::from_reader(File::open(&meta_path).path_context(&meta_path)?)
                .path_context(&meta_path)?; // Add context to the reader result as well
        let which = *meta
            .views
            .keys()
            .choose(rng)
            .ok_or(ErrorKind::EmptyDataset)?;

        // Functions to load renders.
        let mut env_whitepoint = None;
        let mut env = |which: char| -> Result<_, Error> {
            let mut env = open_image(&root.join(format!("{id}_{which}_envio_0000.exr")))?;
            let whitepoint = *env_whitepoint.get_or_insert_with(|| decide_whitepoint(env.view()));
            env.mapv_inplace(|x| x / whitepoint);
            Ok(env)
        };
        let mut fla_whitepoint = None;
        let mut fla = |which: char| -> Result<_, Error> {
            let mut fla = open_image(&root.join(format!("{id}_{which}_flash_0000.exr")))?;
            let whitepoint = *fla_whitepoint.get_or_insert_with(|| decide_whitepoint(fla.view()));
            fla.mapv_inplace(|x| x / whitepoint);
            Ok(fla)
        };

        // Create the initial image and UV map.
        let mut image = match flash {
            _ if flash <= 0.0 => env(which)?,
            _ if flash >= 1.0 => fla(which)?,
            _ => (1.0 - flash) * env(which)? + flash * fla(which)?,
        };
        let uvs = open_image(&root.join(format!("{id}_{which}_position_0000.exr")))?;

        let urange = uvs.slice(s![.., .., 0]).std(0.0);
        let vrange = uvs.slice(s![.., .., 1]).std(0.0);
        if urange < 0.5 || vrange < 0.5 {
            return Err(ErrorKind::SkipSample.into());
            // bail!("not enough positional variation ({urange}, {vrange}), something is wrong with {}/{}", root.display(), id);
        }

        // Rasterize to create the halfway vector
        if let LightingMode::Flash | LightingMode::FlashNoFlash = self.lighting {
            let (height, width, _) = image.dim();
            let mut renderfull = Array3::<f32>::zeros([height, width, 6]);
            rast::render_colocated(
                Array3::zeros([height, width, 10]).view(),
                renderfull.view_mut(),
                meta.flash_distance(which),
                meta.view_distance(which),
                &rast::Options::default(),
            );
            let halfway = renderfull.slice(s![.., .., 3..6]).to_owned();
            rows.image("halfway", halfway);
        }

        // Handle the other image.
        match other_flash {
            Some(other_flash) => {
                // Metadata stuff.
                let other_which = *meta
                    .views
                    .keys()
                    .filter(|this_which| **this_which != which)
                    .choose(rng)
                    .ok_or(ErrorKind::EmptyDataset)?;

                // Create initial image and UVS.
                let other_env = env(other_which)?;
                let other_fla = fla(other_which)?;
                let other_source_image =
                    (1.0 - flash) * other_env + (flash + other_flash) * other_fla;
                let mut other_image = Array3::zeros(image.dim());
                let other_uvs =
                    open_image(&root.join(format!("{id}_{other_which}_position_0000.exr")))?;

                // Align to original image.
                let nearest = warp::NearestBuffer::new(uvs.view(), other_uvs.view());
                warp::reverse_warp(
                    other_source_image.view(),
                    other_image.view_mut(),
                    |pt| nearest.query(pt, 4.0),
                    |_, mut arr| arr.fill(0.0),
                );

                // Final tonemapping stuff.
                let final_whitepoint = decide_whitepoint(other_image.view());
                image.mapv_inplace(|x| (x / final_whitepoint).clamp(0.0, 1.0));
                apply_gamma(image.view_mut(), 2.2f32.recip());
                other_image.mapv_inplace(|x| (x / final_whitepoint).clamp(0.0, 1.0));
                apply_gamma(other_image.view_mut(), 2.2f32.recip());

                rows.image("envrender", image);
                rows.image("image", other_image);
            }
            None => {
                // Final tone mapping stuff.
                image.mapv_inplace(|x| x.clamp(0.0, 1.0));
                apply_gamma(image.view_mut(), 2.2f32.recip());

                rows.image("image", image);
            }
        };

        let mut uvs = uvs;
        uvs.slice_mut(s![.., .., 1]).mapv_inplace(|y| -y);
        uvs.mapv_inplace(|v| v / 2.0 + 0.5);
        rows.image("position", uvs);

        // Result
        Ok(())
    }
}

#[typetag::serde]
impl Dataset for MatfusionGi {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.base.start(ctx)
    }

    fn count(&self) -> usize {
        self.base.count()
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let name = self.base.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let render_base = ctx.resolve_to_path(&self.renders)?;

        let MatfusionBaseData {
            mut diffuse,
            mut specular,
            mut roughness,
            mut normals,
            caption,
        } = self.base.load_svbrdf(ctx, name, rng)?;
        self.form_render(&render_base, name, rng, rows)?;

        let render = rows.get_image("image").clone();
        let mut uvs = rows.get_image("position").clone();
        uvs.slice_mut(s![.., .., 0])
            .mapv_inplace(|x| x * (diffuse.dim().1 - 1) as f32);
        uvs.slice_mut(s![.., .., 1])
            .mapv_inplace(|y| y * (diffuse.dim().0 - 1) as f32);
        let uvs = warp::UvBuffer(uvs.view());

        for x in [&mut diffuse, &mut specular, &mut roughness] {
            let mut dest = Array3::zeros(render.dim());
            warp::reverse_warp(
                x.view(),
                dest.view_mut(),
                |pt| uvs.query(pt),
                |_, mut arr| arr.fill(0.0),
            );
            *x = dest;
        }

        let mut dest = Array3::zeros(render.dim());
        warp::reverse_warp_with_edit(
            normals.view(),
            dest.view_mut(),
            |pt| uvs.query(pt),
            |_, mut arr| arr.fill(0.0),
            transform_normal_map,
        );
        normals = dest;

        let mut albedo_d = diffuse.clone();
        apply_gamma(albedo_d.view_mut(), 2.2);
        let mut albedo_s = specular.clone();
        apply_gamma(albedo_s.view_mut(), 2.2);
        let albedo = albedo_d + albedo_s;
        let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), false);
        rows.image("albedo", albedo);
        rows.image("inverseshading", inverseshading);

        rows.image("diffuse", diffuse);
        rows.image("specular", specular);
        rows.image("roughness", roughness);
        rows.image("normals", normals);
        self.base.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization

        if let Some(text) = caption {
            rows.caption(text);
        }
        rows.name(name);

        Ok(())
    }
}

#[derive(serde::Deserialize, serde::Serialize)]
pub struct BoundsMeta {
    pub x: (f32, f32),
    pub y: (f32, f32),
    pub z: (f32, f32),
}

#[derive(serde::Deserialize, serde::Serialize)]
pub struct ViewMeta {
    pub distance: Option<f32>,
    pub flash_distance: Option<f32>,
    pub flash_offset: Option<Vector2<f32>>,
}

#[derive(serde::Deserialize, serde::Serialize)]
pub struct RenderMeta {
    pub flash_offset: Option<Vector2<f32>>,
    pub distance: Option<f32>,
    pub world: PathBuf,
    pub views: HashMap<char, ViewMeta>,
}

impl RenderMeta {
    pub fn flash_distance(&self, which: char) -> f32 {
        let v = &self.views[&which];
        // unless otherwise specified, the light was colocated with a 1:1 focal length camera
        v.flash_distance
            .or(v.distance)
            .or(self.distance)
            .unwrap_or(2.0)
    }

    pub fn flash_offset(&self, which: char) -> Vector2<f32> {
        let v = &self.views[&which];
        v.flash_offset
            .or(self.flash_offset)
            .unwrap_or(Vector2::new(0.0, 0.0))
    }

    pub fn view_distance(&self, which: char) -> f32 {
        self.views[&which].distance.unwrap_or(2.0)
    }
}
