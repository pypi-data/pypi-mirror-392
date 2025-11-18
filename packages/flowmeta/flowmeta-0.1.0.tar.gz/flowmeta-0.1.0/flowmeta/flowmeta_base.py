"""Main orchestration function for the flowmeta metagenomic pipeline."""

import os
import shutil
import subprocess
from pathlib import Path
from .utils import log_info, log_success, log_warning, log_error, print_colorful_message
from .steps import (
    run_fastp_qc,
    check_fastp_results,
    run_remove_host,
    check_host_remove_results,
    run_extract_host,
    run_kraken_bracken,
    check_kraken_results,
    run_remove_host_counts,
)
from .steps import run_merge_step, STEP6_IMPORT_ERROR

DEFAULT_SUFFIX1 = "_1.fastq.gz"
DEFAULT_SUFFIX2 = "_2.fastq.gz"


class FlowMetaError(RuntimeError):
    """Raised when an unrecoverable error occurs in the pipeline."""


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def verify_fastq_naming(input_dir, suffix1, suffix2):
    """Ensure FASTQ files follow the expected naming convention."""
    files = list(Path(input_dir).glob("*.fastq.gz"))
    if not files:
        raise FlowMetaError(f"No FASTQ files found in {input_dir}")

    invalid = []
    for fp in files:
        name = fp.name
        if name.endswith(suffix1) or name.endswith(suffix2):
            continue
        invalid.append(name)

    if invalid:
        raise FlowMetaError(
            "Found FASTQ files not matching suffix requirements: " + ", ".join(invalid)
        )

    summarize_step(
        "Filename normalization",
        f"All FASTQ files match suffixes {suffix1}/{suffix2}",
        True,
    )


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def load_kraken_db_to_shm(db_path, shm_path="/dev/shm/k2ppf"):
    """Copy the Kraken2 database into shared memory if not present."""
    required = ["hash.k2d", "opts.k2d", "taxo.k2d"]
    db_files = [os.path.join(db_path, f) for f in required]
    if not all(os.path.exists(f) for f in db_files):
        raise FlowMetaError(f"Kraken2 database incomplete at {db_path}")

    if all(os.path.exists(os.path.join(shm_path, f)) for f in required):
        log_info(f"Kraken2 DB already cached in {shm_path}")
        return shm_path

    log_info(f"Copying Kraken2 DB to {shm_path} for faster access")
    if os.path.exists(shm_path):
        shutil.rmtree(shm_path)
    shutil.copytree(db_path, shm_path)

    vmtouch = shutil.which("vmtouch")
    if vmtouch:
        try:
            subprocess.run([vmtouch, "-t", os.path.join(shm_path, "*.k2d")], check=False)
        except Exception:  # best effort
            log_warning("vmtouch preload failed; continuing without preload")
    else:
        log_warning("vmtouch not found; skipping shared-memory preload")
    return shm_path


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def cleanup_kraken_db(shm_path="/dev/shm/k2ppf"):
    if os.path.exists(shm_path):
        log_info(f"Removing shared-memory DB at {shm_path}")
        shutil.rmtree(shm_path, ignore_errors=True)


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def summarize_step(name, description, result):
    status = "✅" if result else "⚠️"
    log_info(f"{status} {name}: {description}")


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Repository: https://github.com/SkinMicrobe/FlowMeta
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def flowmeta_base(
    input_dir,
    output_dir,
    db_bowtie2,
    db_kraken,
    threads=32,
    batch_size=2,
    se=False,
    fastp_length_required=50,
    fastp_retries=3,
    host_retries=3,
    kraken_retries=3,
    copy_db_to_shm=True,
    shm_path="/dev/shm/k2ppf",
    min_count=4,
    suffix1=DEFAULT_SUFFIX1,
    suffix2=DEFAULT_SUFFIX2,
    skip_host_extract=False,
    force=False,
    project_prefix="",
):
    """Run the full 13-step pipeline end-to-end."""
    print_colorful_message("###############################################", "blue")
    print_colorful_message(" flowmeta: Integrated Metagenomic Workflow ", "cyan")
    print_colorful_message("###############################################", "blue")

    if not os.path.isdir(input_dir):
        raise FlowMetaError(f"Input directory not found: {input_dir}")

    output_dir = ensure_dir(output_dir)
    helper_path = os.path.join(os.path.dirname(__file__), "helper")

    verify_fastq_naming(input_dir, suffix1, suffix2)

    paths = {
        "raw": input_dir,
        "qc": ensure_dir(os.path.join(output_dir, "02-qc")),
        "hr": ensure_dir(os.path.join(output_dir, "03-hr")),
        "bam": ensure_dir(os.path.join(output_dir, "04-bam")),
        "host": ensure_dir(os.path.join(output_dir, "05-host")),
        "kraken": ensure_dir(os.path.join(output_dir, "06-ku")),
        "bracken": ensure_dir(os.path.join(output_dir, "07-bracken")),
        "kraken_filtered": ensure_dir(os.path.join(output_dir, "08-ku2")),
        "mpa": ensure_dir(os.path.join(output_dir, "09-mpa")),
    }

    # Step 1 & 2: fastp + validation loops
    for attempt in range(1, fastp_retries + 1):
        log_info(f"Running fastp pass {attempt}/{fastp_retries}")
        run_fastp_qc(
            paths["raw"], paths["qc"],
            num_threads=threads,
            suffix1=suffix1,
            batch_size=batch_size,
            se=se,
            length_required=fastp_length_required,
            force=force,
        )
        valid, invalid = check_fastp_results(paths["qc"], suffix1=suffix1)
        summarize_step("FASTP QC", "fastp + integrity checks", invalid == 0)
        if invalid == 0:
            break
        if attempt == fastp_retries:
            raise FlowMetaError("fastp outputs still invalid after retries")

    # Step 3-6: Bowtie2 host removal and validation
    for attempt in range(1, host_retries + 1):
        log_info(f"Removing host pass {attempt}/{host_retries}")
        run_remove_host(
            paths["qc"], paths["hr"], paths["bam"],
            db_bowtie2, threads=threads,
            suffix1=suffix1, suffix2=suffix2,
            force=force,
        )
        valid, invalid = check_host_remove_results(paths["hr"])
        summarize_step("Host removal", "Bowtie2 + HR integrity", invalid == 0)
        if invalid == 0:
            break
        if attempt == host_retries:
            raise FlowMetaError("Host removal outputs invalid after retries")

    # Step 7: Extract host reads for HLA/mtDNA
    if skip_host_extract:
        log_warning("Skipping host-read extraction step (samtools disabled)")
    else:
        run_extract_host(
            paths["bam"], paths["host"],
            mode="mapped_anypair",
            samtools_threads=threads,
            pigz_threads=threads,
            force=force,
        )
        summarize_step("Host reads", "Samtools fastq extraction", True)

    # Step 8: Prepare Kraken DB
    kraken_db_path = db_kraken
    if copy_db_to_shm:
        kraken_db_path = load_kraken_db_to_shm(db_kraken, shm_path=shm_path)

    # Step 9-11: Kraken classification + validation loops
    helper_itm = helper_path
    for attempt in range(1, kraken_retries + 1):
        log_info(f"Kraken/Bracken pass {attempt}/{kraken_retries}")
        run_kraken_bracken(
            paths["hr"], paths["kraken"], paths["bracken"],
            db_kraken=kraken_db_path,
            helper_path=helper_itm,
            batch_size=batch_size,
            num_threads=threads,
            se=se,
            force=force,
        )
        valid, invalid = check_kraken_results(paths["kraken"])
        summarize_step("Kraken", "Classification + report checks", invalid == 0)
        if invalid == 0:
            break
        if attempt == kraken_retries:
            raise FlowMetaError("Kraken outputs invalid after retries")

    # Step 12: Remove host taxa from reports (Kraken2 second pass)
    run_remove_host_counts(
        paths["kraken"], paths["kraken_filtered"], kraken_db_path,
        helper_path=helper_itm,
        batch_size=batch_size,
        min_count=min_count,
        force=force,
    )
    summarize_step("Kraken host cleanup", "Filter human taxa + rerun Bracken", True)

    # Step 13: Merge everything into OTU/MPA matrices
    if run_merge_step is None:
        detail = f" ({STEP6_IMPORT_ERROR})" if STEP6_IMPORT_ERROR else ""
        raise FlowMetaError(
            "step6_merge_results requires optional dependencies (pandas, numpy). "
            "Install them to enable the final merge step." + detail
        )

    run_merge_step(
        paths["kraken_filtered"],
        paths["kraken_filtered"],
        paths["mpa"],
        helper_path=helper_itm,
        mpa_suffix=".nohuman.kraken.mpa.std.txt",
        report_suffix=".nohuman.kraken.report.std.txt",
        force=force,
        prefix=project_prefix,
    )
    summarize_step("Merge", "Combine Kraken/Bracken tables", True)

    # Cleanup DB from RAM if requested
    if copy_db_to_shm:
        cleanup_kraken_db(shm_path)

    log_success("flowmeta pipeline finished successfully")
    return paths
