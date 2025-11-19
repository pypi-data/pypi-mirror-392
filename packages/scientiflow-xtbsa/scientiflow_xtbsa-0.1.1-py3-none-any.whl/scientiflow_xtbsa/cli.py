# scientiflow_xtbsa/cli.py
from pathlib import Path
import typer
from rich.console import Console
from rich.traceback import install

install()
app = typer.Typer(help="ScientiFlow xTB-SA: MD -> PCA -> frame extraction -> QM/MM + analysis")
console = Console()

from .sampling import get_representative_frames_pca, export_frames_and_qm_region
from .run_xtb import run_xtb_for_outdir, update_report_csv
from .plot_report import _read_report, _summary, plot_timeseries, plot_histogram, plot_box  # reuse internals

def _generate_plots(outdir: Path, csv_path: Path):
    frames, dgs = _read_report(csv_path)
    if not dgs:
        console.print("[yellow]No binding_free_energy values found; skipping plots.[/yellow]")
        return
    order = sorted(range(len(frames)), key=lambda i: int(Path(frames[i]).name.split("_")[-1]))
    frames = [frames[i] for i in order]
    dgs = [dgs[i] for i in order]
    mean, std, sem = _summary(dgs)
    prefix = "xtbsa"
    plot_timeseries(frames, dgs, outdir / f"{prefix}_dg_timeseries.png",
                    title=f"Binding free energy per frame (mean={mean:.2f} kcal/mol)")
    plot_histogram(dgs, outdir / f"{prefix}_dg_hist.png",
                   title=f"Binding free energy distribution (n={len(dgs)})")
    plot_box(dgs, outdir / f"{prefix}_dg_box.png",
             mean=mean,
             title=f"Binding free energy box plot (n={len(dgs)})")
    console.print(f"[green]Plots written to {outdir}[/green]")

@app.command()
def run(
    # IO
    tpr: Path = typer.Option(
        ...,
        "--tpr",
        "--top",
        help="GROMACS portable run input file (.tpr). For other engines, pass the appropriate structure/topology compatible with MDAnalysis (e.g., .prmtop/.psf/.pdb/.gro).",
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
    ),
    traj: Path = typer.Option(..., "--traj", help="Trajectory file (.xtc/.trr/.dcd).", exists=True, readable=True),
    # ligand only (derive selections internally)
    lig_resname: str = typer.Option("LIG", "--lig-resname", help="Ligand residue name (default: LIG)."),
    # extraction control
    nframes: int = typer.Option(15, "--nframes", "-n", help="Number of representative frames.", min=1),
    outdir: Path = typer.Option(Path("frames"), "--outdir", "-o", help="Output directory."),
    qm_cutoff: float = typer.Option(6.0, "--qm-cutoff", help="Cutoff (Ã) to define QM region.", min=0.0),
    whole_residue: bool = typer.Option(True, "--whole-residue/--no-whole-residue",
                                       help="Include entire residues if any atom within cutoff."),
    # xTB runtime knobs
    omp_threads: int = typer.Option(1, "--omp-threads", help="OMP_NUM_THREADS for xTB.", min=1),
    omp_stacksize: str = typer.Option("8G", "--omp-stacksize", help="OMP_STACKSIZE for xTB (e.g. 8G)."),
    kmp_stacksize: str = typer.Option("8G", "--kmp-stacksize", help="KMP_STACKSIZE for xTB (e.g. 8G)."),
    stack_unlimited: bool = typer.Option(True, "--stack-unlimited/--no-stack-unlimited",
                                         help="Raise stack limit if possible."),
    display_plots: bool = typer.Option(True, "--display-plots/--no-display-plots",
                                       help="Generate plots into outdir (default: on)."),
    # control flags
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite outdir contents if exists."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run full pipeline:
      1. PCA+KMeans frame selection (protein backbone CA by default).
      2. Extract complex/protein/ligand XYZ with dynamic selection using ligand name.
      3. Define QM region (whole residues or atom-level).
      4. Run xTB ONIOM single-point energies (implicit solvent ALPB).
      5. Store energies & binding free energies (kcal/mol) in CSV.
      6. (Optional) Produce plots in outdir.
    """
    console.rule("[bold cyan]ScientiFlow xTB-SA â pipeline run[/bold cyan]")

    # derive selections from ligand name
    lig_resname = lig_resname.strip()
    pca_selection = "protein and name CA"
    write_selection = f"(protein or resname {lig_resname})"

    # ensure outdir
    if outdir.exists():
        if force:
            if verbose:
                console.print(f"[yellow]Cleaning outdir:[/yellow] {outdir}")
            for p in outdir.glob("*"):
                try:
                    if p.is_file():
                        p.unlink()
                    else:
                        import shutil
                        shutil.rmtree(p)
                except Exception as e:
                    console.print(f"[red]Warning removing {p}: {e}[/red]")
        else:
            console.print(f"[red]Outdir {outdir} exists. Use --force to overwrite.[/red]")
            raise typer.Exit(code=1)
    else:
        outdir.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]GROMACS TPR:[/green] {tpr}")
    console.print(f"[green]Trajectory:[/green] {traj}")
    console.print(f"[green]Ligand resname:[/green] {lig_resname}")
    console.print(f"[green]Derived PCA selection:[/green] {pca_selection}")
    console.print(f"[green]Derived write selection:[/green] {write_selection}")
    console.print(f"[green]nframes:[/green] {nframes}")
    console.print(f"[green]qm_cutoff:[/green] {qm_cutoff} Ã")
    console.print(f"[green]whole_residue:[/green] {whole_residue}")
    console.print(f"[green]OMP_NUM_THREADS:[/green] {omp_threads}")
    console.print(f"[green]display_plots:[/green] {display_plots}")

    # Step 1: frame selection
    frame_indices = get_representative_frames_pca(tpr, traj, pca_selection, nframes, verbose=verbose)

    # Step 2: extraction + QM region definition
    export_frames_and_qm_region(
        top=tpr,
        traj=traj,
        write_selection=write_selection,
        lig_resname=lig_resname,
        frame_indices=frame_indices,
        outdir=outdir,
        qm_cutoff=qm_cutoff,
        whole_residue=whole_residue,
        verbose=verbose,
    )

    # Step 3: xTB energies
    energies = run_xtb_for_outdir(
        outdir=outdir,
        xtb_cmd="xtb",
        alpb="water",
        timeout=None,
        verbose=verbose,
        output_unit="kcal/mol",
        omp_threads=omp_threads,
        omp_stacksize=omp_stacksize,
        kmp_stacksize=kmp_stacksize,
        stack_unlimited=stack_unlimited,
    )
    update_report_csv(outdir=outdir, energies_by_frame=energies)

    # Step 4: plots (optional)
    if display_plots:
        _generate_plots(outdir=outdir, csv_path=Path.cwd() / "scientiflow_xtbsa_report.csv")

    console.print(f"[blue]Frame indices (0-based):[/blue] {frame_indices}")
    console.print("[bold green]Done.[/bold green]")

def main():
    app()

if __name__ == "__main__":
    main()
