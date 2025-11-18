# withoutbg - Python SDK

AI-powered background removal with local and cloud options.

[![PyPI](https://img.shields.io/pypi/v/withoutbg.svg)](https://pypi.org/project/withoutbg/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**[📚 View Complete Documentation →](https://withoutbg.com/documentation/integrations/python-sdk?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)**

## Installation

```bash
# Using uv (recommended)
uv add withoutbg

# Or with pip
pip install withoutbg
```

> **Don't have `uv` yet?** Download it at [astral.sh/uv](https://astral.sh/uv) - it's a fast, modern Python package installer.

## Quick Start

**Choose Your Model:**
- **[See Focus Open Source Results →](https://withoutbg.com/resources/background-removal-results/model-focus-open-source?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)**
- **[See Pro API Results →](https://withoutbg.com/resources/background-removal-results/model-pro-api?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)**
- **[Compare Focus vs Pro →](https://withoutbg.com/resources/compare/focus-vs-pro?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)**

```python
from withoutbg import WithoutBG

# Local processing with Open Source model
model = WithoutBG.opensource()
result = model.remove_background("input.jpg")
result.save("output.png")

# withoutBG Pro for best quality
model = WithoutBG.api(api_key="sk_your_key")
result = model.remove_background("input.jpg")
result.save("output.png")
```

## API Usage

### Single Image Processing

```python
from withoutbg import WithoutBG

# Initialize model once
model = WithoutBG.opensource()

# Process image
result = model.remove_background("photo.jpg")
result.save("photo-withoutbg.png")

# Process with progress callback
def progress(value):
    print(f"Progress: {value * 100:.1f}%")

result = model.remove_background("photo.jpg", progress_callback=progress)
```

### Batch Processing

```python
from withoutbg import WithoutBG

# Initialize model once (efficient!)
model = WithoutBG.opensource()

# Process multiple images - model is reused for all images
images = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
results = model.remove_background_batch(images, output_dir="results/")

# Or process without saving
results = model.remove_background_batch(images)
for i, result in enumerate(results):
    result.save(f"output_{i}.png")
```

### Using withoutBG Pro

```python
from withoutbg import WithoutBG

# Initialize API client
model = WithoutBG.api(api_key="sk_your_key")

# Process images
result = model.remove_background("input.jpg")

# Batch processing with withoutBG Pro
results = model.remove_background_batch(
    ["img1.jpg", "img2.jpg", "img3.jpg"],
    output_dir="api_results/"
)
```

### Advanced: Direct Model Access

```python
from withoutbg import OpenSourceModel, ProAPI

# For advanced users who need direct control
opensource_model = OpenSourceModel()
result = opensource_model.remove_background("input.jpg")

# Or with custom model paths
# Models can be downloaded from: https://huggingface.co/withoutbg/focus
model = OpenSourceModel(
    depth_model_path="/path/to/depth.onnx",
    isnet_model_path="/path/to/isnet.onnx",
    matting_model_path="/path/to/matting.onnx",
    refiner_model_path="/path/to/refiner.onnx"
)

# Direct withoutBG Pro API access
api = ProAPI(api_key="sk_your_key")
result = api.remove_background("input.jpg")
usage = api.get_usage()
```

## CLI Usage

```bash
# Process single image
withoutbg photo.jpg

# Batch processing
withoutbg photos/ --batch --output-dir results/

# Use withoutBG Pro
withoutbg photo.jpg --api-key sk_your_key

# Specify output format
withoutbg photo.jpg --format jpg --quality 90
```

## Features

- ✨ Local processing with Focus v1.0.0 model (free, ~320MB download)
- 🚀 withoutBG Pro for best quality results
- 📦 Batch processing support
- 🎯 Python API and CLI
- 🔧 Flexible output formats (PNG, JPEG, WebP)
- ⚡ Efficient model loading - load once, process many images

## Performance

**Local Model:**
- First run: ~5-10 seconds (~320MB download from HuggingFace)
- CPU: ~2-5 seconds per image
- Memory: ~2GB RAM

**withoutBG Pro:**
- ~1-3 seconds per image (network dependent)
- No local resources needed

## Configuration

### Model Path Environment Variables

By default, models are downloaded from HuggingFace Hub. You can override this by setting environment variables to use local model files:

```bash
export WITHOUTBG_DEPTH_MODEL_PATH=/path/to/depth_anything_v2_vits_slim.onnx
export WITHOUTBG_ISNET_MODEL_PATH=/path/to/isnet.onnx
export WITHOUTBG_MATTING_MODEL_PATH=/path/to/focus_matting_1.0.0.onnx
export WITHOUTBG_REFINER_MODEL_PATH=/path/to/focus_refiner_1.0.0.onnx
```

**Model Files (total ~320MB):**
- ISNet segmentation: 177 MB
- Depth Anything V2: 99 MB
- Focus Matting: 27 MB
- Focus Refiner: 15 MB

This is useful for:
- Offline environments
- CI/CD pipelines
- Custom model versions
- Faster startup times (no download needed)

## Documentation

- **[Python SDK Documentation](https://withoutbg.com/documentation/integrations/python-sdk?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)** - Complete online documentation
- **[Focus Model Results](https://withoutbg.com/resources/background-removal-results/model-focus-open-source?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)** - See example outputs
- **[Pro API Results](https://withoutbg.com/resources/background-removal-results/model-pro-api?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)** - See example outputs
- **[Compare Models](https://withoutbg.com/resources/compare/focus-vs-pro?utm_source=github&utm_medium=withoutbg-readme&utm_campaign=python-package-readme)** - Focus vs Pro comparison
- **[Main Project README](../../README.md)** - Local documentation

## Development

```bash
# Install in development mode (using uv - recommended)
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Format code
black src/ tests/
ruff check src/ tests/
```

## License

Apache License 2.0 - see [LICENSE](../../LICENSE)
