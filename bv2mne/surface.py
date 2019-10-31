#!/usr/bin/env python

# Author: Alexandre Fabre <alexandre.fabre22@gmail.com>

# Modified by David Meunier <david.meunier@univ-amu.fr>

# from mayavi import mlab
import numpy as np
import mne
from mne import Label
from mne.surface import complete_surface_info
from mne.io.constants import FIFF

from nibabel import gifti

from scipy.stats import rankdata
from bv2mne.utils import  compute_trans, read_texture_info


def get_surface(fname, subject, hemi, trans=None):
    """get surface whith a file

    Parameters
    ----------
    fname : str
        Filename of the surface
    subject : str
        Name of the subject
    hemi : 'lh' | 'rh'
        Hemisphere of interest
    trans : str | array | None
        The matrix transformation or the filename to get this

    Returns
    -------
    surface : instance of Surface
    -------
    Author : Alexandre Fabre
    """

    try:
        coords, triangles = mne.read_surface(fname)
    except Exception:
        try:
            giftiImage = gifti.read(fname)

            coords = giftiImage.darrays[0].data
            triangles = giftiImage.darrays[1].data
        except Exception:
            raise Exception('surface file must be in FreeSurfer or BrainVisa format')

    # Apply trans to coords
    coords = compute_trans(coords, trans) ######################

    # Locations in meters
    coords = coords * 1e-3

    inuse = np.ones(len(coords), dtype=int)
    remains = len(coords)

    if hemi == 'lh':
        Id = 101
    elif hemi == 'rh':
        Id = 102

    # Creating surface dict
    surface = {'rr': coords, 'coord_frame': np.array((FIFF.FIFFV_COORD_MRI), np.int32), 'tris': triangles,
               'ntri': len(triangles), 'use_tris': None, 'np': len(coords), 'inuse': inuse, 'nuse_tris': 0,
               'nuse': remains, 'subject_his_id': subject, 'type': 'surf', 'id': Id, 'nearest': None, 'dist': None}

    surface = mne.surface.complete_surface_info(surface)

    return surface

def get_surface_labels(surface, texture, subject='S4', hemi='lh',
                      fname_atlas=None, fname_color=None):
    """get areas on the surface

    Parameters
    ----------
    surface : instance of Surface
    texture : str | array
        Array to get areas or the filename to get this
    subject : str
        Name of the subject
    hemi : 'lh' | 'rh'
        Name of the hemisphere
    fname_atlas : str | None
        Filename for area atlas
    fname_color : str | None
        Filename for area color

    Returns
    -------
    areas : list of Surface object
    -------
    Author : Alexandre Fabre
    """

    labels = []

    rr = surface['rr']
    # normals = surface['nn']

    # Get texture with gifti format (BainVisa)= labels of MarsAtlas
    if isinstance(texture, str):
        giftiImage = gifti.giftiio.read(texture)
        base_values = giftiImage.darrays[0].data

    else:
        base_values = texture

    values = base_values

    # get parcels and count the number of nodes in each parcel (count)
    parcels, counts = np.unique(values, return_counts=True)

    # get parcels information
    info = read_texture_info(fname_atlas, hemi)

    # get triangles for whole surface
    triangles = surface['tris']
    total_nodes = 0
    for pos, val in enumerate(parcels):

        name_process = info.get(parcels[pos], False)
        if not name_process:
            name = 'no_name'
            # lobe = 'no_name'
        else:
            name = name_process[0]
            # lobe = name_process[1]

        # Find index for nodes of the parcel
        ind = np.where(values == val)

        # Keep only those nodes and pos of parcel that are associated with a
        # face (triangle) in its parcel
        # get triangles where points of the parcel are
        ix = np.in1d(triangles.ravel(), ind).reshape(triangles.shape)

        # Counting the number of True per lines --> True : 1 , False : 0
        # to know how many points of the parcel are in each face
        counts = ix.sum(1)

        # Indices of each triangles that contains 3 points of the parcel
        ind_all = np.where(counts == 3)
        tris_cour = triangles[ind_all]

        # Select nodes that are connected through triangles
        nodes = np.unique(tris_cour)
        iy = np.in1d(ind, nodes)
        ind_n = np.where(iy)
        ind_n = ind_n[0]
        ind = ind[0]

        # Positions and normals
        rr_parcel = rr[ind[ind_n]]
        # normals_parcel = normals[ind[ind_n]]

        # Textures (values)
        values_parcel = values[ind[ind_n]]

        # Locations in meters
        # rr_parcel = rr_parcel * 1e-3

        # Number of nodes
        nodes, tmp = rr_parcel.shape
        vertex_ind = np.arange(total_nodes, total_nodes + nodes, 1)
        total_nodes = total_nodes + nodes  # (was =+???)

        label = Label(vertices=vertex_ind, pos=rr_parcel, values=values_parcel, hemi=hemi,
                      comment=name, name=name, filename=None, subject=subject, verbose=None)

        labels.append(label)

    return labels