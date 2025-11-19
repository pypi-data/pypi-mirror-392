use crate::dataset::{Dataset, DatasetContext, Rows};
use crate::{Error, ErrorKind};
use async_cell::sync::AsyncCell;
use rand::{rngs::StdRng, seq::SliceRandom, Rng, SeedableRng};
use rand_distr::Distribution;
use std::collections::VecDeque;
use std::sync::Arc;

pub struct Loader {
    pub seed: u64,
    pub ctx: Arc<DatasetContext>,
    pub sample_limit: Option<usize>,
    pub replacement: bool,
    pub offset: usize,
    pub stride: usize,
    pub concurrent: usize,
    pub remaining_epocs: usize,
    pub dataset: Arc<dyn Dataset>,
    dataset_id: Option<String>,
    next_index: usize,
    shuffle: Vec<usize>,
    pending: VecDeque<Arc<AsyncCell<Result<Rows, Error>>>>,
    weights: Option<Vec<f64>>,
}

impl Loader {
    pub fn new_with_id(seed: u64, ctx: DatasetContext, id: &str) -> Result<Self, Error> {
        let dataset = ctx.dataset_from_id(id)?;
        let mut loader = Loader::new(seed, ctx, dataset)?;
        loader.dataset_id = Some(id.to_owned());
        Ok(loader)
    }

    pub fn new(seed: u64, ctx: DatasetContext, dataset: Box<dyn Dataset>) -> Result<Self, Error> {
        Ok(Loader {
            seed,
            ctx: Arc::new(ctx),
            sample_limit: None,
            replacement: false,
            offset: 0,
            stride: 1,
            concurrent: 1,
            remaining_epocs: 1,
            next_index: 0,
            dataset: Arc::from(dataset),
            dataset_id: None,
            shuffle: Vec::new(),
            pending: VecDeque::new(),
            weights: None,
        })
    }

    pub fn total_in_epoc(&self) -> usize {
        let count = self.dataset.count();
        match self.sample_limit {
            Some(limit) => count.min(limit),
            None => count,
        }
    }

    pub fn started(&self) -> bool {
        !self.shuffle.is_empty()
    }

    pub fn total(&self) -> usize {
        self.shuffle.len() + self.total_in_epoc() * self.remaining_epocs
    }

    pub fn dataset_total(&self) -> usize {
        self.dataset.count()
    }

    pub fn dataset(&self) -> &dyn Dataset {
        &*self.dataset
    }

    pub fn start(&mut self) -> Result<(), Error> {
        if self.started() {
            return Ok(());
        }

        // Get a mutable reference to the dataset in the Arc
        // This will only work if the Arc has not been cloned yet (i.e., before scheduling)
        let dataset = Arc::get_mut(&mut self.dataset)
            .expect("cannot start dataset after scheduling has begun");

        dataset.start(&self.ctx)?;
        self.weights = dataset.weights();
        self.begin_epoc();
        Ok(())
    }

    pub fn get(&self, index: usize) -> Result<Rows, Error> {
        if self.shuffle.is_empty() {
            panic!("must call start before loading data");
        }
        let real_index = *self.shuffle.get(index).ok_or(ErrorKind::IllegalIndex)?;
        let mut rng = StdRng::seed_from_u64(self.seed.wrapping_add(real_index as u64));
        let mut rows = Rows::default();
        if let Some(dataset_id) = &self.dataset_id {
            rows.dataset_id = dataset_id.clone();
        }
        self.dataset
            .get(&mut rows, &mut rng, &self.ctx, real_index)?;
        Ok(rows)
    }

    pub fn schedule(&mut self) {
        while self.pending.len() < self.concurrent {
            // First, get the index from shuffle
            let real_index = match self.shuffle.get(self.next_index) {
                Some(i) => {
                    self.next_index += self.stride;
                    *i
                }
                None => {
                    if self.remaining_epocs == 0 {
                        return;
                    }
                    // re-seed the loader
                    let mut rng = StdRng::seed_from_u64(self.seed.wrapping_sub(2));
                    self.seed = rng.gen();
                    self.begin_epoc();
                    continue;
                }
            };

            // Get relevant values before moving anything into the closure
            let mut rng = StdRng::seed_from_u64(self.seed.wrapping_add(real_index as u64));
            let mut rows = Rows::default();
            let dataset = self.dataset.clone();
            let ctx = self.ctx.clone();

            let cell = Arc::new(AsyncCell::new());
            let thread_cell = cell.guard_shared(Err(ErrorKind::Paniced.into()));
            self.pending.push_back(cell);

            rayon::spawn(move || {
                let res = dataset.get(&mut rows, &mut rng, &ctx, real_index);
                match res {
                    Ok(_) => thread_cell.set(Ok(rows)),
                    Err(e) => thread_cell.set(Err(e)),
                }
            });
        }
    }

    pub async fn next(&mut self) -> Option<Result<Rows, Error>> {
        let out = loop {
            self.schedule();
            if self.pending.is_empty() {
                return None;
            }
            match self
                .pending
                .pop_front()
                .expect("concurrent is 0")
                .take()
                .await
            {
                Err(Error {
                    kind: ErrorKind::Paniced | ErrorKind::SkipSample,
                    ..
                }) => continue,
                res => break res,
            }
        };
        self.schedule();
        Some(out)
    }

    fn begin_epoc(&mut self) {
        self.next_index = self.offset;
        let mut rng = StdRng::seed_from_u64(self.seed.wrapping_sub(1));
        self.remaining_epocs = self.remaining_epocs.saturating_sub(1);
        self.shuffle.clear();
        self.shuffle.extend(0..self.dataset.count());
        if let Some(w) = &self.weights {
            self.shuffle.retain(|i| w[*i] > 0.0);
        }
        match (self.sample_limit, &self.weights, self.replacement) {
            (Some(limit), Some(w), true) => {
                let dist = rand_distr::WeightedIndex::new(w).unwrap();
                self.shuffle = (0..limit).map(|_| dist.sample(&mut rng)).collect();
            }
            (Some(limit), None, true) => {
                self.shuffle = (0..limit)
                    .map(|_| *self.shuffle.choose(&mut rng).unwrap())
                    .collect();
            }
            (Some(limit), Some(w), false) => {
                self.shuffle = self
                    .shuffle
                    .choose_multiple_weighted(&mut rng, limit, |i| w[*i])
                    .unwrap()
                    .copied()
                    .collect();
            }
            (Some(limit), None, false) => {
                self.shuffle.shuffle(&mut rng);
                self.shuffle.truncate(limit);
            }
            (None, _, _) => {
                if self.weights.is_some() {
                    eprintln!("WARNING: no limit set on epoc size, including all samples and ignoring sample weights");
                }
                if self.replacement {
                    eprintln!("WARNING: no limit set on epoc size, including all samples without replacement");
                }
                self.shuffle.shuffle(&mut rng);
            }
        }
    }
}
