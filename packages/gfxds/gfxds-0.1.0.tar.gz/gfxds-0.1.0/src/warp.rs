use cgmath::{vec3, InnerSpace, Matrix2, Point2, SquareMatrix, Vector2, Vector3};
use ndarray::{s, ArrayView1, ArrayView3, ArrayViewMut1, ArrayViewMut3};

#[derive(Debug, Clone, Copy)]
pub struct Query {
    /// The point in the image/SVBRDF we want to sample.
    /// For an SVBRDF this is usually in the range (0-255, 0-255).
    pub point: Point2<f32>,
    /// A matrix that transforms small pertubations in the output pixel location
    /// into pertubations in the `Query.point` coordinate. This is mainly needed
    /// for minification, but is also used to correctly rotate/distort normal maps
    /// and potentially to convert small normals into roughness.
    pub frame: Option<Matrix2<f32>>,
}

impl Query {
    /// Distorting a normal map requires rotating the X,Y coordinates of the normal.
    pub fn transform_normal(&self, mut normal: Vector3<f32>) -> Option<Vector3<f32>> {
        let mut mat = self
            .frame
            .expect("can not warp normal maps without a frame");
        if mat.x.magnitude() <= f32::EPSILON {
            return None;
        }
        mat.x /= mat.x.magnitude();
        if mat.y.magnitude() <= f32::EPSILON {
            return None;
        }
        mat.y /= mat.y.magnitude();
        let mat = mat.invert()?;
        normal.y *= -1.0; // OpenGL-style normals
        normal = (mat * normal.truncate()).extend(normal.z);
        normal.y *= -1.0;
        Some(normal)
    }
}

fn query_extrapolated<'a>(
    src: &'a ArrayView3<f32>,
    y: isize,
    x: isize,
) -> (ArrayView1<'a, f32>, bool) {
    let cy = y.clamp(0, src.dim().0 as isize - 1);
    let cx = x.clamp(0, src.dim().1 as isize - 1);
    let ext = src.slice(s![cy as usize, cx as usize, ..]);
    (ext, cx == x && cy == y)
}

fn query_interpolated(
    src: ArrayView3<f32>,
    mut dest: ArrayViewMut1<f32>,
    point: Point2<f32>,
) -> bool {
    let ty = point.y - point.y.floor();
    let sy = 1.0 - ty;
    let tx = point.x - point.x.floor();
    let sx = 1.0 - tx;

    let (v00, b00) = query_extrapolated(&src, point.y.floor() as isize, point.x.floor() as isize);
    let (v01, b01) = query_extrapolated(&src, point.y.floor() as isize, point.x.ceil() as isize);
    let (v10, b10) = query_extrapolated(&src, point.y.ceil() as isize, point.x.floor() as isize);
    let (v11, b11) = query_extrapolated(&src, point.y.ceil() as isize, point.x.ceil() as isize);

    for k in 0..dest.len() {
        dest[k] += (v00[k] * sy + v10[k] * ty) * sx + (v01[k] * sy + v11[k] * ty) * tx;
    }

    b00 || b01 || b10 || b11
}

pub fn query(
    src: ArrayView3<f32>,
    mut dest: ArrayViewMut1<f32>,
    Query { point, frame }: Query,
) -> bool {
    dest.fill(0.0);

    'minify: {
        let Some(mut frame) = frame else {
            break 'minify;
        };

        let my = frame.y.magnitude();
        if my <= f32::EPSILON {
            break 'minify;
        }
        frame.y /= my;
        let my = my.ceil() as usize;

        let mx = frame.x.magnitude();
        if mx <= f32::EPSILON {
            break 'minify;
        }
        frame.x /= mx;
        let mx = mx.ceil() as usize;

        if mx <= 1 && my <= 1 {
            break 'minify;
        }

        let mut any = false;
        for dy in 0..my {
            for dx in 0..mx {
                let b = query_interpolated(
                    src,
                    dest.view_mut(),
                    point + frame.x * dx as f32 + frame.y * dy as f32,
                );
                any = any || b;
            }
        }
        dest /= (mx * my) as f32;
        return any;
    }

    // if minification was not possible
    query_interpolated(src, dest, point)
}

pub fn transform_normal_map(q: Query, mut pixel: ArrayViewMut1<f32>) {
    assert_eq!(pixel.dim(), 3);
    let normal = vec3(pixel[0], pixel[1], pixel[2]);
    let normal = normal.map(|x| x * 2.0 - 1.0);
    let Some(normal) = q.transform_normal(normal) else {
        return;
    };
    let normal = normal.map(|x| x * 0.5 + 0.5);
    pixel[0] = normal.x;
    pixel[1] = normal.y;
    pixel[2] = normal.z;
}

pub fn reverse_warp_with_edit(
    source: ArrayView3<f32>,
    mut dest: ArrayViewMut3<f32>,
    mut warp: impl FnMut(Point2<usize>) -> Option<Query>,
    mut fill: impl FnMut(Point2<usize>, ArrayViewMut1<f32>),
    mut edit: impl FnMut(Query, ArrayViewMut1<f32>),
) {
    for i in 0..dest.dim().0 {
        for j in 0..dest.dim().1 {
            let p = Point2 { x: j, y: i };
            let mut dest = dest.slice_mut(s![i, j, ..]);
            'load: {
                let Some(q) = warp(p) else {
                    fill(p, dest);
                    break 'load;
                };
                if !query(source, dest.view_mut(), q) {
                    fill(p, dest);
                    break 'load;
                }
                edit(q, dest.view_mut());
            }
        }
    }
}

/// Performs an arbitrary warping of the array `source`, saving the result into
/// `dest`. The `warp` function takes an output coordinate and specifies the
/// corisponding point in `source`, and `fill` provides a background pixel value
/// when `warp` outputs a cordinate outside the defined area of `source`.
pub fn reverse_warp(
    source: ArrayView3<f32>,
    dest: ArrayViewMut3<f32>,
    warp: impl FnMut(Point2<usize>) -> Option<Query>,
    fill: impl FnMut(Point2<usize>, ArrayViewMut1<f32>),
) {
    reverse_warp_with_edit(source, dest, warp, fill, |_, _| ());
}

#[derive(Debug, Clone)]
pub struct CropInfo {
    pub source_w: f32,
    pub source_h: f32,
    pub offset_x: f32,
    pub offset_y: f32,
}

/// Resizes `source` into `dest` with bilinear interpolation or mean-pooling as needed.
pub fn resize_and_crop(
    source: ArrayView3<f32>,
    dest: ArrayViewMut3<f32>,
    crop: f32,
    offset: Vector2<f32>,
) -> CropInfo {
    let (h0, w0, _) = source.dim();
    let (h1, w1, _) = dest.dim();
    let mut h0 = h0 as f32;
    let mut h1 = h1 as f32;
    let mut w0 = w0 as f32;
    let mut w1 = w1 as f32;

    fn shrink_to_aspect(ideal_h: f32, ideal_w: f32, aspect_h: f32, aspect_w: f32) -> (f32, f32) {
        (
            ideal_h.min(ideal_w * aspect_h / aspect_w),
            ideal_w.min(ideal_h * aspect_w / aspect_h),
        )
    }

    let (cut_h_min, cut_w_min) = shrink_to_aspect(h1.min(h0), w1.min(w0), h1, w1);
    let (cut_h_max, cut_w_max) = shrink_to_aspect(h0, w0, h1, w1);

    let mut cut_h = crop * cut_h_min + (1.0 - crop) * cut_h_max;
    let cut_i = (h0 - cut_h) * offset.y;
    let mut cut_w = crop * cut_w_min + (1.0 - crop) * cut_w_max;
    let cut_j = (w0 - cut_w) * offset.x;

    // switch to inclusive coordinates when magnifying, I guess
    // this is so the right/bottom edges don't have to extrapolate
    if h1 > cut_h {
        h0 = (h0 - 1.0).max(1.0);
        h1 = (h1 - 1.0).max(1.0);
        cut_h = (cut_h - 1.0).max(1.0);
    }
    if w1 > cut_w {
        w0 = (w0 - 1.0).max(1.0);
        w1 = (w1 - 1.0).max(1.0);
        cut_w = (cut_w - 1.0).max(1.0);
    }

    let _ = h0;
    let _ = w0;

    let frame = Matrix2::new(cut_h / h1, 0.0, 0.0, cut_w / w1);
    reverse_warp(
        source,
        dest,
        |i| {
            let point = Point2 {
                y: i.y as f32 / h1 * cut_h + cut_i,
                x: i.x as f32 / w1 * cut_w + cut_j,
            };
            Some(Query {
                point,
                frame: Some(frame),
            })
        },
        |_, _| (),
    );

    CropInfo {
        source_h: cut_h,
        source_w: cut_w,
        offset_y: cut_i,
        offset_x: cut_j,
    }
}

/// A UV map.
pub struct UvBuffer<'a>(pub ArrayView3<'a, f32>);

fn least_squares_slope<T: Copy>(ts: &[T], xy: impl Fn(T) -> (f32, f32)) -> f32 {
    let n = ts.len() as f64;
    let mut sum_x = 0.0;
    let mut sum_y = 0.0;
    let mut sum_xy = 0.0;
    let mut sum_x_squared = 0.0;

    for t in ts {
        let (x, y) = xy(*t);
        let x = x as f64;
        let y = y as f64;
        sum_x += x;
        sum_y += y;
        sum_xy += x * y;
        sum_x_squared += x * x;
    }

    let slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x * sum_x);
    slope as f32
}

impl<'a> UvBuffer<'a> {
    /// Given a point in the UV buffer, create a query that would sample the corrisponding texture.
    pub fn query(&self, Point2 { x, y }: Point2<usize>) -> Option<Query> {
        let u = self.0.get([y, x, 0]).copied()?;
        let v = self.0.get([y, x, 1]).copied()?;
        if !u.is_finite() || !v.is_finite() {
            return None;
        }

        // The tricky part here is seeing how the UV coordinate of neiboring pixels differs,
        // and determining how to rotate the normals in any normal map we might sample.

        let knots = [-32isize, -16, -4, 0, 4, 16, 32];
        let dudx = least_squares_slope(&knots, |t| {
            let x = (x as isize + t).clamp(0, self.0.dim().1 as isize - 1) as usize;
            (x as f32, *self.0.get([y, x, 0]).unwrap())
        });
        let dudy = least_squares_slope(&knots, |t| {
            let y = (y as isize + t).clamp(0, self.0.dim().0 as isize - 1) as usize;
            (y as f32, *self.0.get([y, x, 0]).unwrap())
        });
        let dvdx = least_squares_slope(&knots, |t| {
            let x = (x as isize + t).clamp(0, self.0.dim().1 as isize - 1) as usize;
            (x as f32, *self.0.get([y, x, 1]).unwrap())
        });
        let dvdy = least_squares_slope(&knots, |t| {
            let y = (y as isize + t).clamp(0, self.0.dim().0 as isize - 1) as usize;
            (y as f32, *self.0.get([y, x, 1]).unwrap())
        });

        let frame = Matrix2 {
            x: Vector2 { x: dudx, y: dvdx },
            y: Vector2 { x: dudy, y: dvdy },
        };

        Some(Query {
            point: Point2 { x: u, y: v },
            frame: Some(frame),
        })
    }
}

/// Given two different arbitrary parameterizations `dest` and `source`, figure
/// out how to smoothly warp arbitrary `source` pixels to the dest pixels that
/// have the closest matching parameter (e.g. UV coordinate).
pub struct NearestBuffer<'a> {
    pub dest: ArrayView3<'a, f32>,
    pub source: UvBuffer<'a>,
    pub nn: kdtree::KdTree<f32, Point2<usize>, &'a [f32]>,
}

impl<'a> NearestBuffer<'a> {
    pub fn new(dest: ArrayView3<'a, f32>, source: ArrayView3<'a, f32>) -> Self {
        let mut nn = kdtree::KdTree::new(source.dim().2);
        for i in 0..source.dim().0 {
            for j in 0..source.dim().1 {
                let _ = nn.add(
                    source.slice_move(s![i, j, ..]).to_slice().unwrap(),
                    Point2 { x: j, y: i },
                );
            }
        }
        let source = UvBuffer(source);
        NearestBuffer { dest, source, nn }
    }

    /// Where should the given point in `self.source` go on `self.dest`, so that
    /// the parameters match up.
    pub fn query(&self, Point2 { x, y }: Point2<usize>, margin: f32) -> Option<Query> {
        let q = self.dest.slice(s![y, x, ..]).to_slice()?;
        let sq_dist =
            |a: &[f32], b: &[f32]| -> f32 { a.iter().zip(b).map(|(a, b)| (a - b).powi(2)).sum() };
        let mut near = self.nn.iter_nearest(q, &sq_dist).ok()?;
        let (d, &pt_i) = near.next()?;
        let mut pt = pt_i.cast::<f32>()?;
        if d > margin.powi(2) {
            // we missed by at least `margin` units, consider there to be no match
            None
        } else {
            let q_uv = Point2 { x: q[0], y: q[1] };
            let Query { point: p_uv, frame } = self.source.query(pt_i)?;
            let err = q_uv - p_uv;
            if let Some(frame) = frame.and_then(|frame| frame.invert()) {
                pt += frame * err;
            };
            Some(Query {
                point: pt,
                // TODO: not currently used, which is good because this would be terrifying to
                // calculate.
                frame: None,
            })
        }
    }
}
