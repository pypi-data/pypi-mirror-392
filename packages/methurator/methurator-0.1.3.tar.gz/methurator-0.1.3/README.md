# 🧬 methurator

[![Python Versions](https://img.shields.io/badge/python-≥3.10%20&%20≤3.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tested with pytest](https://img.shields.io/badge/tested%20with-pytest-blue.svg)](https://pytest.org/)

**methurator** is a Python package designed to estimate **sequencing saturation** for  
**reduced-representation bisulfite sequencing (RRBS)** data.

Although optimized for RRBS, methurator can also be used for whole-genome bisulfite sequencing (WGBS)or other genome-wide methylation data (e.g. **EMseq**). However, for whole-genome methylation data we advise you to use [Preseq](https://smithlabresearch.org/software/preseq/) package.

---

## 🧠 Dependencies and Notes

- methurator uses [SAMtools](https://www.htslib.org/) and [MethylDackel](https://github.com/dpryan79/MethylDackel) internally for BAM subsampling, thus they need to be installed.
- When `--genome` is provided, the corresponding FASTA file will be automatically fetched and cached.
- Temporary intermediate files are deleted by default unless `--keep-temporary-files` is specified.

---

## 📦 Installation

```bash
pip install methurator
```

---

## 🚀 Quick Start

### Step 1 — Downsample BAM files

The `downsample` command performs BAM downsampling according to the specified percentages and coverage.

```bash
methurator downsample --genome hg19 --bam test_data/SRX1631721.markdup.sorted.csorted.bam
```

This command generates two summary files:

- **CpG summary** — number of unique CpGs detected in each downsampled BAM
- **Reads summary** — number of reads in each downsampled BAM

Example outputs can be found in [`tests/data`](tests/data).

---

### Step 2 — Plot the sequencing saturation curve

Use the `plot` command to visualize sequencing saturation:

```bash
methurator plot \
  --cpgs_file tests/data/cpgs_summary.csv \
  --reads_file tests/data/reads_summary.csv
```

---

## ⚙️ Command Reference

### 🧩 `downsample` command

| Argument                            | Description                                                                                                        | Default             |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------- |
| `--bam`                             | Path to a single `.bam` file.                                                                                      | —                   |
| `--bamdir`                          | Directory containing multiple BAM files.                                                                           | —                   |
| `--outdir`                          | Output directory.                                                                                                  | `./output`          |
| `--fasta`                           | Path to the reference genome FASTA file. If not provided, it will be automatically downloaded based on `--genome`. | —                   |
| `--genome`                          | Genome used for alignment. Available: `hg19`, `hg38`, `GRCh37`, `GRCh38`, `mm10`, `mm39`.                          | —                   |
| `--downsampling-percentages`, `-ds` | Comma-separated list of downsampling percentages between 0 and 1 (exclusive).                                      | `0.1,0.25,0.5,0.75` |
| `--minimum-coverage`                | Minimum CpG coverage to consider for saturation. Can be a single integer or a list (e.g. `1,3,5`).                 | `3`                 |
| `--keep-temporary-files`            | If set, temporary files will be kept after analysis.                                                               | `False`             |

---

### 📊 `plot` command

| Argument       | Description                              | Default    |
| -------------- | ---------------------------------------- | ---------- |
| `--cpgs_file`  | Path to the CpG coverage summary file.   |            |
| `--reads_file` | Path to the reads coverage summary file. |            |
| `--outdir`     | Output directory.                        | `./output` |

---

## 📘 Example Workflow

```bash
# Step 1: Downsample BAM file
methurator downsample --genome hg19 --bam my_sample.bam

# Step 2: Plot saturation curve
methurator plot \
  --cpgs_file output/cpgs_summary.csv \
  --reads_file output/reads_summary.csv
```

---

## 🧾 Citation

If you use **methurator** in your research, please cite this repository:

```
Author(s). methurator: A Python package for estimating sequencing saturation in RRBS data.
https://github.com/yourusername/methurator
```

---

## 🪪 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Author

**Edoardo Giuili**
[GitHub](https://github.com/edogiuili) • [Contact](edoardogiuili@gmail.com)
