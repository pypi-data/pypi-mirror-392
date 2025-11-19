from typing import Any, Literal, Optional, Tuple, Dict, Callable, TypeAlias, TypedDict
from pathlib import Path
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass

@dataclass
class ImageRow:
    image: np.ndarray
    crop: Optional[Any] # Type of crop is not specified in Rust code

@dataclass
class Rows:
    name: Optional[str]
    caption: Optional[str]
    images: dict[str, ImageRow]

def save_image(
    path: str | Path,
    arr: np.ndarray,
    int16: bool = True,
    ext: Optional[str] = None,
) -> Optional[bytes]:
    """
    Saves a numpy array as an image file.

    Args:
        path: Path to save the image. If "-", returns bytes.
        arr: The image data as a NumPy array (H, W, C).
        int16: If True (default), save as 16-bit PNG/other. If False, save as 8-bit. Ignored for EXR.
        ext: File extension (e.g., "png", "exr"). If None, inferred from path.

    Returns:
        Bytes if path is "-", otherwise None.
    """
    ...

def open_image(path: str | Path) -> np.ndarray:
    """
    Opens an image file into a numpy array (float32).

    Args:
        path: Path to the image file.

    Returns:
        The image data as a NumPy array (H, W, C).
    """
    ...

def open_svbrdf(base: str | Path, name: Optional[str] = None) -> np.ndarray:
    """
    Opens SVBRDF maps (diffuse, specular, roughness, normals) and concatenates them.

    Searches for files containing 'diffuse', 'specular', 'roughness', 'normals'
    in the `base` directory. If `name` is provided and paths point to directories,
    it looks for files like `{name}_diffuse.png`.

    Args:
        base: Base directory or path prefix for the maps.
        name: Optional base name for the map files if `base` points to directories.

    Returns:
        Concatenated SVBRDF data as a NumPy array (H, W, 10).
        Channels: diffuse(3), specular(3), roughness(1), normals(3).
    """
    ...

def rasterize(svbrdf: np.ndarray, **kwargs: Any) -> np.ndarray:
    """
    Renders an SVBRDF using various lighting models.

    Args:
        svbrdf: The SVBRDF data (H, W, 10).
        **kwargs: Rendering arguments matching `gfxds::rast::RenderArgs`.
                  Common args include `mode` (e.g., "basic", "highlight", "dome"),
                  `light_pos`, `camera_pos`, `light_distance`, etc.

    Returns:
        The rendered image as a NumPy array (H, W, 6).
        Channels: RGB(3), XYZ normals(3).
    """
    ...

CropInfoCallback: TypeAlias = Callable[[Tuple[float, float, float, float, float, float]], None]

SubDataset = TypedDict('SubDataset', {'id': str, 'dataset': DatasetConfig | None, 'weight': float})
MultiDataset = TypedDict('MultiDataset', {'kind': Literal['Multi'], 'datasets': list[SubDataset] })
DatasetConfig: TypeAlias = MultiDataset | dict[str, Any]

def resize_and_crop(
    source: np.ndarray,
    width: int,
    height: Optional[int] = None,
    crop: float = 0.0,
    offset: Tuple[float, float] = (0.5, 0.5),
    with_cropinfo: Optional[CropInfoCallback] = None,
) -> np.ndarray:
    """
    Resizes and optionally crops an image.

    Args:
        source: The source image array (H, W, C).
        width: The target width.
        height: The target height. If None, defaults to `width`.
        crop: Crop factor (0.0 to 1.0). 0.0 means no crop (resize only).
              1.0 means crop maximum possible while preserving aspect ratio.
        offset: Normalized offset (x, y) for the crop center (0.0 to 1.0). (0.5, 0.5) is center.
        with_cropinfo: Optional callback function that receives crop information:
                       (source_w, source_h, offset_x, offset_y, dest_h, dest_w).

    Returns:
        The resized and cropped image array.
    """
    ...

def default_config() -> dict[str, DatasetConfig]:
    """
    Returns:
        Default datasets and configuration for each.
    """

def default_config_toml() -> str:
    """
    Returns:
        The datasets.toml this package was built with (see default_config).
    """

class Loader:
    resolved_config: Any
    
    def __init__(
        self,
        root: str | Path,
        dataset: str | DatasetConfig,
        seed: Optional[int] = None,
        concurrent: int = 4,
        epocs: int = 1, # Note: Python typically uses 'epochs'
        limit: Optional[int] = None,
        offset: int = 0,
        stride: int = 1,
        resize: Optional[tuple[int, int]] = None,
        configs: Dict[str, Any] = {},
    ) -> None:
        """
        Args:
            root: Root directory for datasets.
            dataset: Identifier of the dataset to load (see default_config) or a configuration object.
            seed: Random seed for shuffling and augmentations. Auto-generated if None.
            concurrent: Number of samples to load in parallel.
            epocs: Number of times to iterate through the dataset.
            limit: Maximum number of samples to yield per epoch.
            configs: Dictionary overriding dataset configurations. Keys are dataset IDs.
        """
        ...

    def start(self) -> None:
        """
        Initializes the loader, finds dataset files, and prepares for iteration.
        Must be called before iteration or __len__.
        """
        ...

    def __getitem__(self, index: int) -> Rows:
        """Gets a specific sample by index (after starting)."""
        ...

    def __len__(self) -> int:
        """Returns the total number of samples this loader will produce (after starting)."""
        ...

    def __iter__(self) -> "Loader":
        """Starts the loader (if not started) and returns the iterator."""
        ...

    def __next__(self) -> Rows:
        """Returns the next loaded sample."""
        ...

