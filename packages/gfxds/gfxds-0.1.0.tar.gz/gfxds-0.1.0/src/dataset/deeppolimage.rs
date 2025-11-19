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
pub struct DeepPolImage {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    scenes: Vec<String>,
}

#[typetag::serde]
impl Dataset for DeepPolImage {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.scenes.clear();
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        for d in dir_path.read_dir().path_context(&dir_path)? {
            let d = d?;
            let name = d.file_name().into_string().unwrap();
            self.scenes.push(name);
        }
        self.scenes.sort();
        self.base.check_count(self.scenes.len())?;
        Ok(())
    }

    fn count(&self) -> usize {
        self.scenes.len()
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let scene = self.scenes.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let base = ctx.resolve_to_path(&self.dir)?.join(scene);

        // swap aronud to match cromo
        let mut pol_0 = open_image(&base.join("IV.png"))?;
        let mut pol_90 = open_image(&base.join("IH.png"))?;
        let mut pol_45 = open_image(&base.join("I135.png"))?;
        let mut pol_135 = open_image(&base.join("I45.png"))?;
        for pol in [&mut pol_0, &mut pol_90, &mut pol_45, &mut pol_135] {
            auto_dequantize(rng, pol.view_mut());
        }

        let stokes_0 = (pol_0.clone() + &pol_45 + &pol_90 + &pol_135) / 4.0;
        let stokes_1 = pol_0 - pol_90;
        let stokes_2 = pol_45 - pol_135;
        let stokes_all = stack![Axis(3), stokes_0, stokes_1, stokes_2];

        let rgb = stokes_all.slice(s![.., .., .., 0]).to_owned();
        let stokes = stokes_all.mean_axis(Axis(2)).unwrap();

        let mut diffuse = open_image(&base.join("diffuse_map.png"))?;
        auto_dequantize(rng, diffuse.view_mut());
        let mut specular = open_image(&base.join("specular_map.png"))?;
        auto_dequantize(rng, specular.view_mut());
        let mut roughness = open_image(&base.join("roughness_map.png"))?;
        auto_dequantize(rng, roughness.view_mut());
        let mut normals = open_image(&base.join("normal_map.png"))?;
        let weight = normals.map_axis(Axis(2), |d| {
            match d[0] == 0.0 && d[1] == 0.0 && d[2] == 0.0 {
                true => 0.0,
                false => 1.0,
            }
        });
        auto_dequantize(rng, normals.view_mut());
        let weight = stack![Axis(2), weight, weight, weight];

        rows.image("image", rgb);
        rows.image("diffuse", diffuse);
        rows.image("specular", specular);
        rows.image("roughness", roughness);
        rows.image("normals", normals);
        rows.image("weight", weight);
        rows.image("stokespolarization", stokes);
        rows.name(scene);

        // process images before converting to HSV because the stokes
        // vector interpolates better
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
                    // also amplify to visually match cromo? TODO: investigate this
                    (3.0 * dolp).tanh(),
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
