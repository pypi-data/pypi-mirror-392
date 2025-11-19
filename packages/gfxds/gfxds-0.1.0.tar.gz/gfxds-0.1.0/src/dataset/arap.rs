use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{auto_dequantize, inverse_shading, open_image};
use crate::{Error, ErrorKind};
use anyhow::anyhow;
use derivative::Derivative;
use rand::rngs::StdRng;
use url::Url;

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct Arap {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<(String, String)>,
}

#[typetag::serde]
impl Dataset for Arap {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        for d in dir.read_dir().path_context(&dir)? {
            let d = d?;
            if !d.file_type()?.is_dir() {
                continue;
            }
            let scene_path = d.path(); // Get path before moving d
            let scene = d.file_name().into_string().unwrap();
            for d in scene_path.read_dir().path_context(&scene_path)? {
                let d = d?;
                let name = d.file_name().into_string().unwrap();
                if name.contains("albedo") {
                    continue;
                }
                self.found.push((scene.clone(), name.to_owned()));
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

        let splitname = name.split(&['.', '_']).collect::<Vec<_>>();
        let (shortname, albedo_name) = match splitname.as_slice() {
            [name, ext] => (name.to_string(), format!("{name}_albedo.{ext}")),
            [name, light, ext] => (format!("{name}_{light}"), format!("{name}_albedo.{ext}")),
            _ => return Err(anyhow!("{name} is not expected").into()),
        };
        let base_path = ctx.resolve_to_path(&self.dir)?;
        let base = base_path.join(scene);

        let mut render = open_image(&base.join(name))?;
        auto_dequantize(rng, render.view_mut());
        let mut albedo = open_image(&base.join(albedo_name))?;
        auto_dequantize(rng, albedo.view_mut());
        let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), true);
        rows.image("image", render);
        rows.image("albedo", albedo);
        rows.image("inverseshading", inverseshading);
        rows.name(format!("{shortname}_{scene}"));
        // TODO: Previous call was process_images_careful(rows, 0.0, vec2(0.5, 0.5), vec2(0.0, 0.0));
        // This forced a specific crop/offset. Current resize_images uses random offsets.
        self.base.resize_images(rows, rng, ctx)?;
        Ok(())
    }
}
