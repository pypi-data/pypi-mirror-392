# HiC-SCA: Hi-C Spectral Compartment Assignment

A Python package for assigning A-B compartments from Hi-C (chromosome conformation capture) data using spectral decomposition

**Key capabilities:**
- Process .hic files at single or multiple resolutions
- Automatic genome-wide Observed/Expected (O/E) normalization with smoothing
- Eigenvector selection using Inter-AB score, which quantifies A/B compartment assignment confidence
- Cross-resolution evaluation to identify suitable resolutions
- Multiple output formats (HDF5, Excel, BED, BedGraph, plots)

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install from Source](#install-from-source)
  - [Install from PyPI](#install-from-pypi)
  - [Dependencies](#dependencies)
  - [Sample/Test Data](#sample-test-data)
- [Testing](#testing)
- [Quick Start](#quick-start)
  - [Command-Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Command-Line Interface](#command-line-interface-1)
  - [Arguments](#arguments)
  - [Usage Examples](#usage-examples)
  - [Output Files](#output-files)
    - [1. HDF5 Results File (always generated)](#1-hdf5-results-file-always-generated)
    - [2. Excel Files (always generated)](#2-excel-files-always-generated)
    - [3. BED Files (optional, with `--bed`)](#3-bed-files-optional-with---bed)
    - [4. BedGraph Files (optional, with `--bedgraph`)](#4-bedgraph-files-optional-with---bedgraph)
    - [5. Compartment Plots (always generated)](#5-compartment-plots-always-generated)
    - [6. Cross-Resolution MCC Plot (if multiple resolutions)](#6-cross-resolution-mcc-plot-if-multiple-resolutions)
  - [Troubleshooting CLI](#troubleshooting-cli)
- [Python API](#python-api-1)
  - [Core Classes](#core-classes)
    - [HiCSCA - Main Pipeline Class](#hicsca---main-pipeline-class)
  - [Results Dictionary Structure](#results-dictionary-structure)
  - [Evaluation Tools](#evaluation-tools)
    - [CrossResolutionAnalyzer](#crossresolutionanalyzer)
    - [CrossDatasetAnalyzer](#crossdatasetanalyzer)
    - [MCCCalculator](#mcccalculator)
- [Other Documentation](#other-documentation)
- [Citation](#citation)
  - [Dependencies](#dependencies-1)
  - [Sample Data](#sample-data)
- [Acknowledgments](#acknowledgments)
- [License](#license)
- [Contributing](#contributing)

## Installation<a id="installation"></a>
There are two ways to install HiC-SCA: from [source](#install-from-source) or from [PyPI](#install-from-pypi). The main difference is that installing from source includes the [sample/test Hi-C dataset](#sample-test-data).

**Extra instructions for macOS:**

If installing on macOS, you will need Xcode. To check if you have Xcode installed, in Terminal, execute `xcode-select -p`. If it returns an error, you need to install Xcode. There are 3 ways to achieve this:
1. Install Xcode from [Apple Developer](https://developer.apple.com/download/)
2. Install "Command Line Tools" from [Apple Developer](https://developer.apple.com/download/)
3. "Command Line Tools" is installed with brew. Install brew by following the instructions at [brew.sh](https://brew.sh/)

**Extra instructions for Windows 11:**

1. HiC-SCA requires the hic-straw package, which contains C++ code that cannot be compiled by the Microsoft MSVC compiler on Windows. To run HiC-SCA on Windows, use WSL2
2. Instructions for installing WSL 2: https://learn.microsoft.com/en-us/windows/wsl/install

### Install from Source<a id="install-from-source"></a>

1. Check [Miniforge GitHub page](https://github.com/conda-forge/miniforge) for instructions on how to install Miniforge

2. Create a new environment:
```bash
mamba create -n hicsca python git git-lfs cxx-compiler zlib curl
```

3. Activate environment:
```bash
mamba activate hicsca
```

4. Install git-lfs hook:
```bash
git lfs install
```

5. Clone repositories:
```bash
git clone https://github.com/iQLS-MMS/h5typer.git
git clone https://github.com/iQLS-MMS/hic-sca.git
```

6. Install:
```bash
# Install h5typer first (required dependency)
cd h5typer
pip install .

# Install HiC-SCA
cd ../hic-sca
pip install .
```

### Install from PyPI<a id="install-from-pypi"></a>

1. Check [Miniforge GitHub page](https://github.com/conda-forge/miniforge) for instructions on how to install Miniforge

2. Create a new environment:
```bash
mamba create -n hicsca python cxx-compiler zlib curl
```

3. Activate environment:
```bash
mamba activate hicsca
```

4. Install HiC-SCA:
```bash
pip install hic-sca
```

**Note:** The PyPI version doesn't include the .hic sample/test data. To run tests or use the sample data, you need to download [ENCFF216ZNY_Intra_Only.hic](https://github.com/iQLS-MMS/hic-sca/blob/main/tests/test_data/ENCFF216ZNY_Intra_Only.hic) directly from GitHub.

### Requirements<a id="requirements"></a>

- Python >= 3.10
- pip >= 21.0

### Dependencies<a id="dependencies"></a>

The package automatically installs:
- hicstraw >= 1.3.0 (reading .hic files)
- numpy >= 1.19.0 (numerical computations)
- scipy >= 1.15.0 (sparse matrices, eigendecomposition)
- h5py >= 3.0.0 (HDF5 I/O)
- pandas >= 1.0.0 (Excel export)
- openpyxl >= 3.0.0 (Excel I/O)
- matplotlib >= 3.0.0 (plotting)
- h5typer >= 0.1.0 (HDF5 type mapping)

### Sample/Test Data<a id="sample-test-data"></a>

The test .hic dataset contains only the intra-chromosomal contacts of [ENCFF216ZNY](https://www.encodeproject.org/files/ENCFF216ZNY/). This dataset is required for running the test suite or can be used as a sample dataset for trying out HiC-SCA.

**For source installations:**
The file is included at `hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic`

**For PyPI installations:**
Download [ENCFF216ZNY_Intra_Only.hic](https://github.com/iQLS-MMS/hic-sca/blob/main/tests/test_data/ENCFF216ZNY_Intra_Only.hic) directly from GitHub.

## Testing<a id="testing"></a>

To run the test suite, you must install HiC-SCA from source with test dependencies:

```bash
# Install from source
pip install ".[tests]"
```

Then run the tests from the hic-sca folder with:
```bash
pytest tests/
```

## Quick Start<a id="quick-start"></a>

### Command-Line Interface<a id="command-line-interface"></a>

The easiest way to use HiC-SCA is through the command-line interface:

```bash
# Process single resolution
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample

# Process with BED and BedGraph output
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample --bed --bedgraph

# Process multiple resolutions
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 50000 25000 -p my_sample

# Process all available resolutions with verbose output
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -p my_sample -v

# Specify output directory
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample -o results/

# Process specific chromosomes
# WARNING: The background distribution used to compute the O/E Hi-C
#          contact maps will only include the specific chromosomes
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -c chr1 chr2 chr3 -p my_sample
```

**Output files:**
- `my_sample_results.h5` - HDF5 file with complete results
- `my_sample_100000bp.xlsx` - Excel file (mandatory)
- `my_sample_100000bp.bed` - BED file (if `--bed` specified) 
- `my_sample_100000bp.bedgraph` - BedGraph file (if `--bedgraph` specified)
- `my_sample_chr1_100000bp.png` - Compartment plot for chr1
- `my_sample_cross_resolution_mcc.png` - Cross-resolution MCC heatmap (if multiple resolutions)

The BED and bedGraph output files can be visualized on the [UCSC Genome Browser](https://genome.ucsc.edu/) as Custom Tracks. Ensure the correct genome assembly is selected (the sample data uses human GRCh38/hg38).

### Python API<a id="python-api"></a>

```python
from hicsca import HiCSCA

# Initialize pipeline with Hi-C file
hicsca = HiCSCA(
    hic_file_path="hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic",
    resolutions=[100000],  # or None for auto-detect all
    chr_names=None  # None = all autosomal chromosomes
)

# Process all chromosomes
hicsca.process_all_chromosomes(verbose=True)

# Access results
result = hicsca.results[100000]['chr1']
if result['Success']:
    compartment = result['assigned_AB_compartment']
    eig_idx = result['selected_eig_idx']
    score = result['modified_inter_eigval_score']
    print(f"chr1: Selected Eig{eig_idx}, Score: {score:.4f}")

# Export results using convenience methods
hicsca.to_bed(100000, "compartments_100kb.bed")
hicsca.to_bedgraph(100000, "compartments_100kb.bedgraph")
hicsca.to_excel(100000, "compartments_100kb.xlsx")
hicsca.to_hdf5("saved_analysis.h5")

# Plot compartments (saves to files)
hicsca.plot_compartments(100000, output_dir="plots", output_prefix="sample")

# Plot cross-resolution MCC correlation
hicsca.plot_cross_resolution_mcc(save_path="cross_res_mcc.png")
```

## Command-Line Interface<a id="command-line-interface-1"></a>

### Arguments<a id="arguments"></a>

**Required (one of):**
- `-f, --hic-file PATH` - Path to input .hic file
- `--load-hdf5 PATH` - Load existing HDF5 results file

**Optional:**
- `-r, --resolutions BP [BP ...]` - Space-separated resolutions in bp (default: auto-detect all)
- `-p, --output-prefix PREFIX` - Prefix for output files (required)
- `-o, --output-dir DIR` - Output directory (default: current directory)
- `-c, --chromosomes CHR [CHR ...]` - Space-separated chromosome names (default: chr1-chr22)
- `-t, --data-type TYPE` - Data type: "observed" or "oe" (default: "observed")
- `-v, --verbose` - Enable verbose output
- `--bed` - Generate BED files for each resolution
- `--bedgraph` - Generate BedGraph files for each resolution

### Usage Examples<a id="usage-examples"></a>

```bash
# Basic usage
hic-sca -f data.hic -r 100000 -p my_sample

# With BED and BedGraph output
hic-sca -f data.hic -r 100000 -p my_sample --bed --bedgraph

# Multiple resolutions
hic-sca -f data.hic -r 500000 250000 100000 50000 -p my_sample

# All available resolutions
hic-sca -f data.hic -p my_sample -v

# Custom output directory
hic-sca -f data.hic -r 100000 -p my_sample -o results/

# Specific chromosomes
hic-sca -f data.hic -r 100000 -c chr1 chr2 chr3 -p my_sample

# Use pre-normalized O/E data from the .hic file (skip background normalization)
hic-sca -f data.hic -r 100000 -p my_sample -t oe

# Load existing HDF5 and export to BED/BedGraph
hic-sca --load-hdf5 results.h5 -p output --bed --bedgraph

# Load HDF5 with .hic file (enables processing additional data)
hic-sca --load-hdf5 results.h5 -f data.hic -p output

# Load HDF5 and export filtered data (specific resolutions/chromosomes)
hic-sca --load-hdf5 results.h5 -r 100000 -c chr1 chr2 -p output --bed
```

### Output Files<a id="output-files"></a>

The CLI generates the following output files:

#### 1. HDF5 Results File (always generated)<a id="1-hdf5-results-file-always-generated"></a>
**Filename:** `{prefix}_results.h5`

Complete analysis results for all resolutions and chromosomes:
- All compartment predictions
- Pre-computed background normalizations (for fast reloading)
- Eigendecomposition results
- Inter-AB score
- Self-contained: stores chromosome lengths, no .hic file path stored
- Can be loaded with or without .hic file for export or further processing

**Loading HDF5 files:**
```python
from hicsca import HiCSCA

# Load for export only
hicsca = HiCSCA.from_hdf5("results.h5")
hicsca.to_bed(100000, "compartments.bed")

# Load with .hic file to enable processing additional data
hicsca = HiCSCA.from_hdf5("results.h5", hic_file_path="data.hic")
hicsca.process_chromosome("chr1")  # Can process more chromosomes
```

#### 2. Excel Files (always generated)<a id="2-excel-files-always-generated"></a>
**Filename:** `{prefix}_{resolution}bp.xlsx`

One file per resolution with:
- **Per-chromosome worksheets** containing:
  - `Start`: Bin start position (1-indexed, in bp)
  - `End`: Bin end position (in bp)
  - `Value`: Compartment eigenvector value
  - `Compartment`: "A" (positive values), "B" (negative values), or "" (excluded bins)
- **Summary worksheet "Inter-AB Scores"** containing:
  - `Chromosome`: Chromosome name
  - `Inter-AB Score`: Quality metric (numeric value or "N/A" if processing failed)
  - `Confidence`: "High" if 1.75 ≤ score ≤ 3.20, else "Low"

#### 3. BED Files (optional, with `--bed`)<a id="3-bed-files-optional-with---bed"></a>
**Filename:** `{prefix}_{resolution}bp.bed`

BED9 format with RGB colors:
- Consecutive bins of same compartment are merged
- A compartments: red (255,0,0)
- B compartments: blue (0,0,255)
- Zero values (excluded regions) are skipped
- Track header included for genome browser compatibility

**Format:**
```
track name=AB_Compartments_100000bp description="..." itemRgb="On"
chr1    0       300000  A   0   .   0       300000  255,0,0
chr1    400000  800000  B   0   .   400000  800000  0,0,255
```

#### 4. BedGraph Files (optional, with `--bedgraph`)<a id="4-bedgraph-files-optional-with---bedgraph"></a>
**Filename:** `{prefix}_{resolution}bp.bedgraph`

Continuous compartment scores for genome browser visualization:
- One value per bin (not merged)
- Zero values (excluded regions) are skipped
- Track header included

**Format:**
```
track type=bedGraph name="AB_Compartments_100000bp"
chr1    0       100000  0.123456
chr1    100000  200000  -0.098765
```

#### 5. Compartment Plots (always generated)<a id="5-compartment-plots-always-generated"></a>
**Filename:** `{prefix}_{chr_name}_{resolution}bp.png`

Publication-quality plots (300 DPI) for each chromosome:
- Red line: A compartment (positive values)
- Blue line: B compartment (negative values)

#### 6. Cross-Resolution MCC Plot (if multiple resolutions)<a id="6-cross-resolution-mcc-plot-if-multiple-resolutions"></a>
**Filename:** `{prefix}_cross_resolution_mcc.png` and `{prefix}_cross_resolution_mcc_colorbar.png`

Heatmap showing Matthews Correlation Coefficient between resolutions:
- Assesses consistency across different resolutions
- Main heatmap and separate colorbar figure
- Gray cells indicate incompatible resolution pairs (not round multiples)
- Red-white-blue colormap for MCC values (0-1)

### Troubleshooting CLI<a id="troubleshooting-cli"></a>

**"Error: Must provide either --load-hdf5 or -f/--hic-file"**
- Provide at least one input source: `-f` for new .hic file, or `--load-hdf5` for existing results

**"Error: Hi-C file not found"**
- Verify path to .hic file
- Use absolute paths if relative paths cause issues

**"Error: HDF5 file not found"**
- Verify path to HDF5 results file
- Ensure correct file name with `.h5` extension

**"No resolutions available"**
- Check that .hic file contains data at specified resolutions
- Use auto-detection (omit `-r` flag) to see available resolutions

**Memory errors**
- Process fewer resolutions at once
- Use higher resolutions (e.g., 100kb instead of 10kb)
- Close other applications to free up RAM

## Python API<a id="python-api-1"></a>

### Core Classes<a id="core-classes"></a>

#### HiCSCA - Main Pipeline Class<a id="hicsca---main-pipeline-class"></a>

Complete pipeline for A-B compartment prediction from Hi-C data.

**Initialization:**
```python
from hicsca import HiCSCA

hicsca = HiCSCA(
    hic_file_path="data/sample.hic",
    chr_names=None,  # None = all autosomal chromosomes
    resolutions=None,  # None = all available resolutions
    data_type="observed",  # "observed" or "oe"
    norm_type="NONE",
    smoothing_cutoff=400
)
```

**Parameters:**
- `hic_file_path` (str): Path to .hic file
- `chr_names` (list or None): Chromosome names to process (default: all autosomal)
- `resolutions` (list or None): Resolutions in bp (default: auto-detect all)
- `data_type` (str): "observed" (raw contacts with O/E normalization) or "oe" (pre-normalized, skip O/E)
- `norm_type` (str): Normalization type for hicstraw (default: "NONE")
- `smoothing_cutoff` (int): Smoothing parameter for O/E normalization (default: 400, only used when data_type="observed")

**Key Methods:**
```python
# Compute background normalization (automatic when processing, can be called explicitly)
hicsca.compute_background_normalization(resolutions=None)

# Process single chromosome at specified resolutions
hicsca.process_chromosome(chr_name, resolutions=None, verbose=True)

# Process all chromosomes at specified resolutions
hicsca.process_all_chromosomes(resolutions=None, verbose=True)

# Load saved HiCSCA instance
hicsca = HiCSCA.from_hdf5(hdf5_path, hic_file_path=None)
```

**Export Methods:**
```python
# Save complete instance to HDF5
hicsca.to_hdf5(output_path, update=False)

# Generate BED file
hicsca.to_bed(resolution, output_path, chr_names=None, dataset_id=None)

# Generate BedGraph file
hicsca.to_bedgraph(resolution, output_path, chr_names=None, dataset_id=None, track_name=None)

# Generate Excel file
hicsca.to_excel(resolution, output_path, chr_names=None, dataset_id=None)

# Plot compartments (saves to files and/or displays in Jupyter)
hicsca.plot_compartments(
    resolution,
    chr_names=None,
    output_dir=None,  # Specify to save files
    output_prefix=None,
    display=True,  # Set False to disable Jupyter display
    dpi=300,
    figsize=(3.595, 2)
)

# Plot cross-resolution MCC correlation heatmap
hicsca.plot_cross_resolution_mcc(
    chr_name='all',  # 'all' or specific chromosome
    resolutions=None,  # None = all resolutions
    chr_names=None,  # For genome-wide ('all') calculation
    figsize=(2.8, 2.8),
    dpi=300,
    background_alpha=1,  # 0=transparent, 1=opaque
    plot_colorbar=True,  # Generate separate colorbar figure
    save_path=None  # Path to save main figure
)
```

**Usage:**
```python
# Example 1: Using observed data (default - with O/E normalization)
hicsca = HiCSCA(
    "data/sample.hic",
    resolutions=[100000, 50000],
    data_type="observed",
    norm_type="NONE"
)

# Process all chromosomes (results stored in hicsca.results)
hicsca.process_all_chromosomes(verbose=True)

# Access results
result = hicsca.results[100000]["chr1"]
if result['Success']:
    compartment = result['assigned_AB_compartment']
    eig_idx = result['selected_eig_idx']
    score = result['modified_inter_eigval_score']

# Export results
hicsca.to_bed(100000, "compartments_100kb.bed")
hicsca.to_excel(100000, "compartments_100kb.xlsx")
hicsca.to_hdf5("saved_analysis.h5")

# Example 2: Using pre-normalized O/E data (skips background normalization)
hicsca_oe = HiCSCA(
    "data/sample.hic",
    resolutions=[100000],
    data_type="oe",  # Data already O/E normalized
    norm_type="KR"   # Can use normalized data if available
)
hicsca_oe.process_all_chromosomes(verbose=True)

# Example 3: Load previously saved HiCSCA instance
hicsca_loaded = HiCSCA.from_hdf5("saved_analysis.h5")
# All results and normalizations already loaded - no processing needed
result = hicsca_loaded.results[100000]['chr1']
```

### Results Dictionary Structure<a id="results-dictionary-structure"></a>

Results are stored in: `hicsca.results[resolution][chr_name]`

Each result dictionary contains:

**Core Fields (always present):**
- `Success` (bool): Whether processing succeeded
- `Eig Converged` (bool): Whether eigendecomposition converged

**Compartment Prediction (when Success=True):**
- `assigned_AB_compartment` (ndarray): Normalized compartment eigenvector (positive=A, negative=B, zero=excluded)
- `selected_eig_idx` (int): Index of selected eigenvector (1-10)
- `modified_inter_eigval_score` (float): Eigenvalue-weighted eigenvector selection score
- `unmodified_inter_AB_score` (float): Raw inter-compartment contact score

**Eigendecomposition Results:**
- `eigvals` (ndarray): All eigenvalues (11 values: trivial + 10 non-trivial)
- `eigenvects` (ndarray): All eigenvectors (11 × N matrix, row-major format)

**Quality Control:**
- `cutoff` (float): Low-coverage filter cutoff value
- `include_bool` (ndarray): Boolean array indicating bins included in analysis
- `non_zero_not_included_bool` (ndarray): Boolean array for excluded non-zero bins
- `deg` (ndarray): Degree (column sums) of filtered O/E matrix
- `OE_normed_diag` (ndarray): Diagonal of O/E matrix for included bins

**See RESULTS_STRUCTURE.md for complete documentation.**

### Evaluation Tools<a id="evaluation-tools"></a>

#### CrossResolutionAnalyzer<a id="crossresolutionanalyzer"></a>

Analyzes agreement between different resolutions within the same Hi-C dataset.

```python
from hicsca.evals import CrossResolutionAnalyzer

# Initialize with HiCSCA results (auto-detects resolutions and chromosomes)
analyzer = CrossResolutionAnalyzer(hicsca.results)

# Or specify custom resolutions/chromosomes
analyzer = CrossResolutionAnalyzer(
    hicsca.results,
    resolutions=[500000, 250000, 100000, 50000],
    chr_names=['chr1', 'chr2', ..., 'chr22']
)

# Analyze (results stored internally, cached)
analyzer.analyze()

# Plot genome-wide cross-resolution MCC with colorbar
fig, ax, cbar_fig, cbar_ax = analyzer.plot_cross_resolution_mcc()

# Plot specific chromosome with transparent background
fig, ax, cbar_fig, cbar_ax = analyzer.plot_cross_resolution_mcc(
    chr_name='chr1',
    save_path='chr1_mcc.png',
    background_alpha=0
)
# Saves: chr1_mcc.png and chr1_mcc_colorbar.png

# Access MCC matrices directly
genome_wide_mcc = analyzer.mcc_matrices['all']
chr1_mcc = analyzer.mcc_matrices['chr1']
```

#### CrossDatasetAnalyzer<a id="crossdatasetanalyzer"></a>

Analyzes agreement between different Hi-C datasets at the same resolution(s).

```python
from hicsca.evals import CrossDatasetAnalyzer

# Create dataset dictionary (dataset_id -> HiCSCA results)
dataset_dict = {
    'dataset1': hicsca_inst1.results,
    'dataset2': hicsca_inst2.results,
    'dataset3': hicsca_inst3.results
}

# Initialize (auto-detects resolutions, dataset_ids, and chromosomes)
analyzer = CrossDatasetAnalyzer(dataset_dict)

# Analyze all resolutions
analyzer.analyze()

# Plot genome-wide MCC correlation at 100kb with colorbar
fig1, ax1, cbar_fig1, cbar_ax1 = analyzer.plot_mcc_correlation(
    100000,
    tick_labels=['A', 'B', 'C'],
    save_path='mcc_100kb.png'
)
# Saves: mcc_100kb.png and mcc_100kb_colorbar.png

# Plot chr1 orientation agreement
fig2, ax2, cbar_fig2, cbar_ax2 = analyzer.plot_orientation_agreement(
    100000,
    chr_name='chr1',
    save_path='orient_chr1_100kb.png'
)

# Access matrices directly
mcc_genome_wide = analyzer.mcc_matrices[100000]['all']
```

#### MCCCalculator<a id="mcccalculator"></a>

Compute Matthews Correlation Coefficient between compartment predictions.

```python
from hicsca.evals import MCCCalculator

mcc, tp, fp, tn, fn, zeroed, reversed = MCCCalculator.compute_AB_MCC(
    reference_compartments,
    predicted_compartments,
    auto_flip=True  # Automatically handle orientation
)

print(f"MCC: {mcc:.4f}")
```

## Other Documentation<a id="other-documentation"></a>

- **[RESULTS_STRUCTURE.md](RESULTS_STRUCTURE.md)**: Complete documentation of results dictionary structure

## Citation<a id="citation"></a>

If you use this software in your research, please cite:

Chan, J. & Kono, H. HiC-SCA: A Spectral Clustering Method for Reliable A/B Compartment Assignment From Hi-C Data. *Preprint* at https://doi.org/10.1101/2025.09.22.677711 (2025).

### Dependencies<a id="dependencies-1"></a>

Our package uses [hicstraw](https://github.com/aidenlab/straw):

Durand, N.C., Robinson, J.T., Shamim, M.S., Machol, I., Mesirov, J.P., Lander, E.S., and Aiden, E.L. (2016). Juicebox Provides a Visualization System for Hi-C Contact Maps with Unlimited Zoom. *Cell Systems* 3, 99–101. https://doi.org/10.1016/j.cels.2015.07.012.

LOBPCG algorithm (SciPy) for efficient eigen-decomposition:

Knyazev, A.V., Argentati, M.E., Lashuk, I., and Ovtchinnikov, E.E. (2007). Block Locally Optimal Preconditioned Eigenvalue Xolvers (BLOPEX) in hypre and PETSc. https://doi.org/10.48550/ARXIV.0705.2626.

### Sample Data<a id="sample-data"></a>

Sample data from:

Rao, S.S.P., Huntley, M.H., Durand, N.C., Stamenova, E.K., Bochkov, I.D., Robinson, J.T., Sanborn, A.L., Machol, I., Omer, A.D., Lander, E.S., et al. (2014). A 3D Map of the Human Genome at Kilobase Resolution Reveals Principles of Chromatin Looping. *Cell* 159, 1665–1680. https://doi.org/10.1016/j.cell.2014.11.021.

Obtained from the [ENCODE database](https://www.encodeproject.org/):

Luo, Y., Hitz, B.C., Gabdank, I., Hilton, J.A., Kagda, M.S., Lam, B., Myers, Z., Sud, P., Jou, J., Lin, K., et al. (2020). New developments on the Encyclopedia of DNA Elements (ENCODE) data portal. *Nucleic Acids Research* 48, D882–D889. https://doi.org/10.1093/nar/gkz1062.

## Acknowledgments<a id="acknowledgments"></a>

This package uses:
- [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/) for numerical computations and sparse matrix operations
- [matplotlib](https://matplotlib.org/) for visualization
- [h5py](https://www.h5py.org/) for HDF5 file I/O

## License<a id="license"></a>

MIT License

## Contributing<a id="contributing"></a>

Contributions are welcome! Please feel free to submit a Pull Request.

