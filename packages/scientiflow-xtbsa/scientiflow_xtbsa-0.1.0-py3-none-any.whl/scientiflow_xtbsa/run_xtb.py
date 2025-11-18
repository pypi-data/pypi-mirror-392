from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional
import json
import subprocess
import re
import csv
import os

ENERGY_REGEX = re.compile(r"TOTAL ENERGY\s+([\-0-9.Ee+]+)\s+Eh")
HARTREE_TO_KCAL_MOL = 627.5094740631

def read_qm_region(outdir: Path) -> Dict[str, Dict[str, str]]:
    outdir = Path(outdir)
    with (outdir / "qm_region.json").open("r") as f:
        return json.load(f)

def build_xtb_cmd(xyz: Path, region_str: str, alpb: str = "water", xtb_cmd: str = "xtb") -> list[str]:
    return [xtb_cmd, str(xyz), "--oniom", "gfn2:gfnff", region_str, "--alpb", alpb]

def parse_xtb_energy(stdout: str) -> Optional[float]:
    m = ENERGY_REGEX.search(stdout)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None

def _set_unlimited_stack(enable: bool, verbose: bool = False) -> None:
    """
    Try to raise the process stack limit to unlimited (POSIX). No-op on non-POSIX.
    """
    if not enable:
        return
    try:
        import resource  # POSIX only
        soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
        # Set to hard limit if hard is finite, else RLIM_INFINITY
        new_soft = hard if hard not in (resource.RLIM_INFINITY, -1) else resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_STACK, (new_soft, hard if hard != -1 else resource.RLIM_INFINITY))
        if verbose:
            print("Set RLIMIT_STACK to unlimited (or maximum available).")
    except Exception as e:
        if verbose:
            print(f"Could not set unlimited stack: {e}")

def run_xtb_single(
    xyz: Path,
    region_str: str,
    *,
    alpb: str = "water",
    xtb_cmd: str = "xtb",
    timeout: Optional[int] = None,
    verbose: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Optional[float]:
    """
    Run xtb. If verbose=True, stream stdout/stderr to console in real-time while capturing for parsing.
    """
    cmd = build_xtb_cmd(xyz, region_str, alpb=alpb, xtb_cmd=xtb_cmd)

    if verbose:
        # Stream live output and capture
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
            )
        except Exception as e:
            print(f"xtb start failed for {xyz}: {e}")
            return None

        captured_lines = []
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                captured_lines.append(line)
                print(line, end="", flush=True)
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"xtb timed out for {xyz}")
            return None
        stdout = "".join(captured_lines)
        return parse_xtb_energy(stdout)

    # Non-verbose: capture silently
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
    except Exception as e:
        return None

    return parse_xtb_energy(res.stdout)

def _convert_energy(value_eh: Optional[float], unit: str) -> Optional[float]:
    """
    Convert energy from Hartree to requested unit.
    Supported units: 'Eh' (no change), 'kcal/mol'.
    """
    if value_eh is None:
        return None
    if unit.lower() in ("eh", "hartree"):
        return value_eh
    if unit.lower() in ("kcal", "kcal/mol", "kcalmol"):
        return value_eh * HARTREE_TO_KCAL_MOL
    # default: passthrough
    return value_eh

def run_xtb_for_outdir(
    outdir: Path,
    *,
    xtb_cmd: str = "xtb",
    alpb: str = "water",
    timeout: Optional[int] = None,
    verbose: bool = False,
    output_unit: str = "kcal/mol",
    # runtime knobs
    omp_threads: int = 1,
    omp_stacksize: str = "8G",
    kmp_stacksize: Optional[str] = "8G",
    stack_unlimited: bool = True,
) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Iterate frames in qm_region.json and run xtb for complex/protein/ligand using relative paths.
    Streams xtb output in real-time when verbose=True.
    Applies runtime knobs (OMP_* and KMP_* env vars; optional unlimited stack).
    Returns energies per frame in output_unit ('kcal/mol' by default).
    """
    outdir = Path(outdir)
    qm = read_qm_region(outdir)
    energies_by_frame: Dict[str, Dict[str, Optional[float]]] = {}

    # Prepare environment for all xTB subprocesses
    base_env = os.environ.copy()
    base_env["OMP_NUM_THREADS"] = str(omp_threads)
    if omp_stacksize:
        base_env["OMP_STACKSIZE"] = str(omp_stacksize)
    if kmp_stacksize:
        base_env["KMP_STACKSIZE"] = str(kmp_stacksize)

    # Try to set unlimited stack in current process (affects children)
    _set_unlimited_stack(stack_unlimited, verbose=verbose)

    for frame_key in sorted(qm.keys()):
        print(f"Processing {frame_key} ...")

        complex_xyz = outdir / f"{frame_key}_complex.xyz"
        protein_xyz = outdir / f"{frame_key}_protein.xyz"
        ligand_xyz  = outdir / f"{frame_key}_ligand.xyz"

        complex_region = qm[frame_key].get("complex", "")
        protein_region = qm[frame_key].get("protein", "")
        ligand_region  = qm[frame_key].get("ligand", "")

        # Run sequentially with relative paths from CWD: e.g., "xtb frames/frame_001_complex.xyz ..."
        complex_eh = None
        protein_eh = None
        ligand_eh = None

        if complex_xyz.exists() and complex_region:
            if verbose:
                print(f"  complex: OMP_NUM_THREADS={base_env.get('OMP_NUM_THREADS')} OMP_STACKSIZE={base_env.get('OMP_STACKSIZE')} KMP_STACKSIZE={base_env.get('KMP_STACKSIZE')}")
                print(f"           xtb {complex_xyz} --oniom gfn2:gfnff \"{complex_region}\" --alpb {alpb}")
            complex_eh = run_xtb_single(
                complex_xyz, complex_region, alpb=alpb, xtb_cmd=xtb_cmd, timeout=timeout, verbose=verbose, env=base_env
            )
        else:
            print(f"  Skipping complex (missing file or region).")

        if protein_xyz.exists() and protein_region:
            if verbose:
                print(f"  protein: xtb {protein_xyz} --oniom gfn2:gfnff \"{protein_region}\" --alpb {alpb}")
            protein_eh = run_xtb_single(
                protein_xyz, protein_region, alpb=alpb, xtb_cmd=xtb_cmd, timeout=timeout, verbose=verbose, env=base_env
            )
        else:
            print(f"  Skipping protein (missing file or region).")

        if ligand_xyz.exists() and ligand_region:
            if verbose:
                print(f"  ligand : xtb {ligand_xyz} --oniom gfn2:gfnff \"{ligand_region}\" --alpb {alpb}")
            ligand_eh = run_xtb_single(
                ligand_xyz, ligand_region, alpb=alpb, xtb_cmd=xtb_cmd, timeout=timeout, verbose=verbose, env=base_env
            )
        else:
            print(f"  Skipping ligand (missing file or region).")

        # Binding energy (Eh), then convert
        binding_eh = None
        if complex_eh is not None and protein_eh is not None and ligand_eh is not None:
            binding_eh = complex_eh - (protein_eh + ligand_eh)

        # Convert to requested unit
        complex_val = _convert_energy(complex_eh, output_unit)
        protein_val = _convert_energy(protein_eh, output_unit)
        ligand_val = _convert_energy(ligand_eh, output_unit)
        binding_val = _convert_energy(binding_eh, output_unit)

        energies_by_frame[frame_key] = {
            "complex_energy": complex_val,
            "protein_energy": protein_val,
            "ligand_energy": ligand_val,
            "binding_free_energy": binding_val,
        }

        # Short per-frame summary
        def fmt(x): return "NA" if x is None else f"{x:.4f} {output_unit}"
        print(f"  energies: E_c={fmt(complex_val)}, E_p={fmt(protein_val)}, E_l={fmt(ligand_val)}, dG={fmt(binding_val)}")

    return energies_by_frame

def update_report_csv(outdir: Path, energies_by_frame: Dict[str, Dict[str, Optional[float]]]) -> None:
    """
    Update scientiflow_xtbsa_report.csv in CWD with energies (stored values are in the
    unit produced by run_xtb_for_outdir, default: kcal/mol). If it does not exist,
    create it and write rows for frames present in energies_by_frame.
    """
    csv_path = Path.cwd() / "scientiflow_xtbsa_report.csv"
    rows = []

    # Load existing rows if present
    if csv_path.exists():
        with csv_path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]

    # Index rows by base path for quick update
    row_index = {r.get("frame_base_path", ""): i for i, r in enumerate(rows)}

    for frame_key, vals in energies_by_frame.items():
        base_path = Path(outdir) / frame_key
        base_rel = os.path.relpath(base_path, start=Path.cwd()).replace("\\", "/")

        def fmt_num(x):
            return "" if x is None else f"{x:.8f}"

        record = {
            "frame_base_path": base_rel,
            "complex_energy": fmt_num(vals.get("complex_energy")),
            "protein_energy": fmt_num(vals.get("protein_energy")),
            "ligand_energy": fmt_num(vals.get("ligand_energy")),
            "binding_free_energy": fmt_num(vals.get("binding_free_energy")),
        }

        if base_rel in row_index:
            rows[row_index[base_rel]].update(record)
        else:
            rows.append(record)

    # Write back
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "frame_base_path",
                "complex_energy",
                "protein_energy",
                "ligand_energy",
                "binding_free_energy",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
