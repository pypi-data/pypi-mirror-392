# CV-Preprocess - Computer Vision Image Preprocessing Library

A production-ready, single-file Python library for image preprocessing in computer vision tasks.

## Features

- **Image Loading**: Load images in multiple formats (JPG, PNG, BMP, TIFF, GIF, WebP)
- **Normalization**: Min-Max, Z-score, ImageNet, and custom normalization
- **Resizing**: Image resizing with optional aspect ratio preservation
- **Color Space Conversion**: Convert between RGB, BGR, Grayscale, HSV, LAB, YCrCb
- **Filtering**: Gaussian blur, median filter, bilateral filter
- **Augmentation**: Random flip, rotation, brightness, and noise
- **Batch Processing**: Parallel processing of image directories
- **Pre-built Pipelines**: Classification, Detection, Denoising pipelines
- **Single File**: Everything in one Python file for easy distribution
- **Type Hints**: Full type annotation support
- **Production Ready**: Comprehensive error handling and logging

## Installation

```bash
pip install cv-preprocess
```

## Quick Start

### Basic Usage

```python
from cv_preprocess import ImageLoader, ClassificationPipeline

# Load image
loader = ImageLoader()
image = loader.load_image('image.jpg', color_format='BGR')

# Apply classification pipeline
pipeline = ClassificationPipeline(image_size=(224, 224))
processed = pipeline.apply(image)

# Save result
loader.save_image(processed, 'output.jpg', color_format='RGB')
```

### Using Different Pipelines

```python
from cv_preprocess import DetectionPipeline, DenoisingPipeline

# Object detection
detection_pipeline = DetectionPipeline(image_size=(640, 640))
detected = detection_pipeline.apply(image)

# Denoising
denoising_pipeline = DenoisingPipeline()
denoised = denoising_pipeline.apply(image)
```

### Custom Transformations

```python
from cv_preprocess import BasePipeline, Normalizer, Resizer, ColorSpaceConverter

# Create custom pipeline
pipeline = BasePipeline(name="Custom")
pipeline.add_transform(ColorSpaceConverter('BGR', 'RGB'))
pipeline.add_transform(Resizer((256, 256)))
pipeline.add_transform(Normalizer(method='imagenet'))

result = pipeline.apply(image)
```

### Data Augmentation

```python
from cv_preprocess import Augmenter

augmenter = Augmenter()
image = augmenter.random_flip(image, direction='horizontal', probability=0.5)
image = augmenter.random_rotation(image, angle_range=(-30, 30), probability=0.5)
image = augmenter.random_brightness(image, brightness_range=(0.8, 1.2), probability=0.5)
image = augmenter.random_noise(image, noise_scale=0.1, probability=0.5)
```

### Batch Processing

```python
from cv_preprocess import ImageLoader, BatchProcessor, ClassificationPipeline

loader = ImageLoader()
pipeline = ClassificationPipeline()
processor = BatchProcessor(num_workers=4, verbose=True)

def process_image(path):
    image = loader.load_image(path, color_format='BGR')
    return pipeline.apply(image)

# Process entire directory
results = processor.process_directory('./images/', process_image, recursive=True)
```

## Available Classes

### Core Classes

- **ImageLoader**: Load, save, and inspect images
- **ImageTransformer**: Abstract base class for transformations
- **BatchProcessor**: Parallel batch processing

### Preprocessing Classes

- **Normalizer**: Pixel value normalization (minmax, zscore, imagenet, custom)
- **Resizer**: Image resizing with interpolation options
- **ColorSpaceConverter**: Color space transformations
- **FilterApplier**: Image filtering (gaussian, median, bilateral)
- **Augmenter**: Data augmentation operations

### Pipeline Classes

- **BasePipeline**: Composable pipeline for chaining transformations
- **ClassificationPipeline**: Pre-configured for image classification
- **DetectionPipeline**: Pre-configured for object detection
- **DenoisingPipeline**: Pre-configured for image denoising

## Requirements

- Python 3.8+
- NumPy >= 1.21.0
- OpenCV >= 4.5.0
- Pillow >= 9.0.0
- scikit-image >= 0.19.0

## API Reference

### ImageLoader

```python
loader = ImageLoader()

# Load image
image = loader.load_image('path.jpg', color_format='RGB')

# Save image
loader.save_image(image, 'output.jpg', color_format='RGB')

# Get image info
info = loader.get_image_info(image)
# Returns: {'shape': tuple, 'dtype': str, 'height': int, 'width': int, 'channels': int, 'size_mb': float}
```

### Normalizer

```python
# Min-Max normalization
normalizer = Normalizer(method='minmax', value_range=(0.0, 1.0))
normalized = normalizer.transform(image)

# ImageNet normalization
normalizer = Normalizer(method='imagenet')
normalized = normalizer.transform(image)

# Z-score normalization
normalizer = Normalizer(method='zscore')
normalized = normalizer.transform(image)

# Custom normalization
normalizer = Normalizer(method='custom', mean=[0.5, 0.5, 0.5], std=[0.2, 0.2, 0.2])
normalized = normalizer.transform(image)
```

### Resizer

```python
# Direct resize
resizer = Resizer(size=(224, 224), interpolation='bilinear')
resized = resizer.transform(image)

# Resize with aspect ratio preservation
resizer = Resizer(size=(224, 224), interpolation='bilinear', maintain_aspect=True, pad_value=0)
resized = resizer.transform(image)

# Crop center
cropped = resizer.crop_center(image, crop_size=(224, 224))
```

### ColorSpaceConverter

```python
converter = ColorSpaceConverter('BGR', 'RGB')
converted = converter.transform(image)

# Supported conversions: RGB<->BGR, to/from GRAY, HSV, LAB, YCrCb
```

### FilterApplier

```python
# Gaussian blur
filter_applier = FilterApplier(filter_type='gaussian', kernel_size=5, sigma=1.0)
filtered = filter_applier.transform(image)

# Median blur
filter_applier = FilterApplier(filter_type='median', kernel_size=5)
filtered = filter_applier.transform(image)

# Bilateral filter (edge-preserving)
filter_applier = FilterApplier(filter_type='bilateral', diameter=9, sigma_color=75, sigma_space=75)
filtered = filter_applier.transform(image)

# Adjust contrast
result = filter_applier.adjust_contrast(image, alpha=1.5, beta=0)
```

### Augmenter

```python
augmenter = Augmenter()

# Random flip
image = augmenter.random_flip(image, direction='horizontal', probability=0.5)

# Random rotation
image = augmenter.random_rotation(image, angle_range=(-30, 30), probability=0.5)

# Random brightness
image = augmenter.random_brightness(image, brightness_range=(0.8, 1.2), probability=0.5)

# Add random noise
image = augmenter.random_noise(image, noise_scale=0.1, probability=0.5)
```

### BasePipeline

```python
pipeline = BasePipeline(name="MyPipeline")

# Add transformers
pipeline.add_transform(transformer1)
pipeline.add_transform(transformer2)

# Add custom function
pipeline.add_custom_transform(lambda x: x / 255.0)

# Apply pipeline
result = pipeline.apply(image)

# Get summary
print(pipeline.get_summary())
```

## Examples

See the source code docstrings for more examples.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please submit issues and pull requests on GitHub.

## Author

Your Name - you@example.com
