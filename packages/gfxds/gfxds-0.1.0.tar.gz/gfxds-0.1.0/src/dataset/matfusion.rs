use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{
    apply_gamma, auto_dequantize, auto_dequantize_centered, inverse_shading_specular, open_image,
};
use crate::Error;
use crate::{rast, ErrorKind};
use cgmath::{vec3, InnerSpace};
use derivative::Derivative;
use ndarray::{concatenate, s, Array3, Axis};
use rand::rngs::StdRng;
use rand::Rng;
use rand_distr::Distribution;
use std::ffi::OsStr;
use std::fs;
use url::Url;

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct MatfusionBase {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<String>,
    pub gamma_on_disk: bool,
}

pub struct MatfusionBaseData {
    pub diffuse: Array3<f32>,
    pub specular: Array3<f32>,
    pub roughness: Array3<f32>,
    pub normals: Array3<f32>,
    pub caption: Option<String>,
}

#[typetag::serde]
impl Dataset for MatfusionBase {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        if dir.join("diffuse").exists()
            && dir.join("specular").exists()
            && dir.join("roughness").exists()
            && dir.join("normals").exists()
        {
            let diffuse_dir = dir.join("diffuse");
            for texture in diffuse_dir.read_dir().path_context(&diffuse_dir)? {
                let texture = texture?.path();
                let Some(name) = texture.file_name().and_then(OsStr::to_str) else {
                    continue;
                };
                let Some(name) = name.strip_suffix("_diffuse.png") else {
                    continue;
                };
                self.found.push(name.to_string());
            }
        } else {
            for subdir in dir.read_dir().path_context(&dir)? {
                let subdir = subdir?;
                if !subdir.file_type()?.is_dir() {
                    continue;
                }
                let Some(name) = subdir.file_name().to_str().map(|s| s.to_string()) else {
                    continue;
                };
                self.found.push(name);
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
        let name = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;

        let MatfusionBaseData {
            diffuse,
            specular,
            roughness,
            normals,
            caption,
        } = self.load_svbrdf(ctx, name, rng)?;

        rows.image("diffuse", diffuse);
        rows.image("specular", specular);
        rows.image("roughness", roughness);
        rows.image("normals", normals);
        self.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization
        if let Some(text) = caption {
            rows.caption(text);
        }

        Ok(())
    }
}

impl MatfusionBase {
    pub fn load_svbrdf(
        &self,
        ctx: &DatasetContext,
        name: &str,
        rng: &mut impl Rng,
    ) -> Result<MatfusionBaseData, Error> {
        let mut diffuse;
        let mut specular;
        let mut roughness;
        let mut normals;

        let base = ctx.resolve_to_path(&self.dir)?;

        // load textures
        if base.join(format!("{name}.png")).exists() {
            todo!()
        } else if base
            .join("diffuse")
            .join(format!("{name}_diffuse.png"))
            .exists()
        {
            diffuse = open_image(&base.join("diffuse").join(format!("{name}_diffuse.png")))?;
            specular = open_image(&base.join("specular").join(format!("{name}_specular.png")))?;
            roughness = open_image(&base.join("roughness").join(format!("{name}_roughness.png")))?;
            normals = open_image(&base.join("normals").join(format!("{name}_normals.png")))?;
        } else {
            diffuse = open_image(&base.join(name).join("diffuse.png"))?;
            specular = open_image(&base.join(name).join("specular.png"))?;
            roughness = open_image(&base.join(name).join("roughness.png"))?;
            normals = open_image(&base.join(name).join("normals.png"))?;
        }

        let gamma_to_apply = match self.gamma_on_disk {
            false => 2.2f32.recip(),
            true => 1.0,
        };
        auto_dequantize(rng, diffuse.view_mut());
        apply_gamma(diffuse.view_mut(), gamma_to_apply);
        auto_dequantize(rng, diffuse.view_mut());
        apply_gamma(specular.view_mut(), gamma_to_apply);
        auto_dequantize(rng, roughness.view_mut());
        auto_dequantize_centered(rng, normals.view_mut());

        let caption_path = base.join("caption").join(format!("{name}_caption.txt"));
        let caption = match fs::read_to_string(&caption_path) {
            Ok(text) => Some(text.trim().to_string()),
            Err(err) if err.kind() == std::io::ErrorKind::NotFound => None,
            Err(err) => return Err(err).path_context(&caption_path), // Add context here
        };

        for mut n in normals.lanes_mut(Axis(2)) {
            let nv = vec3(n[0], n[1], n[2]);
            let nv = nv.map(|x| x * 2.0 - 1.0);
            let nv = nv.normalize();
            let nv = nv.map(|x| x * 0.5 + 0.5);
            n[0] = nv.x;
            n[1] = nv.y;
            n[2] = nv.z;
        }

        Ok(MatfusionBaseData {
            diffuse,
            specular,
            roughness,
            normals,
            caption,
        })
    }
}

#[derive(serde::Deserialize, serde::Serialize, Debug)]
pub struct MatfusionRasterized {
    #[serde(flatten)]
    pub base: MatfusionBase,
    pub fixed_fov: Option<f32>,
    #[serde(default)]
    pub rasterizer: rast::Options,
}

#[typetag::serde]
impl Dataset for MatfusionRasterized {
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

        let MatfusionBaseData {
            diffuse,
            specular,
            roughness,
            normals,
            caption,
        } = self.base.load_svbrdf(ctx, name, rng)?;

        // the view/flash distance
        let distance = match self.fixed_fov {
            Some(fov) => (fov.to_radians() / 2.).tan().recip(),
            None => rand_distr::Gamma::new(2.0, 2.0).unwrap().sample(rng),
        };

        // rasterize
        let svbrdf = concatenate(
            Axis(2),
            &[
                diffuse.view(),
                specular.view(),
                roughness.slice(s![.., .., ..1]),
                normals.view(),
            ],
        )?;
        let (height, width, _) = svbrdf.dim();
        let mut renderfull = Array3::<f32>::zeros([height, width, 6]);
        rast::render_colocated(
            svbrdf.view(),
            renderfull.view_mut(),
            distance,
            distance,
            &self.rasterizer,
        );
        let render = renderfull.slice(s![.., .., 0..3]).to_owned();
        let halfway = renderfull.slice(s![.., .., 3..6]).to_owned();

        let (inverseshading, albedo) =
            inverse_shading_specular(render.view(), diffuse.view(), specular.view(), false);

        rows.image("diffuse", diffuse);
        rows.image("specular", specular);
        rows.image("roughness", roughness);
        rows.image("normals", normals);
        rows.image("albedo", albedo);
        rows.image("inverseshading", inverseshading);
        rows.image("image", render);
        rows.image("halfway", halfway);
        self.base.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization
        if let Some(text) = caption {
            rows.caption(text);
        }
        Ok(())
    }
}
