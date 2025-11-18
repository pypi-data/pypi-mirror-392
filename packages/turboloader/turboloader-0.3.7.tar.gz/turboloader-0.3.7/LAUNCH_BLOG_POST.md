# Introducing TurboLoader: High-Performance Data Loading for Deep Learning

We're excited to announce TurboLoader v0.3, a high-performance data loading library designed to eliminate the data loading bottleneck in deep learning training pipelines.

## The Problem

Modern deep learning models are GPU-hungry. While GPUs have become incredibly powerful, data loading often can't keep up. Traditional dataloaders frequently leave GPUs idle, waiting for the next batch of training data. This is especially problematic when working with:

- Large datasets stored in TAR archives (WebDataset format)
- High-resolution images requiring on-the-fly decoding and transformations
- Distributed training across multiple GPUs
- Remote data stored in S3 or other cloud storage

## The Solution

TurboLoader is built from the ground up in C++ with performance as the top priority:

### Key Features

**Memory-Mapped I/O**: Zero-copy file reading using mmap for minimal overhead

**SIMD-Accelerated Transforms**: Vectorized image processing using AVX2/NEON instructions

**Concurrent JPEG Decoding**: Multi-threaded image decoding with libjpeg-turbo

**Lock-Free Queues**: High-throughput concurrent data structures for minimal synchronization overhead

**WebDataset Support**: First-class support for the popular WebDataset TAR format

**PyTorch Integration**: Drop-in replacement for PyTorch DataLoader with familiar API

## Performance

TurboLoader delivers significant speedups over traditional dataloaders:

- **SIMD Transforms**: 6700+ img/s for resize operations, 47000+ img/s for normalization
- **Concurrent Processing**: Efficient scaling with 4-8 worker threads
- **Minimal Overhead**: C++ implementation eliminates Python GIL bottlenecks

## Getting Started

Install via pip:

```bash
pip install turboloader
```

Basic usage:

```python
import turboloader

# Create pipeline
pipeline = turboloader.Pipeline(
    tar_paths=["dataset.tar"],
    num_workers=4,
    decode_jpeg=True,
    queue_size=128
)

# Start loading
pipeline.start()

# Get batches
for epoch in range(num_epochs):
    while True:
        batch = pipeline.next_batch(32)
        if len(batch) == 0:
            break
        # Train your model...
    pipeline.reset()
```

## What's New in v0.3.7

This release focuses on stability and concurrency:

- Fixed all race conditions for reliable high-concurrency operation
- Added mutex-protected TAR reader access
- Replaced lock-free queue with ThreadSafeQueue for complex objects
- Verified stability with 8 workers using ThreadSanitizer
- Enhanced thread synchronization throughout

## Roadmap

We're actively working on:

- Multi-format support (PNG, WebP, video)
- Distributed training optimizations
- Advanced augmentation transforms
- S3 and HTTP data source support
- GPU-accelerated JPEG decoding

## Try It Today

TurboLoader is open source under the MIT license. We welcome contributions, feedback, and bug reports!

- **GitHub**: https://github.com/ALJainProjects/TurboLoader
- **Documentation**: https://github.com/ALJainProjects/TurboLoader/tree/main/docs
- **PyPI**: https://pypi.org/project/turboloader/

Let's eliminate the data loading bottleneck together!
