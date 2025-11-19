# scientiflow-xtbsa

ScientiFlow xTB-SA: automated selection of representative MD snapshots and semi-empirical QM/MM ONIOM single-point evaluations to estimate protein–ligand interaction energies.

Maintained by Scientiflow. For end-to-end automated protein–ligand MD workflows integrated with GROMACS and deployment at scale, see https://scientiflow.com/.

## What it does (high level)

- Input: MD topology+trajectory (e.g., GROMACS .tpr + .xtc).
- Sampling: PCA on protein Cα coordinates; KMeans to pick N representative frames.
- Extraction: For each selected frame, write XYZ for complex, protein, and ligand.
- QM/MM region: Define a QM inner region around the ligand using a cutoff (Å). Optionally include whole residues within the cutoff or only atoms within the cutoff.
- Energetics: Run xTB with ONIOM (gfn2:gfnff) and ALPB water for complex, protein, and ligand; compute a per-frame interaction energy proxy:
  ΔG_bind,proxy ≈ E_complex − (E_protein + E_ligand)
- Reporting: Write scientiflow_xtbsa_report.csv (kcal/mol) and plots into the output directory.

### About the equation

- We compute an interaction/binding free-energy proxy from single-point ONIOM energies in implicit solvent:
  ΔG_bind,proxy ≈ E_complex − (E_protein + E_ligand)
- Sign convention: Negative values suggest favorable binding. Positive values can occur for some frames and are expected. The meaningful metric is the ensemble average across many frames (report mean ± SEM).
- Scope: This proxy omits vibrational/rotational/translational entropies and standard-state corrections. For absolute ΔG°, add such corrections or use rigorous alchemical methods. As implemented, this is similar in spirit to MM/PBSA, but with a QM/MM inner region.

## Prerequisites (user)

- xTB executable available on PATH (https://github.com/grimme-lab/xtb)
- Python 3.9+ and internet access to install Python dependencies

## Install (user)

- Install the package:
  pip install scientiflow-xtbsa

- Verify the CLI is available:
  scientiflow-xtbsa --help

## Quick start

Basic GROMACS-first usage (defaults used where possible):
- Select frames, build QM/MM regions, run xTB, write CSV and plots:

  scientiflow-xtbsa --tpr path/to/topology.tpr --traj path/to/trajectory.xtc --outdir frames

Customize ligand residue name (default LIG):
- The selections are derived automatically from the ligand name.

  scientiflow-xtbsa --tpr samples/md_0_10.tpr --traj samples/md_0_10_5ns.xtc --lig-resname UNL1 --outdir frames

Disable whole-residue rule (include only atoms within cutoff):
  scientiflow-xtbsa --tpr samples/md_0_10.tpr --traj samples/md_0_10_5ns.xtc --no-whole-residue

Control frame count and cutoff; tune xTB threading/stack:
  scientiflow-xtbsa --tpr samples/md_0_10.tpr --traj samples/md_0_10_5ns.xtc -n 20 --qm-cutoff 6 --omp-threads 1 --omp-stacksize 8G --kmp-stacksize 8G

Turn off plot generation:
  scientiflow-xtbsa --tpr samples/md_0_10.tpr --traj samples/md_0_10_5ns.xtc --no-display-plots

Note for other MD engines:
- Pass a structure/topology readable by MDAnalysis (e.g., Amber .prmtop + .nc/.dcd, CHARMM/NAMD .psf + .dcd, or .pdb + .dcd) via --tpr (name kept for consistency; the file itself can be any MDAnalysis-supported topology).

## CLI flags and defaults

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| --tpr, --top | Path | required | GROMACS .tpr preferred; for other engines, pass a topology compatible with MDAnalysis (.prmtop/.psf/.pdb/.gro). |
| --traj | Path | required | Trajectory file (.xtc/.trr/.dcd/.nc etc.). |
| --lig-resname | str | LIG | Ligand residue name used in selections. |
| --nframes, -n | int | 15 | Number of representative frames (PCA+KMeans). |
| --outdir, -o | Path | frames | Output directory for frames/plots. |
| --qm-cutoff | float | 6.0 | Cutoff (Å) to define QM inner region around the ligand. |
| --whole-residue / --no-whole-residue | bool | True | If true, include entire residues with any atom within cutoff; else include only atoms within cutoff. |
| --omp-threads | int | 1 | OMP_NUM_THREADS for xTB subprocesses. |
| --omp-stacksize | str | 8G | OMP_STACKSIZE for xTB. |
| --kmp-stacksize | str | 8G | KMP_STACKSIZE for xTB. |
| --stack-unlimited / --no-stack-unlimited | bool | True | Attempt to raise process stack limit (POSIX), similar to ulimit -s unlimited. |
| --display-plots / --no-display-plots | bool | True | Generate plots (timeseries, histogram, box) into outdir. |
| --force, -f | bool | False | Overwrite outdir if it exists. |
| --verbose, -v | bool | False | Stream xTB output and print progress in real time. |

Derived selections (no flags needed):
- PCA selection: "protein and name CA" (protein backbone Cα).
- Write selection: "(protein or resname LIGAND)" where LIGAND is the provided --lig-resname (default LIG).

## Outputs

- outdir/frame_XXX_complex.xyz, frame_XXX_protein.xyz, frame_XXX_ligand.xyz: per-frame structures (numbering per file).
- outdir/qm_region.json: ONIOM QM region index strings for each frame:
  - complex: indices in complex.xyz numbering for QM inner region (ligand + nearby protein).
  - protein: indices in protein.xyz numbering for the protein part of the QM region.
  - ligand: indices 1..n for ligand.xyz.
- scientiflow_xtbsa_report.csv: per-frame energies (kcal/mol) and ΔG_bind,proxy.
- outdir/xtbsa_dg_timeseries.png: per-frame ΔG.
- outdir/xtbsa_dg_hist.png: ΔG distribution.
- outdir/xtbsa_dg_box.png: box plot with mean (star).

## Best practices

- Use many frames (e.g., 20–100) to stabilize averages; report mean ± SEM.
- Ensure protonation states and net charges are consistent across complex/protein/ligand systems for xTB.
- Consider both whole-residue and atom-level cutoff schemes to assess sensitivity.
- Negative average ΔG_bind,proxy indicates favorable binding; individual frames may be positive.

## Troubleshooting

- "No ligand atoms found for resname 'XXX' within write-selection."  
  Ensure --lig-resname matches the residue name in your topology (case-sensitive). The write selection is derived as `(protein or resname XXX)`.

- xTB very slow or stalls:  
  Use `--omp-threads 1 --omp-stacksize 8G --kmp-stacksize 8G --stack-unlimited` (default settings mimic recommended shell script tweaks). Run with `--verbose` to stream xTB output.

## How it works (technical detail)

1. MDAnalysis loads the topology+trajectory.
2. PCA on "protein and name CA" → project frames → KMeans to N clusters → choose medoids.
3. For each chosen frame:
   - Write complex/protein/ligand XYZ.
   - Build QM region by distance from ligand (cutoff Å), either by atoms or by whole residues.
   - Map indices carefully between complex/protein/ligand numberings and serialize to qm_region.json.
4. For each frame, run xTB ONIOM (gfn2:gfnff, ALPB water) for complex/protein/ligand; parse total energies; compute:
   ΔG_bind,proxy ≈ E_complex − (E_protein + E_ligand)
   Convert to kcal/mol and write CSV; generate plots (optional).

Attribution: This package is maintained by Scientiflow. For integrated solutions with GROMACS and production pipelines, visit https://scientiflow.com/.
