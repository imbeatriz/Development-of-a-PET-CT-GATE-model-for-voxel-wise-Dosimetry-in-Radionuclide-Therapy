from __future__ import annotations
from collections.abc import Sequence
import torch
import numpy as np
from pytomography.utils import get_1d_gaussian_kernel

def sinogram_coordinates(info: dict) -> Sequence[torch.Tensor]:
    """Obtains two tensors: the first yields the sinogram coordinates (r/theta) given two crystal IDs (shape [N_crystals_per_ring, N_crystals_per_ring, 2]), the second yields the sinogram index given two ring IDs (shape [Nrings, Nrings])

    Args:
        info (dict): PET geometry information dictionary    

    Returns:
        Sequence[torch.Tensor]: LOR coordinates and sinogram index lookup tensors
    """
    # CHANGED - SUBMODULE IS INCLUDED
    nr_sectors_trans, nr_sectors_axial, nr_modules_axial, nr_modules_trans, nr_submodules_axial, nr_submodules_trans, nr_crystals_trans, nr_crystals_axial = info['rsectorTransNr'], info['rsectorAxialNr'], info['moduleAxialNr'], info['moduleTransNr'], info['submoduleAxialNr'], info['submoduleTransNr'], info['crystalTransNr'], info['crystalAxialNr']
    nr_rings = info['NrRings']
    nr_crystals_per_ring = info['NrCrystalsPerRing']

    min_sector_difference = info['min_rsector_difference']
    min_crystal_difference = min_sector_difference * nr_modules_trans * nr_submodules_trans * nr_crystals_trans # CHANGED 

    radial_size = nr_crystals_per_ring - 2 * (min_crystal_difference - 1) - 1 # number of radial bins in the sinogram
    distance_crystal_id_0_to_first_sector_center = (nr_modules_trans * nr_submodules_trans * nr_crystals_trans) / 2 # CHANGED # offset between crystal 0 and the first rsector’s center
    lor_coordinates = np.zeros((nr_crystals_per_ring, nr_crystals_per_ring, 2)) # store (angular, radial) values for each crystal pair (LOR)
    
    # compute the radial and angular sinogram coordinates for each possible detector pair.
    for full_ring_crystal_id_1 in range(nr_crystals_per_ring):
        crystal_id_1 = (full_ring_crystal_id_1 % nr_crystals_per_ring) - distance_crystal_id_0_to_first_sector_center
        if crystal_id_1 < 0:
                crystal_id_1 += nr_crystals_per_ring
        for full_ring_crystal_id_2 in range(nr_crystals_per_ring):
            crystal_id_2 = (full_ring_crystal_id_2 % nr_crystals_per_ring) - distance_crystal_id_0_to_first_sector_center
            if crystal_id_2 < 0:
                crystal_id_2 += nr_crystals_per_ring
            id_a = 0
            id_b = 0
            if crystal_id_1 < crystal_id_2:
                id_a = crystal_id_1
                id_b = crystal_id_2
            else:
                id_a = crystal_id_2
                id_b = crystal_id_1
            radial = 0
            angular = 0
            if id_b - id_a < min_crystal_difference:
                continue
            else:
                if id_a + id_b >= (3 * nr_crystals_per_ring) / 2 or id_a + id_b < nr_crystals_per_ring / 2:
                    if id_a == id_b:
                        radial = -nr_crystals_per_ring / 2
                    else:
                        radial = ((id_b - id_a - 1) / 2) - ((nr_crystals_per_ring - (id_b - id_a + 1)) / 2)
                else:
                    if id_a == id_b:
                        radial = nr_crystals_per_ring / 2
                    else:
                        radial = ((nr_crystals_per_ring - (id_b - id_a + 1)) / 2) - ((id_b - id_a - 1) / 2)

                radial = np.floor(radial)

                if id_a + id_b < nr_crystals_per_ring / 2:
                    angular = (2 * id_a + nr_crystals_per_ring + radial) / 2
                else:
                    if id_a + id_b >= (3 * nr_crystals_per_ring) / 2:
                        angular = (2 * id_a - nr_crystals_per_ring + radial) / 2
                    else:
                        angular = (2 * id_a - radial) / 2
                lor_coordinates[full_ring_crystal_id_1, full_ring_crystal_id_2, 0] = np.floor(angular)
                lor_coordinates[full_ring_crystal_id_1, full_ring_crystal_id_2, 1] = np.floor(radial + radial_size / 2)
    sinogram_index = np.zeros((nr_rings, nr_rings))
    for ring1 in range(1, nr_rings+1):
        for ring2 in range(1, nr_rings+1):
            ring_difference = abs(ring2 - ring1)
            if ring_difference == 0:
                current_sinogram_index = ring1
            else:
                current_sinogram_index = nr_rings
                if ring1 < ring2:
                    if ring_difference > 1:
                        for ring_distance in range(1, ring_difference):
                            current_sinogram_index += 2 * (nr_rings - ring_distance)
                    current_sinogram_index += ring1
                else:
                    if ring_difference > 1:
                        for ring_distance in range(1, ring_difference):
                            current_sinogram_index += 2 * (nr_rings - ring_distance)
                    current_sinogram_index += nr_rings - ring_difference + ring1 - ring_difference
            sinogram_index[ring1-1, ring2-1] = current_sinogram_index - 1
    return torch.tensor(lor_coordinates).to(torch.long), torch.tensor(sinogram_index).to(torch.long)

# computes the inverse mapping:
# From sinogram bins (angular, radial) → back to detector coordinates (x1, y1, x2, y2)
# From ring pairs → to z-coordinates (z1, z2)
def sinogram_to_spatial(info: dict) -> Sequence[torch.Tensor]:
    """Returns two tensors: the first yields the detector coordinates (x1/y1/x2/y2) of each of the two crystals given the element of the sinogram (shape [N_crystals_per_ring, N_crystals_per_ring, 2, 2]), the second yields the ring coordinates (z1/z2) given two ring IDs (shape [Nrings*Nrings, 2])

    Args:
        info (dict): PET geometry information dictionary

    Returns:
        Sequence[torch.Tensor]: Two tensors yielding spatial coordinates
    """
    scanner_lut = get_scanner_LUT(info) # LUT maps each crystal ID to its 3D spatial coordinates (x, y, z).
    # CHANGED - ADDED SUBMODULE
    nr_sectors_trans, nr_sectors_axial, nr_modules_axial, nr_modules_trans, nr_submodules_axial, nr_submodules_trans, nr_crystals_trans, nr_crystals_axial = info['rsectorTransNr'], info['rsectorAxialNr'], info['moduleAxialNr'], info['moduleTransNr'], info['submoduleAxialNr'], info['submoduleTransNr'], info['crystalTransNr'], info['crystalAxialNr']
    nr_rings = nr_sectors_axial * nr_modules_axial * nr_submodules_axial * nr_crystals_axial # CHANGED
    nr_crystals_per_ring = nr_sectors_trans * nr_modules_trans * nr_submodules_trans * nr_crystals_trans # CHANGED
    min_sector_difference = 0
    min_crystal_difference = min_sector_difference * nr_modules_trans * nr_submodules_trans * nr_crystals_trans # CHANGED
    radial_size = int(nr_crystals_per_ring - 2 * (min_crystal_difference - 1) - 1)
    angular_size = int(nr_crystals_per_ring / 2)
    # This populates each sinogram bin with the (x, y) coordinates of both detectors forming that LOR.
    distance_crystal_id_0_to_first_sector_center = (nr_modules_trans * nr_submodules_trans * nr_crystals_trans) / 2 # CHANGED
    detector_coordinates = np.zeros((angular_size, radial_size, 2, 2), dtype=np.float32) # [N_angular_bins, N_radial_bins, 2 detectors, 2 coordinates (x/y)]
    # Generates first the coordinates on each sinogram
    for full_ring_crystal_id_1 in range(nr_crystals_per_ring):
        crystal_id_1 = full_ring_crystal_id_1 % nr_crystals_per_ring - distance_crystal_id_0_to_first_sector_center
        if crystal_id_1 < 0:
            crystal_id_1 += nr_crystals_per_ring
        for full_ring_crystal_id_2 in range(nr_crystals_per_ring):
            crystal_id_2 = full_ring_crystal_id_2 % nr_crystals_per_ring - distance_crystal_id_0_to_first_sector_center
            if crystal_id_2 < 0:
                crystal_id_2 += nr_crystals_per_ring
            id_a = 0
            id_b = 0
            if crystal_id_1 < crystal_id_2:
                id_a = crystal_id_1
                id_b = crystal_id_2
            else:
                id_a = crystal_id_2
                id_b = crystal_id_1
            radial = 0
            angular = 0
            if id_b - id_a < min_crystal_difference:
                continue
            else:
                if id_a + id_b >= (3 * nr_crystals_per_ring) / 2 or id_a + id_b < nr_crystals_per_ring / 2:
                    if id_a == id_b:
                        radial = -nr_crystals_per_ring / 2
                    else:
                        radial = ((id_b - id_a - 1) / 2) - ((nr_crystals_per_ring - (id_b - id_a + 1)) / 2)
                else:
                    if id_a == id_b:
                        radial = nr_crystals_per_ring / 2
                    else:
                        radial = ((nr_crystals_per_ring - (id_b - id_a + 1)) / 2) - ((id_b - id_a - 1) / 2)
                radial = np.floor(radial)
                if id_a + id_b < nr_crystals_per_ring / 2:
                    angular = (2 * id_a + nr_crystals_per_ring + radial) / 2
                else:
                    if id_a + id_b >= (3 * nr_crystals_per_ring) / 2:
                        angular = (2 * id_a - nr_crystals_per_ring + radial) / 2
                    else:
                        angular = (2 * id_a - radial) / 2
                if full_ring_crystal_id_1 >= full_ring_crystal_id_2:
                    detector_coordinates[int(np.floor(angular)), int(np.floor(radial + radial_size / 2)), 0, :] = scanner_lut[full_ring_crystal_id_1, 0:2]
                    detector_coordinates[int(np.floor(angular)), int(np.floor(radial + radial_size / 2)), 1, :] = scanner_lut[full_ring_crystal_id_2, 0:2]
    ring_coordinates = np.zeros((nr_rings * nr_rings, 2), dtype=np.float32)
    for ring1 in range(1, nr_rings+1):
        for ring2 in range(1, nr_rings+1):
            ring_difference = abs(ring2 - ring1)
            if ring_difference == 0:
                current_sinogram_index = ring1
            else:
                current_sinogram_index = nr_rings
                if ring1 < ring2:
                    if ring_difference > 1:
                        for ring_distance in range(1, ring_difference):
                            current_sinogram_index += 2 * (nr_rings - ring_distance)
                    current_sinogram_index += ring1
                else:
                    if ring_difference > 1:
                        for ring_distance in range(1, ring_difference):
                            current_sinogram_index += 2 * (nr_rings - ring_distance)
                    current_sinogram_index += nr_rings - ring_difference + ring1 - ring_difference
            ring_coordinates[current_sinogram_index-1, 0] = scanner_lut[info['NrCrystalsPerRing']*(ring1-1), 2]
            ring_coordinates[current_sinogram_index-1, 1] = scanner_lut[info['NrCrystalsPerRing']*(ring2-1), 2]
    return torch.tensor(detector_coordinates).to(torch.float32), torch.tensor(ring_coordinates).to(torch.float32)


def listmode_to_sinogram(
    detector_ids: torch.Tensor,
    info: dict,
    weights: torch.Tensor = None,
    normalization: bool = False,
    tof_meta: PETTOFMeta = None
    ) -> torch.Tensor:
    """Converts PET listmode data to sinogram

    Args:
        detector_ids (torch.Tensor): Listmode detector ID data
        info (dict): PET geometry information dictionary
        weights (torch.Tensor, optional): Binning weights for each listmode event. Defaults to None.
        normalization (bool, optional): Whether or not this is a normalization sinogram (need to do some extra steps). Defaults to False.
        tof_meta (PETTOFMeta, optional): PET TOF metadata. Defaults to None.

    Returns:
        torch.Tensor: PET sinogram
    """
    if tof_meta is not None: # if tof_meta is provided
        return _listmodeTOF_to_sinogramTOF(detector_ids, info, tof_meta, weights=weights)
    lor_coordinates, sinogram_index = sinogram_coordinates(info)
    detector_ids = detector_ids[:,:2] 
    within_ring_id = (detector_ids % info['NrCrystalsPerRing']).to(torch.long)
    ring_ids = (detector_ids // info['NrCrystalsPerRing']).to(torch.long)
    # Need to bin by largest "within_ring_id" first (for use with the "ring_coordinates" function yielding spatial coordinates for each ID-pair at each sinogram coordinate)
    within_ring_id, idx = within_ring_id.sort(axis=1, descending=True)
    ring_ids = ring_ids.gather(index=idx, dim=1)
    # Bin sinogram
    bin_edges = [
        torch.arange(int(info['NrCrystalsPerRing']/2)+1).to(torch.float32)-0.5,
        torch.arange(int(info['NrCrystalsPerRing'])+2).to(torch.float32)-0.5,
        torch.arange(int(info['NrRings']**2)+1).to(torch.float32)-0.5   # 
    ]
    sinogram = torch.histogramdd(
        torch.concatenate([lor_coordinates[within_ring_id[:,0], within_ring_id[:,1]], sinogram_index[ring_ids[:,0], ring_ids[:,1]].unsqueeze(1)], dim=-1).to(torch.float32),
        bin_edges,
        weight=weights
    )[0] # CHANGED
    # Opposite binning for normalization sinogram, which always considers "ring_id"s in order (this only works because of +/- z symmetry of normalization factors)
    if normalization:
        sinogram += torch.histogramdd(
            torch.concatenate([lor_coordinates[within_ring_id[:,1], within_ring_id[:,0]], sinogram_index[ring_ids[:,1], ring_ids[:,0]].unsqueeze(1)], dim=-1).to(torch.float32),
            bin_edges,
            weight=weights
        )[0]
        sinogram /= 2
    return sinogram

def _listmodeTOF_to_sinogramTOF(
    detector_ids: torch.Tensor,
    info: dict,
    tof_meta: PETTOFMeta,
    weights: torch.Tensor | None = None
    ) -> torch.Tensor:
    """Helper function to ``listmode_to_sinogram`` for TOF data

    Args:
        detector_ids (torch.Tensor): Listmode detector ID data
        info (dict): PET geometry information dictionary
        weights (torch.Tensor, optional): Binning weights for each listmode event. Defaults to None.
        tof_meta (PETTOFMeta, optional): PET TOF metadata. Defaults to None.

    Returns:
        torch.Tensor: PET TOF sinogram
    """
    lor_coordinates, sinogram_index = sinogram_coordinates(info)
    # Sort by decreasing detector ids
    # Only consider events within TOF range
    TOF_bins = detector_ids[:,2].clone()
    detector_ids = detector_ids[:,:2].clone() #.sort(axis=1, descending=True).values
    within_ring_id = (detector_ids % info['NrCrystalsPerRing']).to(torch.long)
    ring_ids = (detector_ids // info['NrCrystalsPerRing']).to(torch.long)
    # Sort by greatest value within ring (required for using various lookup tables)
    within_ring_id, idx = within_ring_id.sort(axis=1, descending=True)
    # Opposite detector order
    TOF_bins[idx[:,0]==1] = tof_meta.num_bins - 1 - TOF_bins[idx[:,0]==1]
    ring_ids = ring_ids.gather(index=idx, dim=1)
    # Bin sinogram
    bin_edges = [
        torch.arange(int(info['NrCrystalsPerRing']/2)+1).to(torch.float32)-0.5,
        torch.arange(int(info['NrCrystalsPerRing'])+2).to(torch.float32)-0.5,
        torch.arange(int(info['NrRings']**2)+1).to(torch.float32)-0.5 # CHANGED, ADDED THE MISSING NR RINGS
    ]
    data = torch.concatenate([lor_coordinates[within_ring_id[:,0], within_ring_id[:,1]], sinogram_index[ring_ids[:,0], ring_ids[:,1]].unsqueeze(1)], dim=-1).to(torch.float32)
    # Need the loop to prevent memory errors in histogramdd for large dimensionality
    sinogram = torch.empty((len(bin_edges[0])-1, len(bin_edges[1])-1, len(bin_edges[2])-1, tof_meta.num_bins), dtype=torch.float32)
    for bin in range(tof_meta.num_bins):
        if weights is None:
            weights_TOF_bin = None
        else:
            weights_TOF_bin = weights[TOF_bins==bin]
        sinogram_TOF_bin = torch.histogramdd(
            data[TOF_bins==bin],
            bin_edges,
            weight=weights_TOF_bin
        )[0]
        sinogram[...,bin] = sinogram_TOF_bin
    return sinogram

def get_detector_ids_from_trans_axial_ids(
    ids_trans_crystal: torch.Tensor,
    ids_trans_submodule: torch.Tensor,
    ids_trans_module: torch.Tensor,
    ids_trans_rsector: torch.Tensor,
    ids_axial_crystal: torch.Tensor,
    ids_axial_submodule: torch.Tensor,
    ids_axial_module: torch.Tensor,
    ids_axial_rsector: torch.Tensor,
    info: dict
) -> torch.Tensor:
    """Obtain detector IDs dynamically accounting for submodule hierarchy"""
    # Calculate ring index (axial position) - bottom up hierarchy
    ids_ring = (ids_axial_crystal +
                ids_axial_submodule * info['crystalAxialNr'] +
                ids_axial_module * info['crystalAxialNr'] * info['submoduleAxialNr'] +
                ids_axial_rsector * info['crystalAxialNr'] * info['submoduleAxialNr'] * info['moduleAxialNr'])
    
    # Calculate within-ring index (transaxial position) - bottom up hierarchy  
    ids_within_ring = (ids_trans_crystal +
                      ids_trans_submodule * info['crystalTransNr'] +
                      ids_trans_module * info['crystalTransNr'] * info['submoduleTransNr'] +
                      ids_trans_rsector * info['crystalTransNr'] * info['submoduleTransNr'] * info['moduleTransNr'])
    
    # Total crystals per ring
    nb_crystal_per_ring = (info['crystalTransNr'] * info['submoduleTransNr'] * 
                          info['moduleTransNr'] * info['rsectorTransNr'])
    
    ids_detector = ids_ring * nb_crystal_per_ring + ids_within_ring
    return ids_detector
    
def get_axial_trans_ids_from_info(
    info: dict,
    return_combinations: bool = False,
    sort_by_detector_ids: bool = False
):
    """Get axial and transaxial IDs dynamically from info dictionary"""
    # Generate IDs for each level of hierarchy
    ids_trans_crystal = torch.arange(0, info['crystalTransNr'])
    ids_axial_crystal = torch.arange(0, info['crystalAxialNr'])
    ids_trans_submodule = torch.arange(0, info['submoduleTransNr'])
    ids_axial_submodule = torch.arange(0, info['submoduleAxialNr'])
    ids_trans_module = torch.arange(0, info['moduleTransNr'])
    ids_axial_module = torch.arange(0, info['moduleAxialNr'])
    ids_trans_rsector = torch.arange(0, info['rsectorTransNr'])
    ids_axial_rsector = torch.arange(0, info['rsectorAxialNr'])
    
    # Generate all combinations
    ids_trans_crystal, ids_axial_crystal, ids_trans_submodule, ids_axial_submodule, ids_trans_module, ids_axial_module, ids_trans_rsector, ids_axial_rsector = torch.cartesian_prod(
        ids_trans_crystal, ids_axial_crystal, ids_trans_submodule, ids_axial_submodule, 
        ids_trans_module, ids_axial_module, ids_trans_rsector, ids_axial_rsector
    ).T
    
    if sort_by_detector_ids:
        ids_detector = get_detector_ids_from_trans_axial_ids(
            ids_trans_crystal, ids_trans_submodule, ids_trans_module, ids_trans_rsector,
            ids_axial_crystal, ids_axial_submodule, ids_axial_module, ids_axial_rsector, 
            info
        )
        idx_sort = torch.argsort(ids_detector)
        ids_trans_crystal = ids_trans_crystal[idx_sort]
        ids_axial_crystal = ids_axial_crystal[idx_sort]
        ids_trans_submodule = ids_trans_submodule[idx_sort]
        ids_axial_submodule = ids_axial_submodule[idx_sort]
        ids_trans_module = ids_trans_module[idx_sort]
        ids_axial_module = ids_axial_module[idx_sort]
        ids_trans_rsector = ids_trans_rsector[idx_sort]
        ids_axial_rsector = ids_axial_rsector[idx_sort]
    
    if return_combinations:
        ids_trans_crystal = torch.combinations(ids_trans_crystal, 2)
        ids_axial_crystal = torch.combinations(ids_axial_crystal, 2)
        ids_trans_submodule = torch.combinations(ids_trans_submodule, 2)
        ids_axial_submodule = torch.combinations(ids_axial_submodule, 2)
        ids_trans_module = torch.combinations(ids_trans_module, 2)
        ids_axial_module = torch.combinations(ids_axial_module, 2)
        ids_trans_rsector = torch.combinations(ids_trans_rsector, 2)
        ids_axial_rsector = torch.combinations(ids_axial_rsector, 2)
    
    return ids_trans_crystal, ids_axial_crystal, ids_trans_submodule, ids_axial_submodule, ids_trans_module, ids_axial_module, ids_trans_rsector, ids_axial_rsector

def get_scanner_LUT(info: dict):
    """Obtains scanner lookup table that dynamically accounts for submodules"""
    ids_trans_crystal, ids_axial_crystal, ids_trans_submodule, ids_axial_submodule, ids_trans_module, ids_axial_module, ids_trans_rsector, ids_axial_rsector = get_axial_trans_ids_from_info(info, sort_by_detector_ids=True)
    
    # Use values from info dictionary
    radius = info.get('radius', 391.5)
    
    # Calculate axial positions (Z) - dynamic hierarchy
    # Crystal level within submodule
    z_crystal_in_submodule = ids_axial_crystal * info['crystalAxialSpacing'] - (info['crystalAxialNr']-1) * info['crystalAxialSpacing'] / 2
    
    # Submodule level within module  
    z_submodule_in_module = ids_axial_submodule * info['submoduleAxialSpacing'] - (info['submoduleAxialNr']-1) * info['submoduleAxialSpacing'] / 2
    
    # Module level within rsector
    z_module_in_rsector = ids_axial_module * info['moduleAxialSpacing'] - (info['moduleAxialNr']-1) * info['moduleAxialSpacing'] / 2
    
    # Rsector level (axial) - usually 1 for cylindrical scanners
    z_rsector = ids_axial_rsector * info.get('rsectorAxialSpacing', 0) - (info['rsectorAxialNr']-1) * info.get('rsectorAxialSpacing', 0) / 2
    
    # Total Z position
    Z_total = z_crystal_in_submodule + z_submodule_in_module + z_module_in_rsector + z_rsector
    
    # Calculate transaxial positions - dynamic hierarchy
    # Crystal level within submodule
    y_crystal_in_submodule = ids_trans_crystal * info['crystalTransSpacing'] - (info['crystalTransNr']-1) * info['crystalTransSpacing'] / 2
    
    # Submodule level within module
    y_submodule_in_module = ids_trans_submodule * info['submoduleTransSpacing'] - (info['submoduleTransNr']-1) * info['submoduleTransSpacing'] / 2
    
    # Module level within rsector  
    y_module_in_rsector = ids_trans_module * info['moduleTransSpacing'] - (info['moduleTransNr']-1) * info['moduleTransSpacing'] / 2
    
    # Total local Y position within rsector
    local_y = y_crystal_in_submodule + y_submodule_in_module + y_module_in_rsector
    
    # Rsector angular position
    rsector_angle = ids_trans_rsector * (2 * np.pi / info['rsectorTransNr'])
    
    # Convert local coordinates to global
    # Initial rsector position (centered at radius)
    local_x = radius
    
    # Rotate to global coordinates
    global_x = local_x * torch.cos(rsector_angle) - local_y * torch.sin(rsector_angle)
    global_y = local_x * torch.sin(rsector_angle) + local_y * torch.cos(rsector_angle)
    
    # Stack coordinates (Z is typically negative in PET coordinate systems)
    XYZ_crystals = torch.vstack([global_x, global_y, -Z_total]).T
    
    return XYZ_crystals

def sinogram_to_listmode(detector_ids: torch.Tensor, sinogram: torch.Tensor, info: dict) -> torch.Tensor:
    """Obtains listmode data from a sinogram at the given detector IDs

    Args:
        detector_ids (torch.Tensor): Detector IDs at which to obtain listmode data
        sinogram (torch.Tensor): PET sinogram
        info (dict): PET geometry information dictionary

    Returns:
        torch.Tensor: Listmode data
    """     
    # TODO: multiple IDs map to same sinogram bin -> need to divide by number of LORs mapping to each sinogram bin
    lor_coordinates, sinogram_index = sinogram_coordinates(info)
    detector_ids_spatial = detector_ids[:,:2].clone()
    within_ring_id = (detector_ids_spatial % info['NrCrystalsPerRing']).to(torch.long)
    ring_ids = (detector_ids_spatial // info['NrCrystalsPerRing']).to(torch.long)
    within_ring_id, idx = within_ring_id.sort(axis=1, descending=True)
    ring_ids = ring_ids.gather(index=idx, dim=1)
    ring_ids = ring_ids.gather(index=idx, dim=1)
    lm_return = 0
    idx0, idx1 = lor_coordinates[within_ring_id[:,0], within_ring_id[:,1]].T
    idx2 = sinogram_index[ring_ids[:,0], ring_ids[:,1]]
    if len(sinogram.shape)>3: # If TOF
        idxTOF =  detector_ids[:,2].clone()
        lm_return += sinogram[idx0, idx1, idx2, idxTOF] # randoms same for all TOF bins
    else:
        lm_return += sinogram[idx0, idx1, idx2]
    return lm_return

@torch.no_grad()
def smooth_randoms_sinogram(
    sinogram_random: torch.Tensor,
    info: dict,
    sigma_r: float = 4,
    sigma_theta: float = 4,
    sigma_z: float = 4,
    kernel_size_r: int = 21,
    kernel_size_theta: int = 21,
    kernel_size_z: int = 21
    ) -> torch.Tensor:
    """Smooths a PET randoms sinogram using a Gaussian filter in the r, theta, and z direction. Rebins the sinogram into (r,theta,z1,z2) before blurring (same blurring applied to z1 and z2)

    Args:
        sinogram_random (torch.Tensor): PET sinogram of randoms
        info (dict): PET geometry information dictionary
        sigma_r (float, optional): Blurring (in pixel size) in r direction. Defaults to 4.
        sigma_theta (float, optional): Blurring (in pixel size) in r direction. Defaults to 4.
        sigma_z (float, optional): Blurring (in pixel size) in z direction. Defaults to 4.
        kernel_size_r (int, optional): Kernel size in r direction. Defaults to 21.
        kernel_size_theta (int, optional): Kernel size in theta direction. Defaults to 21.
        kernel_size_z (int, optional): Kernel size in z1/z2 diretions. Defaults to 21.

    Returns:
        torch.Tensor: Smoothed randoms sinogram
    """
    _, sinogram_index = sinogram_coordinates(info)
    sino = sinogram_random[:,:,sinogram_index]
    ktheta = get_1d_gaussian_kernel(sigma_theta, kernel_size_theta, 'circular')
    kr = get_1d_gaussian_kernel(sigma_r, kernel_size_r, 'replicate')
    kz = get_1d_gaussian_kernel(sigma_z, kernel_size_z, 'replicate')
    for i, k in enumerate([ktheta,kr,kz,kz]):
        sino = sino.swapaxes(i,3)
        sino = k(sino.flatten(end_dim=-2).unsqueeze(1)).reshape(sino.shape)
        sino = sino.swapaxes(i,3)
    ii = torch.argsort(sinogram_index.ravel())
    ix, iy = ii // sino.shape[-2], ii % sino.shape[-1]
    sinogram_random_interp = sino[:,:,ix,iy]
    return sinogram_random_interp

def randoms_sinogram_to_sinogramTOF(
    sinogram_random: torch.Tenor,
    tof_meta: PETTOFMeta,
    coincidence_timing_width: float,
) -> torch.Tensor:
    """Converts a non-TOF randoms sinogram to a TOF randoms sinogram.

    Args:
        sinogram_random (torch.Tenor): Randoms sinogram (non-TOF)
        tof_meta (PETTOFMeta): PET TOF metadata
        coincidence_timing_width (float): Coincidence timing width used for the acceptance of coincidence events

    Returns:
        torch.Tensor: Randoms sinogram (TOF)
    """
    sinogram_random *= tof_meta.bin_width / (2 * coincidence_timing_width * 0.3 / 2) # 
    return sinogram_random
