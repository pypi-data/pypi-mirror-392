use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{auto_dequantize, inverse_shading, open_image};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use rand::rngs::StdRng;
use url::Url;

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct CGIntrinsics {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub normalize_depth: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<(String, String)>,
}

#[typetag::serde]
impl Dataset for CGIntrinsics {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        let images_dir = dir.join("images");
        for d in images_dir.read_dir().path_context(&dir)? {
            let d = d?;
            if !d.file_type()?.is_dir() {
                continue;
            }
            let scene_path = d.path(); // Get path before moving d
            let scene = d.file_name().into_string().unwrap();
            for d in scene_path.read_dir().path_context(&scene_path)? {
                let d = d?;
                let name = d.file_name().into_string().unwrap();
                let Some(name) = name.strip_suffix("_mlt.png") else {
                    continue;
                };
                self.found.push((scene.clone(), name.to_owned()));
            }
        }
        self.found.sort();
        Ok(())
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let dir = ctx.resolve_to_path(&self.dir)?;
        let (scene, name) = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let base = dir.join("images").join(scene);

        let mut render = open_image(&base.join(format!("{name}_mlt.png")))?;
        auto_dequantize(rng, render.view_mut());
        let mut albedo = open_image(&base.join(format!("{name}_mlt_albedo.png")))?;
        auto_dequantize(rng, albedo.view_mut());
        let mask = open_image(&base.join(format!("{name}_mlt_mask.png")))?;

        let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), false);

        rows.image("image", render);
        rows.image("albedo", albedo);
        rows.image("inverseshading", inverseshading);
        rows.image("weight", mask);
        rows.name(format!("cgintrinsics_{scene}_{name}"));
        Ok(())
    }

    fn count(&self) -> usize {
        self.found.len()
    }
}
