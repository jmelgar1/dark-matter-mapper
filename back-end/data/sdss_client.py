import numpy as np
import requests
import pandas as pd
from astropy import coordinates as coords
from astropy import units as u


def fetch_sdss_galaxies(ra_min, ra_max, dec_min, dec_max, redshift_max=0.3):
    """Fetches galaxies from SDSS within a sky region and redshift range."""
    query = f"""
    SELECT ra, dec, redshift, g, r, i 
    FROM SpecObj 
    WHERE 
      ra BETWEEN {ra_min} AND {ra_max}
      AND dec BETWEEN {dec_min} AND {dec_max}
      AND redshift BETWEEN 0 AND {redshift_max}
    LIMIT 1000  # starting small for testing
    """
    url = "https://skyserver.sdss.org/dr16/SkyServerWS/SearchTools/SqlSearch"
    response = requests.get(url, params={"cmd": query, "format": "json"})
    data = response.json()

    if "Rows" not in data:
        raise ValueError("No data returned from SDSS")

    df = pd.DataFrame(data["Rows"])
    return df


def preprocess_to_3d_voxels(df, voxel_size=50):
    """Convert galaxy positions to 3D voxel grid."""
    # Convert RA/dec/redshift to Cartesian coordinates
    sky_coords = coords.SkyCoord(
        ra=df['ra'] * u.degree,
        dec=df['dec'] * u.degree,
        distance=df['redshift'] * u.Mpc, #redshift is treated as distance (not really but kinda)
        frame='icrs'
    )

    cartesian_coords = sky_coords.cartesian.xyz.value.T

    # Bin into voxels, here we create histogram where each voxel has a certain amount of galaxies.
    # we are splitting it all into bins, where each bin may or may not have galaxies in it.
    voxel_grid, edges = np.histogramdd(cartesian_coords, bins=(voxel_size, voxel_size, voxel_size))
    return voxel_grid