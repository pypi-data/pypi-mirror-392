"""
CV-Preprocess: All-in-one Computer Vision Image Preprocessing Library
======================================================================

A single-file, production-ready computer vision image preprocessing library.

Usage:
    pip install opencv-python numpy pillow scikit-image

    from cv_preprocess import ImageLoader, ClassificationPipeline

    loader = ImageLoader()
    pipeline = ClassificationPipeline(image_size=(224, 224))

    image = loader.load_image('image.jpg', color_format='BGR')
    processed = pipeline.apply(image)

Author: Your Name
License: MIT
Version: 0.1.0
"""

import numpy as np
import cv2
from pathlib import Path
from typing import Union, Optional, Tuple, List, Callable, Dict, Any
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# BASE TRANSFORMER CLASS
# ============================================================================

class ImageTransformer(ABC):
    """Abstract base class for image transformations."""

    def __init__(self, **kwargs):
        """Initialize transformer with parameters."""
        self.params = kwargs

    @abstractmethod
    def transform(self, image: np.ndarray) -> np.ndarray:
        """Apply transformation to image."""
        pass

    def __call__(self, image: np.ndarray) -> np.ndarray:
        """Allow transformer to be called as function."""
        return self.transform(image)

    def get_params(self) -> Dict[str, Any]:
        """Get transformation parameters."""
        return self.params.copy()

    def set_params(self, **kwargs) -> None:
        """Update transformation parameters."""
        self.params.update(kwargs)


# ============================================================================
# IMAGE LOADER
# ============================================================================

class ImageLoader:
    """Load images from various sources and formats."""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}

    def __init__(self, preserve_alpha: bool = False):
        """Initialize ImageLoader."""
        self.preserve_alpha = preserve_alpha

    def load_image(
        self,
        path: Union[str, Path],
        color_format: str = 'RGB',
    ) -> np.ndarray:
        """Load image from file path."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {path.suffix}")

        image = cv2.imread(str(path))

        if image is None:
            raise ValueError(f"Failed to load image: {path}")

        if color_format.upper() == 'RGB':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif color_format.upper() == 'GRAY':
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return image

    def save_image(
        self,
        image: np.ndarray,
        path: Union[str, Path],
        color_format: str = 'RGB',
    ) -> None:
        """Save image to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if color_format.upper() == 'RGB':
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        cv2.imwrite(str(path), image)

    def get_image_info(self, image: np.ndarray) -> dict:
        """Get image metadata."""
        return {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'height': image.shape[0],
            'width': image.shape[1],
            'channels': image.shape[2] if len(image.shape) == 3 else 1,
            'size_mb': image.nbytes / (1024 * 1024),
        }


# ============================================================================
# NORMALIZER
# ============================================================================

class Normalizer(ImageTransformer):
    """Normalize pixel values."""

    def __init__(
        self,
        method: str = 'minmax',
        value_range: Tuple[float, float] = (0.0, 1.0),
        mean: Optional[Tuple[float, ...]] = None,
        std: Optional[Tuple[float, ...]] = None,
    ):
        """Initialize Normalizer."""
        super().__init__(method=method, value_range=value_range, mean=mean, std=std)
        self.method = method

    def transform(self, image: np.ndarray) -> np.ndarray:
        """Apply normalization."""
        if self.method == 'minmax':
            return self._minmax_normalize(image)
        elif self.method == 'zscore':
            return self._zscore_normalize(image)
        elif self.method == 'imagenet':
            return self._imagenet_normalize(image)
        elif self.method == 'custom':
            return self._custom_normalize(image)
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")

    def _minmax_normalize(self, image: np.ndarray) -> np.ndarray:
        """Min-Max normalization."""
        min_val = image.min()
        max_val = image.max()

        if max_val == min_val:
            return np.zeros_like(image, dtype=np.float32)

        normalized = (image.astype(np.float32) - min_val) / (max_val - min_val)

        if self.params['value_range'] != (0.0, 1.0):
            a, b = self.params['value_range']
            normalized = a + normalized * (b - a)

        return normalized

    def _zscore_normalize(self, image: np.ndarray) -> np.ndarray:
        """Z-score normalization."""
        mean = image.mean()
        std = image.std()

        if std == 0:
            return np.zeros_like(image, dtype=np.float32)

        return (image.astype(np.float32) - mean) / std

    def _imagenet_normalize(self, image: np.ndarray) -> np.ndarray:
        """ImageNet normalization."""
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])

        image = image.astype(np.float32) / 255.0

        if image.ndim == 3:
            image = (image - mean) / std

        return image

    def _custom_normalize(self, image: np.ndarray) -> np.ndarray:
        """Custom normalization."""
        mean = self.params.get('mean')
        std = self.params.get('std')

        if mean is None or std is None:
            raise ValueError("Mean and std required for custom normalization")

        image = image.astype(np.float32) / 255.0
        mean = np.array(mean)
        std = np.array(std)

        return (image - mean) / std


# ============================================================================
# RESIZER
# ============================================================================

class Resizer(ImageTransformer):
    """Resize images with various interpolation methods."""

    INTERPOLATION_METHODS = {
        'nearest': cv2.INTER_NEAREST,
        'bilinear': cv2.INTER_LINEAR,
        'bicubic': cv2.INTER_CUBIC,
        'lanczos4': cv2.INTER_LANCZOS4,
        'area': cv2.INTER_AREA,
    }

    def __init__(
        self,
        size: Tuple[int, int],
        interpolation: str = 'bilinear',
        maintain_aspect: bool = False,
        pad_value: int = 0,
    ):
        """Initialize Resizer."""
        super().__init__(
            size=size,
            interpolation=interpolation,
            maintain_aspect=maintain_aspect,
            pad_value=pad_value,
        )

    def transform(self, image: np.ndarray) -> np.ndarray:
        """Resize image."""
        if self.params['maintain_aspect']:
            return self._resize_with_aspect(image)
        else:
            return self._resize_direct(image)

    def _resize_direct(self, image: np.ndarray) -> np.ndarray:
        """Resize without maintaining aspect ratio."""
        target_h, target_w = self.params['size']
        interp = self.INTERPOLATION_METHODS[self.params['interpolation']]

        return cv2.resize(image, (target_w, target_h), interpolation=interp)

    def _resize_with_aspect(self, image: np.ndarray) -> np.ndarray:
        """Resize while maintaining aspect ratio."""
        h, w = image.shape[:2]
        target_h, target_w = self.params['size']

        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        interp = self.INTERPOLATION_METHODS[self.params['interpolation']]
        resized = cv2.resize(image, (new_w, new_h), interpolation=interp)

        top = (target_h - new_h) // 2
        bottom = target_h - new_h - top
        left = (target_w - new_w) // 2
        right = target_w - new_w - left

        return cv2.copyMakeBorder(
            resized, top, bottom, left, right,
            cv2.BORDER_CONSTANT,
            value=self.params['pad_value'],
        )

    def crop_center(self, image: np.ndarray, crop_size: Tuple[int, int]) -> np.ndarray:
        """Crop center region of image."""
        h, w = image.shape[:2]
        crop_h, crop_w = crop_size

        top = (h - crop_h) // 2
        left = (w - crop_w) // 2

        return image[top:top+crop_h, left:left+crop_w]


# ============================================================================
# COLOR SPACE CONVERTER
# ============================================================================

class ColorSpaceConverter(ImageTransformer):
    """Convert between different color spaces."""

    CONVERSIONS = {
        'RGB_to_BGR': cv2.COLOR_RGB2BGR,
        'BGR_to_RGB': cv2.COLOR_BGR2RGB,
        'RGB_to_GRAY': cv2.COLOR_RGB2GRAY,
        'BGR_to_GRAY': cv2.COLOR_BGR2GRAY,
        'RGB_to_HSV': cv2.COLOR_RGB2HSV,
        'BGR_to_HSV': cv2.COLOR_BGR2HSV,
        'RGB_to_LAB': cv2.COLOR_RGB2LAB,
        'BGR_to_LAB': cv2.COLOR_BGR2LAB,
        'RGB_to_YCrCb': cv2.COLOR_RGB2YCrCb,
        'BGR_to_YCrCb': cv2.COLOR_BGR2YCrCb,
    }

    def __init__(self, source_space: str, target_space: str):
        """Initialize ColorSpaceConverter."""
        conversion_key = f"{source_space}_to_{target_space}"
        if conversion_key not in self.CONVERSIONS:
            raise ValueError(f"Unsupported conversion: {conversion_key}")

        super().__init__(source_space=source_space, target_space=target_space)
        self.conversion_key = conversion_key

    def transform(self, image: np.ndarray) -> np.ndarray:
        """Convert color space."""
        conversion_code = self.CONVERSIONS[self.conversion_key]
        return cv2.cvtColor(image, conversion_code)


# ============================================================================
# FILTER APPLIER
# ============================================================================

class FilterApplier(ImageTransformer):
    """Apply various filters to images."""

    def __init__(self, filter_type: str = 'gaussian', **filter_params):
        """Initialize FilterApplier."""
        super().__init__(filter_type=filter_type, **filter_params)

    def transform(self, image: np.ndarray) -> np.ndarray:
        """Apply filter."""
        filter_type = self.params['filter_type']

        if filter_type == 'gaussian':
            kernel_size = self.params.get('kernel_size', 5)
            sigma = self.params.get('sigma', 1.0)
            if kernel_size % 2 == 0:
                kernel_size += 1
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

        elif filter_type == 'median':
            kernel_size = self.params.get('kernel_size', 5)
            if kernel_size % 2 == 0:
                kernel_size += 1
            return cv2.medianBlur(image, kernel_size)

        elif filter_type == 'bilateral':
            diameter = self.params.get('diameter', 9)
            sigma_color = self.params.get('sigma_color', 75)
            sigma_space = self.params.get('sigma_space', 75)
            return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)

        else:
            raise ValueError(f"Unknown filter type: {filter_type}")

    def adjust_contrast(self, image: np.ndarray, alpha: float = 1.5, beta: float = 0) -> np.ndarray:
        """Adjust contrast and brightness."""
        result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return np.uint8(np.clip(result, 0, 255))


# ============================================================================
# AUGMENTER
# ============================================================================

class Augmenter(ImageTransformer):
    """Apply data augmentation transformations."""

    def __init__(self, **augmentation_params):
        """Initialize Augmenter."""
        super().__init__(**augmentation_params)

    def transform(self, image: np.ndarray) -> np.ndarray:
        """Apply augmentation."""
        return image

    def random_flip(
        self,
        image: np.ndarray,
        direction: str = 'horizontal',
        probability: float = 0.5,
    ) -> np.ndarray:
        """Randomly flip image."""
        if np.random.random() < probability:
            if direction == 'horizontal':
                return cv2.flip(image, 1)
            elif direction == 'vertical':
                return cv2.flip(image, 0)
            elif direction == 'both':
                return cv2.flip(image, -1)
        return image

    def random_rotation(
        self,
        image: np.ndarray,
        angle_range: Tuple[float, float] = (-30, 30),
        probability: float = 0.5,
    ) -> np.ndarray:
        """Randomly rotate image."""
        if np.random.random() < probability:
            angle = np.random.uniform(*angle_range)
            h, w = image.shape[:2]
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            return cv2.warpAffine(image, matrix, (w, h))
        return image

    def random_brightness(
        self,
        image: np.ndarray,
        brightness_range: Tuple[float, float] = (0.8, 1.2),
        probability: float = 0.5,
    ) -> np.ndarray:
        """Randomly adjust brightness."""
        if np.random.random() < probability:
            brightness_factor = np.random.uniform(*brightness_range)
            image = image.astype(np.float32) * brightness_factor
            return np.uint8(np.clip(image, 0, 255))
        return image

    def random_noise(
        self,
        image: np.ndarray,
        noise_scale: float = 0.1,
        probability: float = 0.5,
    ) -> np.ndarray:
        """Add random noise to image."""
        if np.random.random() < probability:
            noise = np.random.normal(0, noise_scale, image.shape)
            image = image.astype(np.float32) + noise * 255
            return np.uint8(np.clip(image, 0, 255))
        return image


# ============================================================================
# BATCH PROCESSOR
# ============================================================================

class BatchProcessor:
    """Process multiple images efficiently with parallel support."""

    def __init__(
        self,
        num_workers: int = 4,
        use_threads: bool = False,
        verbose: bool = False,
    ):
        """Initialize BatchProcessor."""
        self.num_workers = num_workers
        self.use_threads = use_threads
        self.verbose = verbose

    def process_batch(
        self,
        image_paths: List[Union[str, Path]],
        process_func: Callable,
    ) -> List[np.ndarray]:
        """Process batch of images in parallel."""
        executor_class = ThreadPoolExecutor if self.use_threads else ProcessPoolExecutor

        results = []
        total = len(image_paths)

        with executor_class(max_workers=self.num_workers) as executor:
            futures = {executor.submit(process_func, path): path for path in image_paths}

            for idx, future in enumerate(futures, 1):
                try:
                    result = future.result()
                    results.append(result)
                    if self.verbose:
                        print(f"Processed {idx}/{total}")
                except Exception as e:
                    if self.verbose:
                        print(f"Error processing {futures[future]}: {e}")
                    continue

        return results

    def process_directory(
        self,
        directory: Union[str, Path],
        process_func: Callable,
        recursive: bool = False,
        extensions: tuple = ('.jpg', '.png', '.bmp'),
    ) -> List[np.ndarray]:
        """Process all images in a directory."""
        directory = Path(directory)

        if recursive:
            image_paths = [p for ext in extensions for p in directory.rglob(f'*{ext}')]
        else:
            image_paths = [p for ext in extensions for p in directory.glob(f'*{ext}')]

        if self.verbose:
            print(f"Found {len(image_paths)} images")

        return self.process_batch(image_paths, process_func)


# ============================================================================
# PIPELINES
# ============================================================================

class BasePipeline:
    """Compose multiple image transformations into a pipeline."""

    def __init__(self, name: str = "Pipeline"):
        """Initialize pipeline."""
        self.name = name
        self.transformations: List[ImageTransformer] = []

    def add_transform(self, transformer: ImageTransformer) -> 'BasePipeline':
        """Add transformation to pipeline."""
        self.transformations.append(transformer)
        return self

    def add_custom_transform(self, func: Callable) -> 'BasePipeline':
        """Add custom transformation function."""
        class CustomTransformer(ImageTransformer):
            def transform(self, image: np.ndarray) -> np.ndarray:
                return func(image)

        self.transformations.append(CustomTransformer())
        return self

    def apply(self, image: np.ndarray) -> np.ndarray:
        """Apply all transformations in sequence."""
        result = image.copy()
        for transformer in self.transformations:
            result = transformer.transform(result)
        return result

    def __call__(self, image: np.ndarray) -> np.ndarray:
        """Allow pipeline to be called as function."""
        return self.apply(image)

    def get_summary(self) -> str:
        """Get pipeline summary."""
        lines = [f"Pipeline: {self.name}"]
        lines.append(f"Total transformations: {len(self.transformations)}")
        for idx, transformer in enumerate(self.transformations, 1):
            lines.append(f"  {idx}. {transformer.__class__.__name__}")
        return "\n".join(lines)


class ClassificationPipeline(BasePipeline):
    """Pipeline for image classification preprocessing."""

    def __init__(self, image_size: tuple = (224, 224), normalize: bool = True):
        """Initialize classification pipeline."""
        super().__init__(name="ClassificationPipeline")
        self.add_transform(ColorSpaceConverter('BGR', 'RGB'))
        self.add_transform(Resizer(image_size, interpolation='bilinear'))
        if normalize:
            self.add_transform(Normalizer(method='imagenet'))


class DetectionPipeline(BasePipeline):
    """Pipeline for object detection preprocessing."""

    def __init__(self, image_size: tuple = (640, 640), normalize: bool = True):
        """Initialize detection pipeline."""
        super().__init__(name="DetectionPipeline")
        self.add_transform(ColorSpaceConverter('BGR', 'RGB'))
        self.add_transform(Resizer(image_size, interpolation='bilinear', maintain_aspect=True))
        if normalize:
            self.add_transform(Normalizer(method='minmax', value_range=(0, 1)))


class DenoisingPipeline(BasePipeline):
    """Pipeline for image denoising."""

    def __init__(self):
        """Initialize denoising pipeline."""
        super().__init__(name="DenoisingPipeline")
        self.add_transform(FilterApplier(filter_type='bilateral', diameter=9, sigma_color=75, sigma_space=75))
        self.add_transform(FilterApplier(filter_type='gaussian', kernel_size=5))


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ImageLoader',
    'ImageTransformer',
    'Normalizer',
    'Resizer',
    'ColorSpaceConverter',
    'FilterApplier',
    'Augmenter',
    'BatchProcessor',
    'BasePipeline',
    'ClassificationPipeline',
    'DetectionPipeline',
    'DenoisingPipeline',
]


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("CV-Preprocess - Computer Vision Image Preprocessing Library")
    print("=" * 60)

    print("\nAvailable Classes:")
    for cls_name in __all__:
        print(f"  - {cls_name}")

    print("\nQuick Start Example:")
    print("""
    from cv_preprocess import ImageLoader, ClassificationPipeline

    # Load image
    loader = ImageLoader()
    image = loader.load_image('image.jpg', color_format='BGR')

    # Process with classification pipeline
    pipeline = ClassificationPipeline(image_size=(224, 224))
    processed = pipeline.apply(image)

    # Save result
    loader.save_image(processed, 'output.jpg', color_format='RGB')
    """)
