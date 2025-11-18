#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def oem_rep(CIF_file, output_path='YOUR_PATH_OUTPUT', basis_set='pcseg-0', int_type='TM', PCA_red=None, norm=False, sort=False):
    import os
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from ase import io
    from pyscf import lo
    from pyscf.pbc import gto
    from pathlib import Path

    # Validate int_type
    allowed_int_type = {"TM", "VM", "SM"}
    if int_type not in allowed_int_type:
        raise ValueError(f"int_type must be one of {allowed_int_type}, but got '{int_type}'")

    # Validate CIF path
    if not (CIF_file.lower().endswith(".cif") and os.path.isfile(CIF_file)):
        print(f"Error: {CIF_file} is not a valid .cif file path")
        return

    # Read CIF
    cif = io.read(CIF_file, index=0)
    coord = pd.concat([
        pd.DataFrame(cif.get_chemical_symbols()),
        pd.DataFrame(cif.get_positions())
    ], axis=1).to_string(header=False,index=False,index_names=False).replace('\n', ' ; ')

    # Build periodic cell
    cell = gto.Cell()
    cell.atom = coord
    cell.basis = basis_set
    cell.pseudo = 'gth-pade'

    try:
        cell.a = np.eye(3) * cif.cell
    except AttributeError:
        cell.a = cif.cell
    cell.build()

    # Compute one-electron integrals
    if int_type=='TM':
        rep_mat = cell.pbc_intor('int1e_kin') # Generating the kinetic energy matrix (TM representation)
    elif int_type=='VM':
        rep_mat = cell.pbc_intor('int1e_nuc') # Generating the nuclear attraction matrix (VM representation)
    elif int_type=='SM':
        rep_mat = cell.pbc_intor('int1e_ovlp') # Generating the overlap matrix (SM representation)

    # Normalization
    if norm:
        trace_T = np.trace(rep_mat)
        if trace_T != 0:
            rep_mat /= trace_T
        rep_mat = (rep_mat - rep_mat.mean()) / rep_mat.std()

    # Sorting
    if sort:
        ao_labels = cell.ao_labels(fmt=False)
        atom_indices = [ao[1] for ao in ao_labels]
        sort_order = np.argsort(atom_indices)
        rep_mat = rep_mat[np.ix_(sort_order, sort_order)]

    # PCA
    if PCA_red is not None:
        pca = PCA(n_components=PCA_red)
        rep_mat = pca.fit_transform(rep_mat)

    # Output path handling
    path = Path(CIF_file)
    filename = path.stem

    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    np.save(output_dir / f"{filename}_{int_type}.npy", rep_mat,allow_pickle=False)

