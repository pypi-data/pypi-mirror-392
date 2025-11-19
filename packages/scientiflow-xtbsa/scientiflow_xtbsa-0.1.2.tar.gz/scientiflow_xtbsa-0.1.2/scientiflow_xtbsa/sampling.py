from pathlib import Path
from typing import List
import numpy as np
import MDAnalysis as mda
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import json
import csv
import os

def get_representative_frames_pca(
    top, traj, pca_selection: str, nframes: int, random_state: int = 42, verbose: bool = False
) -> List[int]:
    """
    Load trajectory, perform PCA on selected atoms, cluster in PC space, and pick
    representative frames (closest to cluster centroids).
    Returns 0-based frame indices sorted ascending.
    """
    u = mda.Universe(str(top), str(traj))
    ag = u.select_atoms(pca_selection)
    if ag.n_atoms == 0:
        raise ValueError(f"PCA selection matched 0 atoms: {pca_selection}")

    n_frames = len(u.trajectory)
    if n_frames == 0:
        raise ValueError("Trajectory has 0 frames")

    # Gather coordinates for selected atoms for all frames
    coords = np.empty((n_frames, ag.n_atoms, 3), dtype=float)
    for i, ts in enumerate(u.trajectory):
        coords[i] = ag.positions  # AtomGroup updates per frame

    # Flatten per-frame coordinates
    X = coords.reshape(n_frames, -1)

    # PCA to 3 PCs (or as many as possible)
    n_components = min(3, X.shape[1])
    pcs = PCA(n_components=n_components, random_state=random_state).fit_transform(X)

    # Cluster PCs into k groups (k <= number of frames)
    k = min(nframes, n_frames)
    if k < nframes and verbose:
        print(f"Requested nframes={nframes} but only {n_frames} frames available; using k={k}")

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init="auto")
    labels = kmeans.fit_predict(pcs)

    # Representative frame per cluster: closest to centroid in PC space
    frame_indices = []
    for cluster_id in range(k):
        cluster_idx = np.where(labels == cluster_id)[0]
        centroid = kmeans.cluster_centers_[cluster_id]
        dists = np.linalg.norm(pcs[cluster_idx] - centroid, axis=1)
        rep = int(cluster_idx[np.argmin(dists)])
        frame_indices.append(rep)

    frame_indices = sorted(set(frame_indices))
    if verbose:
        print(f"Selected frame indices (0-based): {frame_indices}")
    return frame_indices

def _to_range_string(indices_1based: List[int]) -> str:
    """Convert sorted 1-based indices to compact range string '1-3,5,7-9'."""
    if not indices_1based:
        return ""
    ranges = []
    start = prev = indices_1based[0]
    for x in indices_1based[1:]:
        if x == prev + 1:
            prev = x
            continue
        ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = x
    ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
    return ",".join(ranges)

# --------- helpers: exact coordinate-based mapping per frame (no rounding) ---------
def _coord_key_tuple(xyz: np.ndarray):
    """
    Return a tuple key for a 3-vector of floats. Uses exact floats from MDAnalysis
    (no rounding) as requested.
    """
    return (float(xyz[0]), float(xyz[1]), float(xyz[2]))

def _order_map_for_ag(ag: mda.core.groups.AtomGroup):
    """
    Build a map from exact coordinate tuple to 1-based order(s) within the AtomGroup.
    Multiple atoms can share the same coordinates; keep all in insertion order.
    """
    mapping = {}
    for i, pos in enumerate(ag.positions, start=1):
        key = _coord_key_tuple(pos)
        mapping.setdefault(key, []).append(i)
    return mapping

def _map_orders_by_coords(target_ag: mda.core.groups.AtomGroup, ref_map: dict) -> List[int]:
    """
    Map each atom in target_ag to 1-based order in the reference AtomGroup using exact
    coordinate matching. If multiple candidates exist for a coordinate, assign the first
    not-yet-used one to keep a stable 1:1 mapping.
    """
    used = set()
    orders = []
    for pos in target_ag.positions:
        key = _coord_key_tuple(pos)
        if key not in ref_map:
            # In the same frame with the same coordinates this should not happen
            # If it does, skip to be robust.
            continue
        candidates = ref_map[key]
        # pick first not used, else fall back to first
        chosen = None
        for c in candidates:
            if c not in used:
                chosen = c
                break
        if chosen is None:
            chosen = candidates[0]
        used.add(chosen)
        orders.append(chosen)
    # unique sorted for compact ranges
    return sorted(set(orders))

def _select_inner_protein(u: mda.Universe, write_selection: str, lig_resname: str, cutoff: float, whole_residue: bool):
    """
    Select protein atoms for QM region around ligand:
      - whole_residue=True: include entire residues within cutoff of ligand.
      - whole_residue=False: include only atoms within cutoff of ligand.
    Both cases restrict to write_selection and exclude ligand atoms.
    """
    base = f"({write_selection}) and not resname {lig_resname}"
    if whole_residue:
        query = f"byres (around {cutoff} resname {lig_resname}) and {base}"
    else:
        query = f"(around {cutoff} resname {lig_resname}) and {base}"
    return u.select_atoms(query)
# -----------------------------------------------------------------------------

def export_frames_and_qm_region(
    top,
    traj,
    write_selection: str,
    lig_resname: str,
    frame_indices: List[int],
    outdir: Path,
    qm_cutoff: float,
    whole_residue: bool = True,
    verbose: bool = False,
):
    """
    For each frame:
      - write frame_XXX_complex.xyz, frame_XXX_protein.xyz, frame_XXX_ligand.xyz
      - determine QM region indices:
          * whole_residue=True  -> whole residues near ligand
          * whole_residue=False -> only atoms near ligand
        complex indices in complex.xyz numbering; protein indices in protein.xyz numbering; ligand indices 1..n.
      - write qm_region.json and initialize scientiflow_xtbsa_report.csv.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    u = mda.Universe(str(top), str(traj))

    # Atom groups defining XYZ output order (positions update per frame)
    complex_ag = u.select_atoms(write_selection)
    if complex_ag.n_atoms == 0:
        raise ValueError(f"Write selection matched 0 atoms: {write_selection}")
    ligand_all = u.select_atoms(f"({write_selection}) and resname {lig_resname}")
    if ligand_all.n_atoms == 0:
        raise ValueError(f"No ligand atoms found for resname '{lig_resname}' within write-selection.")
    protein_all = u.select_atoms(f"({write_selection}) and not resname {lig_resname}")

    qm_json = {}
    report_rows = []  # rows for scientiflow_xtbsa_report.csv

    for i, frame_idx in enumerate(sorted(frame_indices), start=1):
        # Move to frame
        u.trajectory[frame_idx]

        # Paths
        complex_path = outdir / f"frame_{i:03d}_complex.xyz"
        protein_path = outdir / f"frame_{i:03d}_protein.xyz"
        ligand_path = outdir / f"frame_{i:03d}_ligand.xyz"

        # Write XYZs for this frame (orders of AGs define numbering)
        complex_ag.write(str(complex_path))
        if protein_all.n_atoms:
            protein_all.write(str(protein_path))
        ligand_all.write(str(ligand_path))

        # Build coordinate -> order maps for this frame
        complex_map = _order_map_for_ag(complex_ag)
        protein_map = _order_map_for_ag(protein_all) if protein_all.n_atoms else {}
        # ligand numbering is always full 1..n in its own file; map still useful for checks
        ligand_map = _order_map_for_ag(ligand_all)

        # Determine inner protein (whole residues or atoms within cutoff of ligand)
        inner_protein_ag = _select_inner_protein(u, write_selection, lig_resname, qm_cutoff, whole_residue)

        # Complex numbering (for XTB --oniom on complex.xyz)
        ligand_complex_idx = _map_orders_by_coords(ligand_all, complex_map)
        inner_protein_complex_idx = _map_orders_by_coords(inner_protein_ag, complex_map)
        qm_complex_idx = sorted(set(ligand_complex_idx).union(inner_protein_complex_idx))

        # Protein numbering (only protein part of QM region)
        inner_protein_protein_idx = _map_orders_by_coords(inner_protein_ag, protein_map) if protein_map else []

        # Ligand numbering: 1..n (full ligand in ligand.xyz)
        ligand_local_idx = list(range(1, ligand_all.n_atoms + 1))

        # Build JSON entry
        frame_key = f"frame_{i:03d}"
        qm_json[frame_key] = {
            "complex": _to_range_string(qm_complex_idx),
            "protein": _to_range_string(inner_protein_protein_idx),
            "ligand": _to_range_string(ligand_local_idx),
        }

        # Add report row (relative base path; energy columns to be filled after xTB run)
        base_path = Path(outdir) / f"frame_{i:03d}"
        base_rel = os.path.relpath(base_path, start=Path.cwd())
        report_rows.append(
            {
                "frame_base_path": base_rel.replace("\\", "/"),
                "complex_energy": "",
                "protein_energy": "",
                "ligand_energy": "",
                "binding_free_energy": "",
            }
        )

        if verbose:
            print(
                f"{frame_key}: complex={qm_json[frame_key]['complex']} "
                f"protein={qm_json[frame_key]['protein']} "
                f"ligand={qm_json[frame_key]['ligand']}"
            )

    # Write qm_region.json
    with (outdir / "qm_region.json").open("w") as f:
        json.dump(qm_json, f, indent=2)

    # Write report CSV in current working directory
    csv_path = Path.cwd() / "scientiflow_xtbsa_report.csv"
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
        writer.writerows(report_rows)


