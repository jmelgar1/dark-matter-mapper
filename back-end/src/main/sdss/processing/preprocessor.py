from astropy import coordinates as coords
from astropy import units as u
import numpy as np

def convert_to_cartesian(df) -> np.ndarray:
    """Convert RA/dec/redshift to 3D Cartesian coordinates"""
    sky_coords = coords.SkyCoord(
        ra=df['ra'].values * u.degree,
        dec=df['dec'].values * u.degree,
        distance=df['redshift'].values * u.Mpc,
        frame='icrs'
    )
    return sky_coords.cartesian.xyz.value.T

def create_voxel_grid(coordinates, voxel_size=50) -> np.ndarray:
    """Convert 3D coordinates to density voxel grid"""
    return np.histogramdd(coordinates, bins=(voxel_size, voxel_size, voxel_size))[0]