gunzip GCA_000001405.28_GRCh38.p13_genomic.fna.gz
# FlowMeta: Operations Quick Reference 🌟

> Repository: <https://github.com/SkinMicrobe/FlowMeta>  
> Title: FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline  
> Author: Dongqiang Zeng  
> Email: interlaken@smu.edu.cn

## 1. Overview

FlowMeta consolidates 13 previously separate shell and Python scripts into a single Python package. Through the `flowmeta_base` command you can execute the entire workflow from `fastp → Bowtie2 → Kraken2/Bracken → host filtering → downstream merges`, suitable for microbiome, environmental, soil, or clinical shotgun metagenomic studies.

- Each stage writes `*.task.complete` markers to support resumable execution.
- Optional shared-memory caching accelerates Kraken2 when large databases are involved.
- The `--project_prefix` flag tags Step 6 merged files (for example `SMOOTH-`).

## 2. Environment and installation

```bash
conda activate meta   # Python >= 3.8
pip install flowmeta   # install from PyPI
```

Use [`environment.yml`](environment.yml) to recreate the recommended Conda environment. External executables required on `PATH` include fastp, Bowtie2, samtools, kraken2, bracken, pigz, and seqkit.

## 3. Typical invocation

```bash
flowmeta_base \
    --input_dir /mnt/data/01-raw \
    --output_dir /mnt/data/flowmeta-out \
    --db_bowtie2 /mnt/db/GRCh38_noalt_as/GRCh38_noalt_as \
    --db_kraken /mnt/db/k2ppf \
    --threads 32 \
    --project_prefix SMOOTH-
```

### Output layout

```
01-raw/        Raw FASTQ (read-only)
02-qc/         fastp reports and QC checkpoints
03-hr/         Host-depleted FASTQ
04-bam/        Bowtie2 BAM files and stats
05-host/       Optional host read exports
06-ku/         Kraken2 reports (round one)
07-bracken/    Bracken abundance tables
08-ku2/        Host-filtered rerun outputs
09-mpa/        Final OTU/MPA/summary matrices
```

## 4. Frequently used flags

| Flag | Description |
| --- | --- |
| `--input_dir` | Raw FASTQ directory; expects `_1.fastq.gz` / `_2.fastq.gz` pairs by default. |
| `--output_dir` | Pipeline workspace; automatically creates directories `02-qc` through `09-mpa`. |
| `--db_bowtie2` | Bowtie2 index prefix. |
| `--db_kraken` | Kraken2 database directory containing `hash.k2d`, `opts.k2d`, `taxo.k2d`. |
| `--threads` | Thread count for fastp, Bowtie2, and Kraken2. |
| `--batch` | Number of samples processed concurrently for fastp/Kraken2. |
| `--min_count` | Bracken minimum count threshold for Step 5 host filtering. |
| `--project_prefix` | Prefix applied to Step 6 merged products (e.g. `SMOOTH-`). |
| `--skip_host_extract` | Skip Step 5 host read extraction. |
| `--force` | Force recomputation from the step specified by `--step`. |
| `--no_shm` / `--shm_path` | Control whether the Kraken2 database is copied to shared memory. |

Refer to `docs/tutorial.html` for the complete CLI description and troubleshooting guidance.

## 5. Build the package

```bash
pip install build
python -m build --wheel
ls dist/
```

Wheel artifacts install on any Python ≥ 3.8 interpreter. Run `python -m build --sdist` when preparing a PyPI release so that documentation is bundled with the source distribution.

## 6. Reference databases

### Kraken2

- Download official libraries: <https://benlangmead.github.io/aws-indexes/k2>
- Extract to a location such as `/mnt/db/k2ppf` and point `--db_kraken` to the directory containing `hash.k2d`, `opts.k2d`, and `taxo.k2d`.
- SSD or RAM-disk staging delivers the best throughput for large projects.

### Bowtie2 (human GRCh38 example)

```bash
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.28_GRCh38.p13/GCA_000001405.28_GRCh38.p13_genomic.fna.gz
gunzip GCA_000001405.28_GRCh38.p13_genomic.fna.gz
seqkit grep -rvp "alt|PATCH" GCA_000001405.28_GRCh38.p13_genomic.fna > GRCh38_noalt.fna
mkdir -p /mnt/db/GRCh38_noalt_as
bowtie2-build GRCh38_noalt.fna /mnt/db/GRCh38_noalt_as/GRCh38_noalt_as
flowmeta_base ... --db_bowtie2 /mnt/db/GRCh38_noalt_as/GRCh38_noalt_as
```

## 7. Documentation links

- Primary README: [`README.md`](README.md)
- Detailed HTML tutorial: [`docs/tutorial.html`](docs/tutorial.html)
- Quick validation script: `docs/quickstart.md`

## 8. Contact

For support or collaboration, contact **Dongqiang Zeng** at <interlaken@smu.edu.cn>. The canonical repository is <https://github.com/SkinMicrobe/FlowMeta>.

