# scientiflow_xtbsa/cli.py
from pathlib import Path
import typer
from rich.console import Console
from rich.traceback import install

install()
app = typer.Typer(help="ScientiFlow xTB-SA: MD -> PCA -> frame extraction -> downstream QM/MM")
console = Console()

from .sampling import get_representative_frames_pca
from .sampling import export_frames_and_qm_region
from .run_xtb import run_xtb_for_outdir, update_report_csv

@app.command()
def run(
    # IO
    top: Path = typer.Option(
        ...,
        "--top",
        help="Topology file (.tpr, .top, .gro, .pdb) from GROMACS.",
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
    ),
    traj: Path = typer.Option(
        ...,
        "--traj",
        help="Trajectory file (.xtc, .trr, .dcd) from GROMACS.",
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
    ),

    # PCA & selections
    pca_selection: str = typer.Option(
        "protein and name CA",
        "--pca-selection",
        help='Selection string for PCA (MDAnalysis selection language). Default: "protein and name CA".',
    ),
    lig_resname: str = typer.Option(
        "LIG",
        "--lig-resname",
        help="Residue name of the ligand (used to write ligand-only XYZ). Default: LIG",
    ),
    write_selection: str = typer.Option(
        "(protein or resname LIG)",
        "--write-selection",
        help='Selection string used to write XYZ files (default: "(protein or resname LIG)").',
    ),

    # extraction control
    nframes: int = typer.Option(
        15,
        "--nframes",
        "-n",
        help="Number of representative frames to extract (via PCA+KMeans).",
        min=1,
    ),
    outdir: Path = typer.Option(
        Path("frames"),
        "--outdir",
        "-o",
        help="Output directory to write per-frame XYZ files.",
    ),
    qm_cutoff: float = typer.Option(
        6.0,
        "--qm-cutoff",
        help="Cutoff (Ã) around ligand to include protein residues/atoms in QM region.",
        min=0.0,
    ),
    whole_residue: bool = typer.Option(
        True,
        "--whole-residue/--no-whole-residue",
        help="If set, include entire residues when any atom is within cutoff of ligand.",
    ),
    # xTB runtime knobs
    omp_threads: int = typer.Option(
        1, "--omp-threads", help="Set OMP_NUM_THREADS for xTB subprocess runs.", min=1
    ),
    omp_stacksize: str = typer.Option(
        "8G", "--omp-stacksize", help="Set OMP_STACKSIZE for xTB subprocess runs (e.g., 8G, 512M)."
    ),
    kmp_stacksize: str = typer.Option(
        "8G", "--kmp-stacksize", help="Set KMP_STACKSIZE for xTB subprocess runs (e.g., 8G, 512M)."
    ),
    stack_unlimited: bool = typer.Option(
        True,
        "--stack-unlimited/--no-stack-unlimited",
        help="If set, increase process stack limit to unlimited before running xTB.",
    ),
    # control flags
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite output directory if it exists.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Parent entry: run pipeline steps. Currently implements step 1:
    PCA -> KMeans -> extract representative frames and write PDBs.
    """
    console.rule("[bold cyan]Scientiflow xTB-SA â run: extract frames (step 1)")

    # ensure outdir
    if outdir.exists():
        if force:
            if verbose:
                console.print(f"[yellow]Removing existing output dir:[/yellow] {outdir}")
            # be conservative: only remove contents, not top-level dir
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
            console.print(f"[red]Output directory {outdir} already exists. Use --force to overwrite.[/red]")
            raise typer.Exit(code=1)
    else:
        outdir.mkdir(parents=True, exist_ok=True)

    console.print(f"[green]Topology:[/green] {top}")
    console.print(f"[green]Trajectory:[/green] {traj}")
    console.print(f"[green]PCA selection:[/green] {pca_selection}")
    console.print(f"[green]Write selection:[/green] {write_selection}")
    console.print(f"[green]Ligand resname:[/green] {lig_resname}")
    console.print(f"[green]nframes:[/green] {nframes}")
    console.print(f"[green]outdir:[/green] {outdir}")
    console.print(f"[green]qm_cutoff:[/green] {qm_cutoff} Ã")
    console.print(f"[green]whole_residue:[/green] {whole_residue}")
    console.print(f"[green]OMP_NUM_THREADS:[/green] {omp_threads}")
    console.print(f"[green]OMP_STACKSIZE:[/green] {omp_stacksize}")
    console.print(f"[green]KMP_STACKSIZE:[/green] {kmp_stacksize}")
    console.print(f"[green]stack_unlimited:[/green] {stack_unlimited}")

    # Step 1: Identify representative frames via PCA+KMeans
    frame_indices = get_representative_frames_pca(
        top, traj, pca_selection, nframes, verbose=verbose
    )

    # Step 2: Export XYZs and QM region JSON for each selected frame
    export_frames_and_qm_region(
        top=top,
        traj=traj,
        write_selection=write_selection,
        lig_resname=lig_resname,
        frame_indices=frame_indices,
        outdir=outdir,
        qm_cutoff=qm_cutoff,
        whole_residue=whole_residue,
        verbose=verbose,
    )

    # Step 3: Run xTB for complex/protein/ligand per frame and update CSV
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

    console.print(f"[blue]Extracted frame indices (0-based):[/blue] {frame_indices}")
    console.print("[bold green]Done.[/bold green]")

def main():
    app()

if __name__ == "__main__":
    main()
