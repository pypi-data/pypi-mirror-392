import os
import time
import numpy as np
from numba import jit
import multiprocessing as mp
from ase.data import atomic_masses
from aegon.libutils import readxyzs, writexyzs, centroid, sort_by_energy, align_two
#------------------------------------------------------------------------------------------
# Global tolerances
tolsij = 0.95
tolene = 0.10
#------------------------------------------------------------------------------------------
# Optimized USR helper functions
#------------------------------------------------------------------------------------------
@jit(nopython=True)
def lastwo_central_moment_numba(arr):
    """
    Compute the last two central moments (variance and third central moment)
    for a 1D numpy array using Numba for speed.
    Returns: array([second_moment, third_moment])
    """
    xavg = np.mean(arr)
    res = arr - xavg
    ssq2 = np.mean(res**2)
    ssq3 = np.mean(res**3)
    return np.array([ssq2, ssq3])
#------------------------------------------------------------------------------------------
def lastwo_central_moment(listxxx):
    """
    Wrapper that converts an arbitrary sequence to float64 numpy array
    and calls the Numba implementation.
    """
    arr = np.array(listxxx, dtype=np.float64)
    return lastwo_central_moment_numba(arr)
#------------------------------------------------------------------------------------------
@jit(nopython=True)
def find_extreme_points_numba(positions, centroid):
    """
    Find four characteristic points used by USR:
      - centroid (provided)
      - atom closest to centroid
      - atom farthest from centroid
      - atom farthest from the farthest atom (to obtain an extended diameter)
    Implemented in Numba for speed. Returns a tuple:
      (centroid, closest_pos, farthest_pos, farthest_from_farthest_pos)
    """
    n_atoms = len(positions)
    distances_to_centroid = np.zeros(n_atoms)
    for i in range(n_atoms):
        distances_to_centroid[i] = np.linalg.norm(positions[i] - centroid)
    closest_idx = np.argmin(distances_to_centroid)
    farthest_idx = np.argmax(distances_to_centroid)

    distances_from_farthest = np.zeros(n_atoms)
    for i in range(n_atoms):
        distances_from_farthest[i] = np.linalg.norm(positions[i] - positions[farthest_idx])
    farthest_from_farthest_idx = np.argmax(distances_from_farthest)

    return (centroid, positions[closest_idx], positions[farthest_idx], positions[farthest_from_farthest_idx])
#------------------------------------------------------------------------------------------
def four_points(atoms):
    """
    Build the positions array and compute the four characteristic points
    using the centroid helper and the Numba extreme point finder.
    """
    positions = np.array([atom.position for atom in atoms])
    ctd = centroid(atoms)
    return find_extreme_points_numba(positions, ctd)
#------------------------------------------------------------------------------------------
@jit(nopython=True)
def calculate_usr_descriptors_numba(positions, points, masses=None, mass_avg=None):
    """
    Calculate USR descriptors for a set of positions given the four points.
    If masses is provided, compute mass-weighted moments as additional features.
    Returns:
      - 8 features for monoatomic (4 x [variance, third_moment])
      - 16 features if masses provided (adds 4 mass-weighted pairs)
    """
    ctd, cst, fct, ftf = points
    n_atoms = len(positions)
    lctd = np.zeros(n_atoms)
    lcst = np.zeros(n_atoms)
    lfct = np.zeros(n_atoms)
    lftf = np.zeros(n_atoms)

    for i in range(n_atoms):
        pos = positions[i]
        lctd[i] = np.linalg.norm(pos - ctd)
        lcst[i] = np.linalg.norm(pos - cst)
        lfct[i] = np.linalg.norm(pos - fct)
        lftf[i] = np.linalg.norm(pos - ftf)

    a1 = lastwo_central_moment_numba(lctd)
    a2 = lastwo_central_moment_numba(lcst)
    a3 = lastwo_central_moment_numba(lfct)
    a4 = lastwo_central_moment_numba(lftf)

    # If no masses are provided, return the unweighted descriptors (8 values)
    if masses is None:
        return np.concatenate((a1, a2, a3, a4))

    # Otherwise compute mass-weighted distances and their moments
    lctdm = np.zeros(n_atoms)
    lcstm = np.zeros(n_atoms)
    lfctm = np.zeros(n_atoms)
    lftfm = np.zeros(n_atoms)
    for i in range(n_atoms):
        mi = masses[i]
        lctdm[i] = lctd[i] * mi / mass_avg
        lcstm[i] = lcst[i] * mi / mass_avg
        lfctm[i] = lfct[i] * mi / mass_avg
        lftfm[i] = lftf[i] * mi / mass_avg

    b1 = lastwo_central_moment_numba(lctdm)
    b2 = lastwo_central_moment_numba(lcstm)
    b3 = lastwo_central_moment_numba(lfctm)
    b4 = lastwo_central_moment_numba(lftfm)

    return np.concatenate((a1, a2, a3, a4, b1, b2, b3, b4))
#------------------------------------------------------------------------------------------
def USRMonoatom(moleculein):
    """
    Compute the 8-feature USR descriptor (geometry-only) for a molecule.
    """
    positions = np.array([atom.position for atom in moleculein])
    points = four_points(moleculein)
    return calculate_usr_descriptors_numba(positions, points)
#------------------------------------------------------------------------------------------
def USRMultiatom(moleculein):
    """
    Compute the 16-feature USR descriptor including mass-weighted moments.
    """
    positions = np.array([atom.position for atom in moleculein])
    masses = np.array([atomic_masses[atom.number] for atom in moleculein])
    mass_avg = np.mean(masses)
    points = four_points(moleculein)
    return calculate_usr_descriptors_numba(positions, points, masses, mass_avg)
#------------------------------------------------------------------------------------------
@jit(nopython=True)
def similarity_numba(vi, vj, n_features):
    """
    Fast similarity metric implemented in Numba:
    similarity = 1 / (1 + (Manhattan_distance / n_features))
    Returns a float in (0,1].
    """
    manhattan_distance = np.sum(np.abs(vi - vj))
    return 1.0 / (1.0 + manhattan_distance / float(n_features))
#------------------------------------------------------------------------------------------
def compute_similarity_matrix_serial(descriptors, n_features):
    """
    Compute a symmetric similarity matrix (serial) for a list of descriptors.
    """
    n_mols = len(descriptors)
    similarity_matrix = np.zeros((n_mols, n_mols))
    for i in range(n_mols):
        vi = descriptors[i]
        for j in range(i, n_mols):
            vj = descriptors[j]
            sij = similarity_numba(vi, vj, n_features)
            similarity_matrix[i, j] = sij
            similarity_matrix[j, i] = sij
    return similarity_matrix
#------------------------------------------------------------------------------------------
def find_similar_elements(listmol, similarity_matrix, tols=tolsij, tole=tolene):
    """
    Identify and remove molecules similar by geometry (similarity >= tols)
    and close in energy (|DeltaE| <= tole). Returns list of dissimilar (kept) molecules.
    """
    similar_indices = []
    num_elements = similarity_matrix.shape[0]

    for i in range(num_elements):
        for j in range(i + 1, num_elements):
            edf = np.abs(listmol[i].info['e'] - listmol[j].info['e'])
            if (similarity_matrix[i, j] >= tols) and (edf <= tole):
                similar_indices.append(j)

    similar_indices = list(set(similar_indices))
    dissimilars_atoms = [listmol[i] for i in range(num_elements) if i not in similar_indices]
    return dissimilars_atoms
#------------------------------------------------------------------------------------------
def disc_USR_sublist(args):
    """
    Process a sublist of molecules with USR descriptors — worker for multiprocessing.
    Args tuple: (sublist, tols, tole, mono)
    Returns: filtered list for the sublist
    """
    sublist, tols, tole, mono = args
    num_molecules = len(sublist)
    if num_molecules == 0:
        return []

    n_features = 8 if mono else 16

    # Compute descriptors for the sublist
    if mono:
        descriptors = [USRMonoatom(mol) for mol in sublist]
    else:
        descriptors = [USRMultiatom(mol) for mol in sublist]
    # Compute similarity matrix and filter
    similarity_matrix = compute_similarity_matrix_serial(descriptors, n_features)
    return find_similar_elements(sublist, similarity_matrix, tols, tole)
#------------------------------------------------------------------------------------------
def split_list(lst, n):
    """
    Split a list into n approximately equal parts.
    """
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]
#------------------------------------------------------------------------------------------
def _second_pass_filtering(molecules, tols, tole, mono):
    """
    Efficient second-pass filtering across many molecules.
    Only compares molecules close in energy to reduce comparisons.
    """
    if len(molecules) <= 1:
        return molecules

    molecules_sorted = sorted(molecules, key=lambda x: x.info['e'])
    n_mols = len(molecules_sorted)

    # Precompute descriptors once
    n_features = 8 if mono else 16
    if mono:
        descriptors = [USRMonoatom(mol) for mol in molecules_sorted]
    else:
        descriptors = [USRMultiatom(mol) for mol in molecules_sorted]

    keep_indices = set(range(n_mols))

    # For each molecule, compare only to neighbors in energy within a window
    for i in range(n_mols):
        if i not in keep_indices:
            continue

        vi = descriptors[i]
        ei = molecules_sorted[i].info['e']

        # Limit search range to save time (adjustable heuristic)
        search_range = min(50, n_mols // 10)
        start_j = max(0, i - search_range)
        end_j = min(n_mols, i + search_range + 1)

        for j in range(start_j, end_j):
            if j <= i or j not in keep_indices:
                continue

            edf = np.abs(ei - molecules_sorted[j].info['e'])
            if edf > tole:
                continue

            sij = similarity_numba(vi, descriptors[j], n_features)
            if sij >= tols:
                keep_indices.remove(j)

    return [molecules_sorted[i] for i in sorted(keep_indices)]
#------------------------------------------------------------------------------------------
def comparator_usr_serial(molecules, tols=tolsij, tole=tolene, mono=False):
    """
    Serial USR comparator — computes descriptors and filters duplicates entirely in memory.
    Returns filtered list of molecules.
    """
    ni = len(molecules)
    if ni == 0:
        return []

    n_features = 8 if mono else 16

    # Compute descriptors
    if mono:
        descriptors = [USRMonoatom(mol) for mol in molecules]
    else:
        descriptors = [USRMultiatom(mol) for mol in molecules]

    # Build similarity matrix and filter
    similarity_matrix = compute_similarity_matrix_serial(descriptors, n_features)
    filtered_molecules = find_similar_elements(molecules, similarity_matrix, tols, tole)

    return filtered_molecules
#------------------------------------------------------------------------------------------
def comparator_usr_batch(molecules, batch_size=100, tols=tolsij, tole=tolene, mono=False):
    """
    Batch-processing USR comparator (no multiprocessing).
    Useful when multiprocessing is unreliable or not desired.
    Processes molecules in batches, then applies a second-pass filter across batches.
    """
    start = time.time()
    ni = len(molecules)

    if ni == 0:
        return []

    molecules = sort_by_energy(molecules, 1)

    # If the list is small, run the serial comparator directly
    if ni <= batch_size:
        return comparator_usr_serial(molecules, tols, tole, mono)

    # Process in batches
    all_filtered_mols = []
    n_batches = (ni + batch_size - 1) // batch_size

    for i in range(n_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, ni)
        batch = molecules[start_idx:end_idx]

        filtered_batch = comparator_usr_serial(batch, tols, tole, mono)
        all_filtered_mols.extend(filtered_batch)

    # Second pass filtering between batches to remove cross-batch duplicates
    if len(all_filtered_mols) > 1:
        all_filtered_mols = _second_pass_filtering(all_filtered_mols, tols, tole, mono)

    # Sort final list by energy
    all_filtered_mols = sort_by_energy(all_filtered_mols, 1)

    nf = len(all_filtered_mols)
    end = time.time()
    print('USR comparison (batch) at %5.2f s [%d -> %d]' % (end - start, ni, nf))

    return all_filtered_mols

#------------------------------------------------------------------------------------------
# Additional functions for comparison against references
#------------------------------------------------------------------------------------------

def make_similarity_matrix_compare(moleculein, moleculeref, mono=False):
    """
    Build a cross-similarity matrix between two molecule lists.
    Returns a (len(moleculein) x len(moleculeref)) numpy array of similarities.
    """
    n_features = 8 if mono else 16

    # Compute descriptors for both sets
    if mono:
        descriptors1 = [USRMonoatom(mol) for mol in moleculein]
        descriptors2 = [USRMonoatom(mol) for mol in moleculeref]
    else:
        descriptors1 = [USRMultiatom(mol) for mol in moleculein]
        descriptors2 = [USRMultiatom(mol) for mol in moleculeref]

    total_molecules1, total_molecules2 = len(moleculein), len(moleculeref)
    similarity_matrix = np.zeros((total_molecules1, total_molecules2), dtype=float)

    # Fill the matrix
    for i in range(total_molecules1):
        vi = descriptors1[i]
        for j in range(total_molecules2):
            vj = descriptors2[j]
            similarity_matrix[i, j] = similarity_numba(vi, vj, n_features)

    return similarity_matrix
#------------------------------------------------------------------------------------------
def molin_sim_molref(moleculein, moleculeref, tols=tolsij, tole=tolene, mono=False):
    """
    Compare molecules in 'moleculein' against reference set 'moleculeref'.
    Removes molecules from 'moleculein' that are similar to any reference
    (similarity >= tols and |DeltaE| <= tole).
    Returns the filtered moleculein list.
    """
    start = time.time()
    ni = len(moleculein)

    matrixs = make_similarity_matrix_compare(moleculein, moleculeref, mono)

    similares = []
    for i, imol in enumerate(moleculein):
        for j, jmol in enumerate(moleculeref):
            if (matrixs[i, j] >= tols) and (np.abs(imol.info['e'] - jmol.info['e']) <= tole):
                similares.append(i)
                break

    moleculeout = [imol for i, imol in enumerate(moleculein) if i not in similares]
    nf = len(moleculeout)
    end = time.time()
    print('USR comparison (vs reference) at %5.2f s [%d -> %d]' % (end - start, ni, nf))
    return moleculeout
#------------------------------------------------------------------------------------------

