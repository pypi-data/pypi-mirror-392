"""Step 6: Merge Kraken/Bracken results and create OTU/MPA matrices"""

import os
import glob
import subprocess
import tempfile

import pandas as pd
from ..utils import log_info, log_success, log_warning, print_colorful_message


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def _outputs_ready(paths):
    return bool(paths) and all(os.path.exists(p) and os.path.getsize(p) > 0 for p in paths)


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def _prefix_name(prefix: str, name: str) -> str:
    return f"{prefix}{name}" if prefix else name


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def run_combine_bracken_outputs(bracken_dir, helper_path, output_dir, prefix=""):
    """Combine Bracken outputs for genus/family/order/species levels."""
    os.makedirs(output_dir, exist_ok=True)
    bracken_files = glob.glob(os.path.join(bracken_dir, '*.bracken'))
    if not bracken_files:
        log_warning(f"No bracken files found in {bracken_dir}")
        return []

    level_mapping = {'g': 'genus', 'f': 'family', 'o': 'order', 's': 'species'}
    script = os.path.join(helper_path, 'combine_bracken_outputs2.py')
    generated = []

    for level, level_name in level_mapping.items():
        level_files = [f for f in bracken_files if f.endswith(f"{level}.bracken")]
        if not level_files:
            log_warning(f"No {level}.bracken files found")
            continue

        names = ','.join([
            os.path.basename(file).replace(f"{level}.bracken", '')
            for file in level_files
        ])
        level_output = os.path.join(
            output_dir,
            _prefix_name(prefix, f"2-combined_bracken_results_{level_name}.txt"),
        )

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
            tmp.write('\n'.join(level_files))
            tmp_path = tmp.name

        command = [
            'python', script,
            '--file_list', tmp_path,
            '--names', names,
            '-o', level_output
        ]
        subprocess.run(command, check=True)
        os.remove(tmp_path)
        log_info(f"Combined Bracken ({level_name}) ready")
        if os.path.exists(level_output) and os.path.getsize(level_output) > 0:
            generated.append(level_output)

    return generated


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def merge_results(kraken_dir, bracken_dir, mpa_dir, helper_path,
                  mpa_suffix='nohuman.kraken.mpa.std.txt',
                  report_suffix='nohuman.kraken.report.std.txt',
                  prefix=""):
    """Aggregate Kraken MPAs and Bracken tables into final outputs."""
    os.makedirs(mpa_dir, exist_ok=True)
    produced = []

    log_info("Merging Kraken MPA files...")
    mpa_files = [
        os.path.join(kraken_dir, f)
        for f in os.listdir(kraken_dir)
        if f.endswith(mpa_suffix) and os.path.getsize(os.path.join(kraken_dir, f)) > 0
    ]
    if not mpa_files:
        log_warning("No MPA files found to merge")
    else:
        combine_mpa_script = os.path.join(helper_path, 'combine_mpa.py')
        combined_mpa = os.path.join(mpa_dir, _prefix_name(prefix, '1-combine_mpa_std.txt'))
        mpa_files_sorted = sorted(mpa_files)
        command = ['python', combine_mpa_script, '-i', *mpa_files_sorted, '-o', combined_mpa]
        subprocess.run(command, check=True)
        update_mpa_column_names(combined_mpa, mpa_files_sorted, mpa_suffix)
        log_info("Combined MPA output ready")
        produced.append(combined_mpa)

    log_info("Creating OTU matrices from Kraken outputs...")
    kraken2otu_script = os.path.join(helper_path, 'kraken2otu.py')
    otu_output = os.path.join(mpa_dir, _prefix_name(prefix, 'count_separated'))
    os.makedirs(otu_output, exist_ok=True)
    remove_empty_reports(kraken_dir, report_suffix)
    for level in ['c', 'o', 'f', 'g', 's']:
        command = [
            'python', kraken2otu_script,
            '--extension', report_suffix,
            '--inputfolder', kraken_dir,
            '--level', level,
            '--outdir', otu_output
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    _rename_otu_outputs(otu_output)

    produced.extend(run_combine_bracken_outputs(bracken_dir, helper_path, mpa_dir, prefix=prefix))

    log_success("Combined Kraken/Bracken results ready")
    return produced


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def update_mpa_column_names(file_path, mpa_files, mpa_suffix):
    sample_ids = [os.path.basename(f).replace(mpa_suffix, "") for f in mpa_files]
    if not os.path.exists(file_path):
        return
    df = pd.read_csv(file_path, sep='\t')
    expected_cols = 1 + len(sample_ids)
    if len(df.columns) != expected_cols:
        log_warning("MPA column count mismatch; skipping rename")
        return
    df.columns = ['taxonomy'] + sample_ids
    df.to_csv(file_path, sep='\t', index=False)


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def remove_empty_reports(directory, suffix):
    empty_files = []
    for path in glob.glob(os.path.join(directory, f"*{suffix}")):
        if os.path.getsize(path) == 0:
            empty_files.append(path)
            os.remove(path)
    if empty_files:
        log_warning(f"Removed {len(empty_files)} empty report files before OTU generation")


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def _rename_otu_outputs(outdir):
    if not os.path.isdir(outdir):
        return
    for path in glob.glob(os.path.join(outdir, "otu_table_*.csv")):
        base = os.path.basename(path)
        renamed = base.replace("otu_table_", "count_data_")
        if renamed == base:
            continue
        target = os.path.join(outdir, renamed)
        try:
            os.replace(path, target)
        except OSError:
            continue


# FlowMeta: Automated End-to-End Metagenomic Profiling Pipeline
# Author: Dongqiang Zeng
# Email: interlaken@smu.edu.cn
# Affiliation: Southern Medical University
# Last Modified: 2025-11-15
def run_merge_step(kraken_dir, bracken_dir, mpa_dir, helper_path,
                   mpa_suffix='nohuman.kraken.mpa.std.txt',
                   report_suffix='nohuman.kraken.report.std.txt',
                   force=False,
                   prefix=""):
    """Execute step 6 merging pipeline."""
    log_info("=" * 60)
    print_colorful_message("STEP 6: Merge Kraken/Bracken outputs", 'cyan')
    log_info("=" * 60)

    done_flag = os.path.join(mpa_dir, _prefix_name(prefix, "step6.task.complete"))
    if os.path.exists(done_flag) and not force:
        log_info("Skipped Step 6 (already merged)")
        return True

    outputs = merge_results(
        kraken_dir,
        bracken_dir,
        mpa_dir,
        helper_path,
        mpa_suffix=mpa_suffix,
        report_suffix=report_suffix,
        prefix=prefix
    )

    if _outputs_ready(outputs):
        with open(done_flag, 'w') as f:
            f.write('Merge step complete')
        log_success("STEP 6 completed successfully")
        return True

    log_warning("STEP 6 outputs incomplete; task flag not written")
    return False
