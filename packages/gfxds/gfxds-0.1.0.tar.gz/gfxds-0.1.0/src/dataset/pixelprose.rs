use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::ResultExt;
use crate::imgutil::{image2array, LimitedReader};
use crate::{Error, ErrorKind};
use derivative::Derivative;
use image::ImageFormat;
use parquet::file::serialized_reader::SerializedFileReader;
use rand::rngs::StdRng;
use regex::Regex;
use std::cell::Cell;
use std::io::{Cursor, Read};
use std::time::Duration;
use url::Url;

#[derive(serde::Deserialize)]
pub struct PixelProseRow {
    key: String,
    url: String,
    vlm_caption: String,
    width: usize,
    height: usize,
}

#[derive(serde::Serialize, serde::Deserialize, Derivative)]
#[derivative(Debug)]
#[serde(deny_unknown_fields)]
pub struct PixelProse {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub is_train: bool,
    #[serde(with = "serde_regex")]
    pub caption_find: Regex,
    pub caption_replace: String,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<PixelProseRow>,
}

#[typetag::serde]
impl Dataset for PixelProse {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        self.found.clear();
        let dir_path = ctx.resolve_to_path(&self.dir)?;
        let mut splits = vec![self.is_train; 10];
        splits[0] = !splits[0]; // Use split 0 for validation, rest for training

        let data_dir = dir_path.join("data");
        for e in data_dir.read_dir().path_context(&data_dir)? {
            let e = e?;
            if !e.file_name().to_string_lossy().ends_with(".parquet") {
                continue;
            }
            let file = SerializedFileReader::try_from(e.path().as_path())?;
            for r in file {
                let r = r?;
                let r: PixelProseRow = serde_json::from_value(r.to_json_value())?;
                if r.width < 512 || r.height < 512 {
                    continue;
                }
                self.found.push(r);
            }
        }
        self.found.sort_by(|a, b| a.key.cmp(&b.key));
        let i = Cell::new(0);
        self.found
            .retain(|_| splits[i.replace(i.get() + 1) % splits.len()]);
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
        let chosen = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;

        // Retry mechanism could be added here if desired
        let response = match ureq::get(&chosen.url)
            .timeout(Duration::from_secs(10)) // Increased timeout
            .call()
        {
            Ok(res) => res,
            Err(err) => {
                eprintln!("Skipping {}: HTTP error {}", chosen.key, err);
                return Err(ErrorKind::SkipSample.into());
            }
        };

        if response.status() != 200 {
            eprintln!("Skipping {}: HTTP status {}", chosen.key, response.status());
            return Err(ErrorKind::SkipSample.into());
        }

        let format = response
            .header("Content-Type")
            .and_then(ImageFormat::from_mime_type);

        let mut body = Vec::new();
        LimitedReader::new(response.into_reader(), 40_000_000) // 40MB limit
            .read_to_end(&mut body)
            .map_err(|io_err| {
                eprintln!("Skipping {}: Read error: {}", chosen.key, io_err);
                ErrorKind::SkipSample // Treat read errors (like limit exceeded) as skippable
            })?;

        let mut reader = image::io::Reader::new(Cursor::new(body));
        if let Some(format) = format {
            reader.set_format(format);
        } else {
            reader = reader.with_guessed_format().map_err(|_| {
                eprintln!("Skipping {}: Could not guess format", chosen.key);
                ErrorKind::SkipSample // Treat format guessing failure as skippable
            })?;
        }

        let image = reader.decode().map_err(|img_err| {
            eprintln!("Skipping {}: Decode error: {}", chosen.key, img_err);
            ErrorKind::SkipSample // Treat decode errors as skippable
        })?;

        if image.width() < 512 || image.height() < 512 {
            eprintln!(
                "Skipping {}: Image too small ({}x{})",
                chosen.key,
                image.width(),
                image.height()
            );
            return Err(ErrorKind::SkipSample.into());
        }
        rows.image("image", image2array(image)?);

        let mut buffer = String::new();
        let caption = &chosen.vlm_caption;
        let caption = match self.caption_find.captures(caption) {
            Some(caps) => {
                caps.expand(&self.caption_replace, &mut buffer);
                &buffer
            }
            None => {
                eprintln!(
                    "Skipping {}: Caption {} did not match regex",
                    chosen.key, caption
                );
                return Err(ErrorKind::SkipSample.into()); // Skip if caption doesn't match
            }
        };
        rows.name(format!("pixelprose_{}", &chosen.key));
        rows.caption(caption.trim()); // Trim whitespace from caption

        // TODO: Previous call was process_images(rows, 0.0, rng);
        // This used a fixed crop value. Current resize_images uses self.base.resize_using_crop.
        self.base.resize_images(rows, rng, ctx)?;
        Ok(())
    }
}
