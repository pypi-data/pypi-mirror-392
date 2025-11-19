use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{auto_dequantize, inverse_shading, open_image};
use crate::{Error, ErrorKind};
use anyhow::anyhow;
use derivative::Derivative;
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use rand::Rng;
use url::Url;

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct Mid {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub is_train: bool,
    pub input_direction: Option<usize>, // Only used if is_train is false
    pub gt_direction: Option<usize>,    // Only used if is_train is false
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    found: Vec<String>,
}

#[typetag::serde]
impl Dataset for Mid {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        for dir in dir_path.read_dir().path_context(&dir_path)? {
            let dir = dir?;
            if !dir.file_type()?.is_dir() {
                continue;
            }
            let name = dir.file_name().into_string().unwrap();
            self.found.push(name);
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
        let dir_path = ctx.resolve_to_path(&self.dir)?;

        let (image, other_image, input_lighting, output_lighting, _crop) = if self.is_train {
            let image = self.found.choose(rng).ok_or(ErrorKind::IllegalIndex)?;
            let other_image = self.found.choose(rng).ok_or(ErrorKind::IllegalIndex)?;
            let input_lighting = rng.gen_range(0..25);
            let mut output_lighting = rng.gen_range(0..24);
            if output_lighting >= input_lighting {
                output_lighting += 1;
            }
            let crop = rng.gen_range(0.0f32..1.0).powi(2);
            (image, other_image, input_lighting, output_lighting, crop)
        } else {
            let image = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
            let other_image = &self.found[(index + 1) % self.found.len()];
            let input_lighting = self.input_direction.ok_or(ErrorKind::Other(anyhow!(
                "input_direction must be set for non-train Mid dataset"
            )))?;
            let output_lighting = self.gt_direction.ok_or(ErrorKind::Other(anyhow!(
                "gt_direction must be set for non-train Mid dataset"
            )))?;
            (image, other_image, input_lighting, output_lighting, 0.0)
        };

        let render = open_image(
            &dir_path
                .join(image)
                .join(format!("dir_{input_lighting}_mip2.jpg")),
        )?;
        let relightingguide = open_image(
            &dir_path
                .join(other_image)
                .join(format!("dir_{output_lighting}_mip2.jpg")),
        )?;
        let relighting = open_image(
            &dir_path
                .join(image)
                .join(format!("dir_{output_lighting}_mip2.jpg")),
        )?;

        rows.image("image", render);
        rows.image("relightingguide", relightingguide);
        rows.image("relighting", relighting);

        for image in rows.images.values_mut() {
            auto_dequantize(rng, image.image.view_mut());
        }

        let albedo_path = dir_path.join(image).join("albedo.exr");
        if albedo_path.exists() {
            let mut albedo = open_image(&albedo_path)?;
            auto_dequantize(rng, albedo.view_mut());
            let render = rows.get_image("image"); // Get after potential modification by auto_dequantize
            let (inverseshading, albedo) = inverse_shading(render.view(), albedo.view(), false);
            rows.image("albedo", albedo);
            rows.image("inverseshading", inverseshading);
        }

        rows.name(image);
        // TODO: Previous call was process_images(rows, crop, rng);
        // This used a specific crop value. Current resize_images uses self.base.resize_using_crop.
        // We need a way to pass the dynamic `crop` value calculated above.
        // For now, using the base config value, which might be incorrect for training.
        self.base.resize_images(rows, rng, ctx)?;
        Ok(())
    }
}
