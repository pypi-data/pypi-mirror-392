use crate::error::{Error, ResultExt}; // Import custom Error and ResultExt
use image::{DynamicImage, ImageBuffer, Rgb, Rgb32FImage, RgbImage};
use ndarray::{concatenate, Array3, ArrayView3, ArrayViewMut3, Axis};
use rand::Rng;
use std::io::{self, Read, Take};
use std::path::Path;

pub fn array2rgbf(arr: Array3<f32>) -> Rgb32FImage {
    let mut arr = arr.as_standard_layout().to_owned();
    if arr.dim().2 == 1 {
        arr = concatenate(Axis(2), &[arr.view(), arr.view(), arr.view()])
            .unwrap()
            .as_standard_layout()
            .to_owned();
    }
    let shape = arr.dim();
    assert_eq!(shape.2, 3, "must have 3 channels");
    Rgb32FImage::from_raw(shape.1 as u32, shape.0 as u32, arr.into_raw_vec())
        .expect("could not create image object")
}

pub fn array2rgb8(mut arr: Array3<f32>) -> RgbImage {
    arr.mapv_inplace(|x| match x.is_nan() {
        false => x.clamp(0.0, 1.0),
        true => 0.0,
    });
    DynamicImage::ImageRgb32F(array2rgbf(arr)).into_rgb8()
}

pub fn array2rgb16(mut arr: Array3<f32>) -> ImageBuffer<Rgb<u16>, Vec<u16>> {
    arr.mapv_inplace(|x| match x.is_nan() {
        false => x.clamp(0.0, 1.0),
        true => 0.0,
    });
    DynamicImage::ImageRgb32F(array2rgbf(arr)).into_rgb16()
}

pub fn image2array(img: DynamicImage) -> Result<Array3<f32>, Error> {
    let img = img.into_rgb32f();
    Ok(Array3::from_shape_vec(
        [img.height() as usize, img.width() as usize, 3],
        img.into_raw(),
    )?)
}

pub fn open_image(path: &Path) -> Result<Array3<f32>, Error> {
    let img = image::open(path).path_context(path)?;
    image2array(img).path_context(path)
}

pub fn open_image_u16(path: &Path) -> Result<Array3<u16>, Error> {
    let img = image::open(path).path_context(path)?;
    let img = img.into_rgb16();
    Ok::<_, Error>(Array3::from_shape_vec(
        [img.height() as usize, img.width() as usize, 3],
        img.into_raw(),
    )?)
    .path_context(path)
}

pub fn apply_gamma(mut arr: ArrayViewMut3<f32>, gamma: f32) {
    for x in arr.iter_mut() {
        *x = (*x).powf(gamma);
    }
}

const MAX_DEQUANTIZE_RANGE: f32 = 1.0 / 100.0;

fn dequantize_range(arr: impl Iterator<Item = f32>) -> f32 {
    let mut seq: Vec<f32> = arr.collect();
    seq.retain(|x| x.is_finite());
    seq.sort_unstable_by(|a, b| a.partial_cmp(b).unwrap().reverse());
    seq.dedup_by(|a, b| (*a - *b).abs() < f32::EPSILON);
    if seq.is_empty() {
        return 0.0;
    }
    for i in 0..(seq.len() - 1) {
        seq[i] -= seq[i + 1];
    }
    seq.pop();
    if seq.len() <= 4 {
        return 1.0 / 255.0; // default dequantization
    }
    seq.sort_unstable_by(|a, b| a.partial_cmp(b).unwrap());
    let range = 2.0 * seq[3 * seq.len() / 4];
    let range = range.min(MAX_DEQUANTIZE_RANGE);
    range
}

pub fn auto_dequantize(rng: &mut impl Rng, mut arr: ArrayViewMut3<f32>) -> f32 {
    let range = dequantize_range(arr.view().iter().copied());
    arr.mapv_inplace(|x| x / (1.0 + range) + rng.gen::<f32>() * range);
    range
}

pub fn auto_dequantize_centered(rng: &mut impl Rng, mut arr: ArrayViewMut3<f32>) {
    let halfrange = dequantize_range(arr.view().iter().copied()) / 2.0;
    arr.mapv_inplace(|x| x + rng.gen_range(-halfrange..=halfrange));
}

pub fn decide_whitepoint(image: ArrayView3<f32>) -> f32 {
    let mut vec: Vec<f32> = image.iter().copied().filter(|x| x.is_finite()).collect();
    vec.sort_by(|a, b| a.partial_cmp(b).unwrap());
    vec[(vec.len() - 1) * 95 / 100] * 1.2
}

pub fn inverse_shading_specular(
    render: ArrayView3<f32>,
    diffuse: ArrayView3<f32>,
    specular: ArrayView3<f32>,
    albedo_gamma: bool,
) -> (Array3<f32>, Array3<f32>) {
    let mut albedo_d = diffuse.to_owned();
    apply_gamma(albedo_d.view_mut(), 2.2);
    let mut albedo_s = specular.to_owned();
    apply_gamma(albedo_s.view_mut(), 2.2);
    let albedo = albedo_d + albedo_s;
    inverse_shading(render, albedo.view(), albedo_gamma)
}

pub fn inverse_shading(
    render: ArrayView3<f32>,
    albedo: ArrayView3<f32>,
    albedo_gamma: bool,
) -> (Array3<f32>, Array3<f32>) {
    let mut linrender = render.to_owned();
    apply_gamma(linrender.view_mut(), 2.2);

    let mut linalbedo = albedo.to_owned();
    if albedo_gamma {
        apply_gamma(linalbedo.view_mut(), 2.2);
    }
    /*
    let scale = linrender.mean().unwrap_or(1.0) / albedo.mean().unwrap_or(1.0);
    let scale = scale.min(
        1.0 / albedo
            .iter()
            .copied()
            .max_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(1.0),
    );
    let albedo = albedo.mapv(|x| x * scale);
    */

    let mut inverseshading = linrender.clone() / (linalbedo.clone() + &linrender);

    /*
    for i in 0..inverseshading.dim().0 {
        for j in 0..inverseshading.dim().1 {
            let saturated = linrender.slice(s![i, j, ..]).iter().any(|x| *x == 1.0)
                || linalbedo.slice(s![i, j, ..]).iter().any(|x| *x == 1.0);
            if saturated {
                let mut d = inverseshading.slice_mut(s![i, j, ..]);
                let d0 = *d.iter().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap();
                d.fill(d0);
            }
        }
    }
    */

    inverseshading.mapv_inplace(|x| x.clamp(0.0, 1.0));
    apply_gamma(inverseshading.view_mut(), 1.0 / 2.2);
    apply_gamma(linalbedo.view_mut(), 1.0 / 2.2);
    let albedo = linalbedo.mapv(|x| x.clamp(0.0, 1.0));
    (inverseshading, albedo)
}

pub struct LimitedReader<R: Read> {
    inner: Take<R>,
    limit: u64,
}

impl<R: Read> LimitedReader<R> {
    pub fn new(reader: R, limit: u64) -> Self {
        LimitedReader {
            inner: reader.take(limit),
            limit,
        }
    }
}

impl<R: Read> Read for LimitedReader<R> {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        let bytes_read = self.inner.read(buf)?;
        if self.inner.limit() == 0 && bytes_read > 0 {
            Err(io::Error::new(
                io::ErrorKind::PermissionDenied,
                format!("Read limit of {} bytes exceeded", self.limit),
            ))
        } else {
            Ok(bytes_read)
        }
    }
}
