use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{auto_dequantize, open_image};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use ndarray::{s, stack, Array3, Axis};
use palette::rgb::Rgb;
use palette::{Hsv, IntoColor, RgbHue};
use rand::rngs::StdRng;
use url::Url;

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct Cromo {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub scenes: Vec<Url>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    frames: Vec<(usize, String, String)>,
}

#[typetag::serde]
impl Dataset for Cromo {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.frames.clear();
        for (scene_index, scene_url) in self.scenes.iter().enumerate() {
            let scene_path = ctx.resolve_to_path(scene_url)?;
            for sequence_entry in scene_path.read_dir().path_context(&scene_path)? {
                let sequence_entry = sequence_entry?;
                let sequence_name = sequence_entry.file_name().into_string().unwrap();
                let png_dir = sequence_entry.path().join("rgb").join("left").join("data");
                for png_entry in png_dir.read_dir().path_context(&png_dir)? {
                    let png_entry = png_entry?;
                    let png_name = png_entry.file_name().into_string().unwrap();
                    let Some(frame_name) = png_name.strip_suffix(".png") else {
                        continue;
                    };
                    self.frames
                        .push((scene_index, sequence_name.clone(), frame_name.to_owned()));
                }
            }
        }
        self.frames.sort();
        self.base.check_count(self.frames.len())?;
        Ok(())
    }

    fn count(&self) -> usize {
        self.frames.len()
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let (scene_idx, sequence, frame) = self.frames.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let scene_path = ctx.resolve_to_path(&self.scenes[*scene_idx])?;

        let mut rgb = open_image(
            &scene_path
                .join(sequence)
                .join("rgb")
                .join("left")
                .join("data")
                .join(format!("{frame}.png")),
        )?;
        auto_dequantize(rng, rgb.view_mut());

        let mut polarized = open_image(
            &scene_path
                .join(sequence)
                .join("polarized")
                .join("left")
                .join("data")
                .join(format!("{frame}.png")),
        )?;
        auto_dequantize(rng, polarized.view_mut());
        let polarized = polarized.mean_axis(Axis(2)).unwrap();
        let h = polarized.dim().0 / 4;
        let pol_0 = polarized.slice(s![0 * h..1 * h, ..]);
        let pol_45 = polarized.slice(s![1 * h..2 * h, ..]);
        let pol_90 = polarized.slice(s![2 * h..3 * h, ..]);
        let pol_135 = polarized.slice(s![3 * h..4 * h, ..]);

        let stokes_0 = (pol_0.to_owned() + pol_45 + pol_90 + pol_135) / 4.0;
        let stokes_1 = pol_0.to_owned() - pol_90;
        let stokes_2 = pol_45.to_owned() - pol_135;
        let stokes = stack![Axis(2), stokes_0, stokes_1, stokes_2];

        // process images before converting to HSV because the stokes
        // vector interpolates better
        rows.image("image", rgb);
        rows.image("stokespolarization", stokes);
        rows.name(format!("{scene_idx}_{sequence}_{frame}"));
        // TODO: Previous call was process_images(rows, rng.gen_range(0.0..0.5), rng);
        // This used a random crop value. Current resize_images uses self.base.resize_using_crop.
        self.base.resize_images(rows, rng, ctx)?;
        let stokes = rows.get_image("stokespolarization").clone(); // Clone because rows is borrowed mutably

        // technically the angle is half this, but we'll leave it because
        // we'd double it anyway when converting to HSV
        let mut pol_rgb = Array3::<f32>::zeros(stokes.dim());
        for i in 0..stokes.dim().0 {
            for j in 0..stokes.dim().1 {
                let s = stokes.slice(s![i, j, ..]);
                let dolp = (s[1] * s[1] + s[2] * s[2]).sqrt() / s[0].max(0.01);
                // this really 2x the angle of polarization since s1 and s2 are 45 degrees offset
                // but it is perfect for colormapping, since the hue should wrap around at 180 degrees
                let aolp2 = s[2].atan2(s[1]);
                let hsv = Hsv::new(
                    RgbHue::from_radians(aolp2),
                    // apply a sigmoid curve to degree to get it between 0 and 1
                    dolp.tanh(),
                    1.0,
                );
                let rgb: Rgb = hsv.into_color();
                pol_rgb[(i, j, 0)] = rgb.red;
                pol_rgb[(i, j, 1)] = rgb.green;
                pol_rgb[(i, j, 2)] = rgb.blue;
            }
        }
        rows.image("hsvpolarization", pol_rgb);

        Ok(())
    }
}
