# WSI-Toolbox Codebase Exploration

## Project Overview
WSI-Toolbox is a comprehensive toolkit for processing Whole Slide Image (WSI) data. It:
- Converts WSI files to HDF5 format with patch splitting
- Extracts patch embeddings using foundation models (GigaPath, UNI, Virchow2)
- Performs clustering and sub-clustering analysis
- Generates preview visualizations

## Main CLI Structure

### Entry Point
- **File**: `/home/ken/src/github.com/endaaman/WSI-toolbox/wsi_toolbox/cli.py`
- **Main Class**: `CLI(BaseMLCLI)` (extends pydantic-autocli)
- **Invocation**: `python -m wsi_toolbox.cli` or via `uv run cli`

### CLI Design Pattern
Uses **pydantic-autocli** with method-based subcommands:
- Each `run_*` method becomes a subcommand (e.g., `run_wsi2h5` → `wsi2h5`)
- Each `*Args` class defines arguments for corresponding command
- `CommonArgs` includes shared arguments (device, seed)
- Arguments use `param()` for configuration (short/long flags, defaults)

### Available Subcommands

1. **wsi2h5** - Convert WSI to HDF5 with patches
   - Args: input_path, output_path, patch_size (256), engine (auto/openslide/tifffile), mpp, rotate
   - Uses: WSIProcessor.convert_to_hdf5()

2. **process-patches** - Extract patch embeddings
   - Args: input_path, batch_size (512), model_name (gigapath/uni), with_latent_features, overwrite
   - Uses: TileProcessor.evaluate_hdf5_file()

3. **process-slide** - Extract slide-level features (GigaPath LongNet)
   - Args: input_path, device, overwrite
   - Uses: GigaPath slide_encoder

4. **cluster** - Leiden clustering with UMAP visualization
   - Args: input_paths, cluster_name, sub (sub-cluster filter), model, resolution, use_umap_embs, overwrite
   - Uses: ClusterProcessor.anlyze_clusters()

5. **cluster-scores** - Generate PCA-based scores for cluster subsets
   - Args: input_path, name, clusters, model, scaler (minmax/std)
   - Saves scores to HDF5 under `{model}/scores_{name}`

6. **cluster-latent** - Cluster latent features from patches
   - Args: input_path, name, model, resolution
   - Uses: leiden_cluster() on latent features

7. **preview** - Generate cluster thumbnail visualization
   - Args: input_path, output_path, model, cluster_name, size (64), open
   - Uses: PreviewClustersProcessor

8. **preview-scores** - Generate score heatmap thumbnail
   - Args: input_path, model, score_name, size
   - Uses: PreviewScoresProcessor

9. **preview-latent-pca** - Visualize latent features with PCA coloring
   - Uses: PreviewLatentPCAProcessor

10. **preview-latent** - Visualize latent cluster assignments
    - Uses: PreviewLatentClusterProcessor

## Processor Classes

### File: `/home/ken/src/github.com/endaaman/WSI-toolbox/wsi_toolbox/processor.py`

#### WSI File Abstractions
- **WSIFile** (base): Abstract interface for WSI access
- **TiffFile**: TIFF-based WSI (using tifffile + zarr)
- **OpenSlideFile**: OpenSlide-based WSI (SVS, VMS, NDPI, etc.)
- **StandardImage**: Standard image files (JPG, PNG)

**Key Methods**:
- `get_mpp()`: Get microns per pixel resolution
- `get_original_size()`: Get full resolution dimensions
- `read_region(xywh)`: Read rectangular region as RGB numpy array

#### WSIProcessor
**Purpose**: Converts WSI to HDF5 with patch extraction

**Key Methods**:
- `__init__(image_path, engine='auto', mpp=0)`: Auto-detect engine based on file extension
- `convert_to_hdf5(hdf5_path, patch_size=256, rotate=False, progress='tqdm')`

**Process**:
1. Reads WSI metadata (size, mpp)
2. Auto-scales patches to standardized mpp (0.36-0.50)
3. Extracts patches, filters white patches
4. Stores in HDF5 with coordinates and metadata

**HDF5 Structure Created**:
```
patches: (patch_count, size, size, 3) - uint8
coordinates: (patch_count, 2) - pixel coordinates
metadata/original_mpp
metadata/original_width, height
metadata/image_level
metadata/mpp, scale, patch_size
metadata/patch_count, cols, rows
```

#### TileProcessor
**Purpose**: Extracts embeddings from patches using foundation models

**Methods**:
- `__init__(model_name='uni', device='cuda')`
- `evaluate_hdf5_file(hdf5_path, batch_size=256, with_latent_features=False, overwrite=False)`

**Features**:
- Supports: UNI, GigaPath, Virchow2
- Can extract both CLS token features and latent patch features
- Processes in batches with progress tracking
- Handles normalization (ImageNet mean/std)
- Uses mixed precision (float16) for efficiency

**Saves**:
- `{model}/features`: CLS embeddings (batch, emb_size)
- `{model}/latent_features`: Patch tokens (batch, latent_size², emb_size) [optional]

#### ClusterProcessor
**Purpose**: Performs clustering on embeddings across one or more HDF5 files

**Methods**:
- `__init__(hdf5_paths, model_name, cluster_name='', cluster_filter=None)`
- `anlyze_clusters(resolution=1.0, use_umap_embs=False, overwrite=False)`
- `plot_umap(fig_path=None)`: Visualize with UMAP

**Features**:
- Supports multi-file clustering with merged embeddings
- Sub-clustering: Can filter clusters and re-cluster subsets
- Leiden algorithm for community detection
- StandardScaler preprocessing
- UMAP for 2D visualization

**Saves**:
- `{model}/clusters`: Cluster assignments per patch

#### Preview Processors (BasePreviewProcessor subclasses)

**BasePreviewProcessor**: Abstract base for thumbnail generation
- Loads patch data and renders with overlays
- Creates full-resolution (cols*size × rows*size) thumbnail

**PreviewClustersProcessor**:
- Overlays colored frames with cluster numbers
- Uses tab20 colormap

**PreviewScoresProcessor**:
- Colors patches by score values using viridis colormap
- Displays score values as text

**PreviewLatentPCAProcessor**:
- PCA reduces latent features to 3 RGB channels
- Overlays PCA visualization on patches

**PreviewLatentClusterProcessor**:
- Colors latent patch tokens by cluster assignment
- Uses tab20 colormap for discrete clusters

## Key Utilities

### File: `/home/ken/src/github.com/endaaman/WSI-toolbox/wsi_toolbox/utils/cli.py`
- **BaseMLArgs**: Base Pydantic model with `seed` field
- **BaseMLCLI(AutoCLI)**: Extended CLI with seed setting before command execution

### File: `/home/ken/src/github.com/endaaman/WSI-toolbox/wsi_toolbox/common.py`
- **create_model()**: Factory for loading foundation models (UNI, GigaPath, Virchow2)
- **DEFAULT_MODEL**: Loaded from `DEFAULT_MODEL` env var, defaults to 'uni'
- Model configs for each backend (dimensions, initialization)

### Utility Functions (processor.py)
- **is_white_patch()**: Filters out white/background patches
- **cosine_distance()**: Distance metric
- **safe_del()**: Safe HDF5 deletion

## HDF5 Data Organization

The HDF5 structure supports multiple models and analysis types:

```
/patches                    - Raw patch images
/coordinates                - Patch pixel coordinates
/metadata/                  - Image and processing metadata
/{model}/features           - CLS embeddings
/{model}/latent_features    - Patch-level embeddings
/{model}/clusters           - Leiden clustering results
/{model}/latent_clusters    - Clustering of latent features
/{model}/scores_{name}      - Score values per patch
```

Where `{model}` is: `gigapath`, `uni`, or `virchow2`

## Development Standards

From CLAUDE.md:
- Always use `uv` for package management
- CLI uses pydantic-autocli for subcommand structure
- Pattern: `def run_foo_bar(self, args)` → `python script.py foo-bar`
- Return `True`/`None` for success, `False` for failure, `int` for exit codes
