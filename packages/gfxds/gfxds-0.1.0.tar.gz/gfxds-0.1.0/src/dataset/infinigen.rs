use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{apply_gamma, auto_dequantize, open_image};
use crate::{Error, ErrorKind};
use anyhow::anyhow;
use cgmath::{vec3, Matrix, Matrix3, SquareMatrix};
use derivative::Derivative;
use ndarray::{s, stack, Array2, Array3, Axis};
use ndarray_npy::{read_npy, NpzReader};
use rand::rngs::StdRng;
use std::fs;
use url::Url;

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct Infinigen {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub normalize_depth: bool,
    pub worldspace_normals_on_disk: bool,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<(String, String)>,
}

#[typetag::serde]
impl Dataset for Infinigen {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir = ctx.resolve_to_path(&self.dir)?;
        for d in dir.read_dir().path_context(&dir)? {
            let d = d?;
            if !d.file_type()?.is_dir() {
                continue;
            }
            let scene = d.file_name().into_string().unwrap();
            let frames_path = d.path().join("frames").join("Image").join("camera_0");
            if !frames_path.exists() {
                continue;
            }
            for d in frames_path.read_dir().path_context(&frames_path)? {
                let d = d?;
                let name = d.file_name().into_string().unwrap();
                let Some(name) = name.strip_prefix("Image_") else {
                    continue;
                };
                let Some(name) = name.strip_suffix(".png") else {
                    continue;
                };
                self.found.push((scene.clone(), name.to_owned()));
            }
        }
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
        let (scene, name) = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let base = ctx.resolve_to_path(&self.dir)?.join(scene).join("frames");

        let mut render = open_image(
            &base
                .join("Image")
                .join("camera_0")
                .join(format!("Image_{name}.png")),
        )?;
        auto_dequantize(rng, render.view_mut());
        let normals_path = base
            .join("SurfaceNormal")
            .join("camera_0")
            .join(format!("SurfaceNormal_{name}.npy"));
        let mut normals =
            match read_npy::<_, Array3<f32>>(&normals_path).path_context(&normals_path) {
                Ok(n) => n,
                Err(_) => read_npy::<_, Array3<f64>>(&normals_path)
                    .path_context(&normals_path)?
                    .mapv(|f| f as f32),
            };
        let mut diffuse = open_image(
            &base
                .join("DiffCol")
                .join("camera_0")
                .join(format!("DiffCol_{name}.png")),
        )?;
        auto_dequantize(rng, diffuse.view_mut());
        let mut diffuse_direct = open_image(
            &base
                .join("DiffDir")
                .join("camera_0")
                .join(format!("DiffDir_{name}.png")),
        )?;
        auto_dequantize(rng, diffuse_direct.view_mut());
        apply_gamma(diffuse_direct.view_mut(), 2.2);
        let mut diffuse_indirect = open_image(
            &base
                .join("DiffInd")
                .join("camera_0")
                .join(format!("DiffInd_{name}.png")),
        )?;
        auto_dequantize(rng, diffuse_indirect.view_mut());
        apply_gamma(diffuse_indirect.view_mut(), 2.2);
        // TODO: GlosCol is specular F_0 + fresnel lightening
        let mut specular_direct = open_image(
            &base
                .join("GlossDir")
                .join("camera_0")
                .join(format!("GlossDir_{name}.png")),
        )?;
        auto_dequantize(rng, specular_direct.view_mut());
        apply_gamma(specular_direct.view_mut(), 2.2);
        let mut specular_indirect = open_image(
            &base
                .join("GlossInd")
                .join("camera_0")
                .join(format!("GlossInd_{name}.png")),
        )?;
        auto_dequantize(rng, specular_indirect.view_mut());
        apply_gamma(specular_indirect.view_mut(), 2.2);
        let depth_path = base
            .join("Depth")
            .join("camera_0")
            .join(format!("Depth_{name}.npy"));
        let mut depth: Array2<f32> = read_npy(&depth_path).path_context(&depth_path)?;

        // sometimes infinigen has double-resoultion depth
        if depth.dim().0 == 2 * render.dim().0 && depth.dim().1 == 2 * render.dim().1 {
            let mut halfdepth = Array2::zeros((render.dim().0, render.dim().1));
            for i in 0..render.dim().0 {
                for j in 0..render.dim().1 {
                    halfdepth[(i, j)] = (depth[(2 * i, 2 * j)]
                        + depth[(2 * i + 1, 2 * j)]
                        + depth[(2 * i + 1, 2 * j + 1)]
                        + depth[(2 * i, 2 * j + 1)])
                        / 4.0;
                }
            }
            depth = halfdepth;
        }

        let camview_path = base
            .join("camview")
            .join("camera_0")
            .join(format!("camview_{name}.npz"));
        let mut camview =
            NpzReader::new(fs::File::open(&camview_path).path_context(&camview_path)?)
                .path_context(&camview_path)?;

        // Camera view matrix
        let t: Array2<f64> = camview.by_name("T")?;
        let t = t.mapv(|f| f as f32);
        // negation is to undo the infinigen transform at
        // https://github.com/princeton-vl/infinigen/blob/59a2574f3d6a2ab321f3e50573dddecd31b15095/infinigen/core/placement/camera.py#L832
        // in order to get back the original blender transform
        #[rustfmt::skip]
        let t = Matrix3::new(
            t[(0, 0)], -t[(0, 1)], -t[(0, 2)],
            t[(1, 0)], -t[(1, 1)], -t[(1, 2)],
            t[(2, 0)], -t[(2, 1)], -t[(2, 2)],
        ).transpose();
        let rot = t
            .invert()
            .ok_or(anyhow!("view matrix should always be invertable"))?;

        // Camera projection matrix
        let k: Array2<f64> = camview.by_name("K")?;
        let k = k.mapv(|f| f as f32);
        #[rustfmt::skip]
        let k = Matrix3::new(
            k[(0, 0)], k[(0, 1)], k[(0, 2)],
            k[(1, 0)], k[(1, 1)], k[(1, 2)],
            k[(2, 0)], k[(2, 1)], k[(2, 2)],
        ).transpose();
        let proj = k
            .invert()
            .ok_or(anyhow!("projection matrix should always be invertable"))?;

        if self.worldspace_normals_on_disk {
            for i in 0..normals.dim().0 {
                for j in 0..normals.dim().1 {
                    // negation and permutation is to undo the infinigen transform at
                    // https://github.com/princeton-vl/infinigen/blob/59a2574f3d6a2ab321f3e50573dddecd31b15095/infinigen/core/rendering/post_render.py#L54
                    // in order to get back the original blender normal
                    // this isn't the exact inverse because infinigen was also compensating for cv2
                    let normal = vec3(-normals[(i, j, 0)], normals[(i, j, 2)], normals[(i, j, 1)]);
                    let normal = rot * normal;
                    normals[(i, j, 0)] = normal.x;
                    normals[(i, j, 1)] = normal.y;
                    normals[(i, j, 2)] = normal.z;
                }
            }
        }
        // infinigen may have unreliable normals, check if a normal is facing the camera and flip if it is not
        for i in 0..normals.dim().0 {
            for j in 0..normals.dim().1 {
                let p = proj * vec3(j as f32, i as f32, 1.0);
                let x = p.x;
                let y = -p.y;
                let z = -1.0;
                let normal = normals.slice_mut(s![i, j, ..]);
                if normal[0] * x + normal[1] * y + normal[2] * z > 0.0 {
                    for v in normal {
                        *v *= -1.0;
                    }
                }
            }
        }
        let normals = normals.mapv(|f| f * 0.5 + 0.5);

        let mut diffuse_shading = diffuse_direct + diffuse_indirect;
        //diffuse_shading *= 0.5;
        let mut specular_shading = specular_direct + specular_indirect;
        //diffuse_shading *= 0.5;

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

        let weight = diffuse_shading.map_axis(Axis(2), |d| {
            let l = 1.0 / 256.0 + f32::EPSILON;
            match d[0] < l && d[1] < l && d[2] < l {
                true => 0.0,
                false => 1.0,
            }
        });
        let weight = stack![Axis(2), weight, weight, weight];
        let mut depth = stack![Axis(2), depth, depth, depth];

        auto_dequantize(rng, depth.view_mut());

        diffuse_shading.mapv_inplace(|x| x.clamp(0.0, 1.0));
        apply_gamma(diffuse_shading.view_mut(), 1.0 / 2.2);
        specular_shading.mapv_inplace(|x| x.clamp(0.0, 1.0));
        apply_gamma(specular_shading.view_mut(), 1.0 / 2.2);

        // segmentation stuff
        /*
        let mut instances = NpzReader::new(File::open(
            &base
                .join("ObjectSegmentation")
                .join("camera_0")
                .join(format!("ObjectSegmentation_{name}.npz")),
        )?)?;
        let instances: Array1<u8> = instances.by_name("indices")?;
        let instances = instances
            .into_shape((render.dim().0, render.dim().1))
            .unwrap();
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
        */

        rows.image("diffuse", diffuse);
        rows.image("diffuseshading", diffuse_shading);
        rows.image("specularshading", specular_shading);
        rows.image("normals", normals);
        rows.image("image", render);
        rows.image("depth", depth);
        rows.image("weight", weight);
        rows.name(format!("infinigen_{scene}_{name}"));

        //rows.image("instancecolors", instance_colors);
        self.base.resize_images(rows, rng, ctx)?; // TODO: before normalization and dequantization
        Ok(())
    }
}
