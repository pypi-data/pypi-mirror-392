use super::{Dataset, DatasetBase, DatasetContext, Rows};
use crate::error::{ErrorKind, ResultExt};
use crate::imgutil::open_image;
use crate::Error;
use derivative::Derivative;
use rand::rngs::StdRng;
use regex::RegexSet;
use std::ffi::OsStr;
use std::fs;
use std::path::Path;
use url::Url;

fn load_split(root: &Path, split: &str) -> Result<Vec<String>, Error> {
    let path = root.join(format!("{split}.txt"));
    if path.exists() {
        Ok(fs::read_to_string(&path)
            .path_context(&path)?
            .lines()
            .map(|line| line.trim().to_string())
            .filter(|line| !line.is_empty())
            .collect())
    } else {
        let path = root.join("split.csv");
        Ok(fs::read_to_string(&path)
            .path_context(&path)?
            .lines()
            .filter_map(|line| line.trim().split_once(','))
            .filter(|&(_, s)| s == split)
            .map(|(n, _)| n.to_string())
            .collect())
    }
}

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct NestedImageFolder {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub split: String,
    pub name: Option<String>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<String>, // Stores the 'name' from the split file lines
    pub matching: Option<Vec<(String, f64)>>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub matching_regex: RegexSet,
}

#[typetag::serde]
impl Dataset for NestedImageFolder {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        if let Some(weightby) = &self.matching {
            self.matching_regex = RegexSet::new(weightby.iter().map(|(re, _)| re))?;
        }

        let dir_path = ctx.resolve_to_path(&self.dir)?;
        self.found = load_split(&dir_path, &self.split)?;
        self.found.sort(); // Ensure consistent order

        if self.found.is_empty() {
            return Err(ErrorKind::EmptyDataset.into());
        }
        self.base.check_count(self.found.len())?;
        Ok(())
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let name = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let item_dir_path = ctx.resolve_to_path(&self.dir)?.join(name);

        for entry_result in fs::read_dir(&item_dir_path).path_context(&item_dir_path)? {
            let entry = entry_result.path_context(&item_dir_path)?;
            let path = entry.path();

            if path.is_file() {
                if let Some(extension) = path.extension().and_then(OsStr::to_str) {
                    if extension.eq_ignore_ascii_case("png")
                        || extension.eq_ignore_ascii_case("jpg")
                        || extension.eq_ignore_ascii_case("jpeg")
                    {
                        let Some(file_stem) = path.file_stem().and_then(OsStr::to_str) else {
                            // Skip files without a valid stem (e.g., hidden files like .DS_Store)
                            continue;
                        };
                        let component_name = file_stem.to_string();
                        let image_array = open_image(&path)?; // open_image handles its own path_context
                        rows.image(component_name, image_array);
                    }
                }
            }
        }

        if rows.images.is_empty() {
            return Err(ErrorKind::SkipSample.into());
        }

        let caption_path = item_dir_path.join("caption.txt");
        match fs::read_to_string(&caption_path) {
            Ok(text) => rows.caption(text.trim().to_string()),
            Err(err) if err.kind() == std::io::ErrorKind::NotFound => {
                // Caption is optional, so no error if not found
            }
            Err(err) => return Err(err).path_context(&caption_path),
        };

        rows.name(format!(
            "{}_{}",
            self.name.as_deref().unwrap_or("imagefolder"),
            name
        ));
        self.base.resize_images(rows, rng, ctx)?;

        Ok(())
    }

    fn count(&self) -> usize {
        self.found.len()
    }

    fn weights(&self) -> Option<Vec<f64>> {
        let matching = self.matching.as_ref()?;
        let mut weights = Vec::with_capacity(self.found.len());
        for name in &self.found {
            weights.push(match self.matching_regex.matches(name).iter().next() {
                Some(index) => matching[index].1,
                None => 0.0,
            });
        }
        Some(weights)
    }
}

#[derive(serde::Deserialize, serde::Serialize, Derivative)]
#[derivative(Debug)]
pub struct ImageFolder {
    #[serde(flatten)]
    pub base: DatasetBase,
    pub dir: Url,
    pub split: String,
    pub component: String,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub found: Vec<String>, // Stores the 'name' from the split file lines
    pub matching: Option<Vec<(String, f64)>>,
    #[serde(skip)]
    #[derivative(Debug = "ignore")]
    pub matching_regex: RegexSet,
}

#[typetag::serde]
impl Dataset for ImageFolder {
    fn start(&mut self, ctx: &DatasetContext) -> Result<(), Error> {
        if let Some(weightby) = &self.matching {
            self.matching_regex = RegexSet::new(weightby.iter().map(|(re, _)| re))?;
        }

        let dir_path = ctx.resolve_to_path(&self.dir)?;
        self.found = load_split(&dir_path, &self.split)?;
        self.found.sort(); // Ensure consistent order

        if self.found.is_empty() {
            return Err(ErrorKind::EmptyDataset.into());
        }
        self.base.check_count(self.found.len())?;
        Ok(())
    }

    fn get(
        &self,
        rows: &mut Rows,
        rng: &mut StdRng,
        ctx: &DatasetContext,
        index: usize,
    ) -> Result<(), Error> {
        let name = self.found.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let dir_path = ctx.resolve_to_path(&self.dir)?;

        for ext in ["png", "jpg", "jpeg", "exr"] {
            let path = dir_path.join(format!("{name}.{ext}"));
            if path.exists() {
                let image_array = open_image(&path)?;
                rows.image(self.component.clone(), image_array);
                break;
            }
        }

        if rows.images.is_empty() {
            return Err(ErrorKind::SkipSample.into());
        }

        let path = dir_path.join(format!("{name}.txt"));
        match fs::read_to_string(&path) {
            Ok(text) => rows.caption(text.trim().to_string()),
            Err(err) if err.kind() == std::io::ErrorKind::NotFound => {
                // Caption is optional, so no error if not found
            }
            Err(err) => return Err(err).path_context(&path),
        };

        rows.name(name);
        self.base.resize_images(rows, rng, ctx)?;

        Ok(())
    }

    fn count(&self) -> usize {
        self.found.len()
    }

    fn weights(&self) -> Option<Vec<f64>> {
        let matching = self.matching.as_ref()?;
        let mut weights = Vec::with_capacity(self.found.len());
        for name in &self.found {
            weights.push(match self.matching_regex.matches(name).iter().next() {
                Some(index) => matching[index].1,
                None => 0.0,
            });
        }
        Some(weights)
    }
}
