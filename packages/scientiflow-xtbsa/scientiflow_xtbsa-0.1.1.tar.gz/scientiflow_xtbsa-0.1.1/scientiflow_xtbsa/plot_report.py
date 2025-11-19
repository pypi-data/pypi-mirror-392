#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse
import csv
import math
from typing import List, Tuple
import matplotlib.pyplot as plt

def _read_report(csv_path: Path) -> Tuple[List[str], List[float]]:
    frames: List[str] = []
    dgs: List[float] = []
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("frame_base_path", "").strip()
            dg_str = (row.get("binding_free_energy") or "").strip()
            if not label or not dg_str:
                continue
            try:
                dg = float(dg_str)
            except ValueError:
                continue
            frames.append(label)
            dgs.append(dg)
    return frames, dgs

def _summary(dgs: List[float]) -> Tuple[float, float, float]:
    if not dgs:
        return float("nan"), float("nan"), float("nan")
    n = len(dgs)
    mean = sum(dgs) / n
    var = sum((x - mean) ** 2 for x in dgs) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(var)
    sem = std / math.sqrt(n) if n > 1 else float("nan")
    return mean, std, sem

def _frame_order_key(label: str) -> int:
    # Expect labels like "frames/frame_001"
    try:
        base = Path(label).name  # frame_001
        num = int(base.split("_")[-1])
        return num
    except Exception:
        return 0

def plot_timeseries(frames: List[str], dgs: List[float], out_png: Path, title: str):
    x = list(range(1, len(dgs) + 1))
    plt.figure(figsize=(8, 4.5), dpi=150)
    plt.plot(x, dgs, marker="o", linestyle="-", color="#1f77b4", label="dG per frame")
    plt.axhline(0.0, color="k", linewidth=1, linestyle="--", alpha=0.6)
    plt.xlabel("Frame index (sorted)")
    plt.ylabel("Binding free energy (kcal/mol)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_histogram(dgs: List[float], out_png: Path, title: str):
    plt.figure(figsize=(8, 4.5), dpi=150)
    plt.hist(dgs, bins=min(30, max(10, len(dgs)//2)), color="#2ca02c", alpha=0.8, edgecolor="black")
    plt.axvline(0.0, color="k", linewidth=1, linestyle="--", alpha=0.6)
    plt.xlabel("Binding free energy (kcal/mol)")
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def plot_box(dgs: List[float], out_png: Path, mean: float, title: str):
    plt.figure(figsize=(5, 6), dpi=150)
    box = plt.boxplot(
        dgs,
        vert=True,
        patch_artist=True,
        labels=["Binding"],
        boxprops=dict(facecolor="#aec7e8", edgecolor="#1f77b4"),
        medianprops=dict(color="#d62728", linewidth=2),
        whiskerprops=dict(color="#1f77b4"),
        capprops=dict(color="#1f77b4"),
        flierprops=dict(marker="o", markerfacecolor="#ff9896", markersize=5, alpha=0.7),
    )
    plt.ylabel("Binding free energy (kcal/mol)")
    plt.title(title)
    # Mean as star
    plt.scatter(1, mean, marker="*", s=180, color="#ff7f0e", zorder=5, label=f"Mean = {mean:.2f}")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

def main():
    p = argparse.ArgumentParser(description="Plot ScientiFlow xTB-SA binding energies from CSV.")
    p.add_argument("-c", "-csv", "--csv", type=Path,
                   default=Path.cwd() / "scientiflow_xtbsa_report.csv",
                   help="Path to scientiflow_xtbsa_report.csv (default: CWD).")
    p.add_argument("-o", "--outdir", type=Path,
                   default=Path.cwd() / "plots",
                   help="Directory to save plots (default: ./plots).")
    p.add_argument("-p", "--prefix", type=str, default="xtbsa",
                   help="Filename prefix for plots (default: xtbsa).")
    args = p.parse_args()

    csv_path = args.csv
    outdir = args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        return

    frames, dgs = _read_report(csv_path)
    if not dgs:
        print("No binding_free_energy values found in CSV.")
        return

    # Sort by frame order
    order = sorted(range(len(frames)), key=lambda i: _frame_order_key(frames[i]))
    frames = [frames[i] for i in order]
    dgs = [dgs[i] for i in order]

    mean, std, sem = _summary(dgs)
    print(f"Frames: {len(dgs)}")
    print(f"Mean dG (kcal/mol): {mean:.3f}")
    print(f"Std  dG (kcal/mol): {std:.3f}")
    if not math.isnan(sem):
        print(f"SEM  dG (kcal/mol): {sem:.3f}")

    # Timeseries and histogram
    plot_timeseries(frames, dgs, outdir / f"{args.prefix}_dg_timeseries.png",
                    title=f"Binding free energy per frame (mean={mean:.2f} kcal/mol)")
    plot_histogram(dgs, outdir / f"{args.prefix}_dg_hist.png",
                   title=f"Binding free energy distribution (n={len(dgs)})")
    # Box plot
    plot_box(dgs, outdir / f"{args.prefix}_dg_box.png",
             mean=mean,
             title=f"Binding free energy box plot (n={len(dgs)})")

    print(f"Wrote plots to: {outdir}")

if __name__ == "__main__":
    main()
