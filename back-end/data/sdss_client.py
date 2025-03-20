import logging

import numpy as np
import requests
import pandas as pd
from astropy import coordinates as coords
from astropy import units as u

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_sdss_galaxies(
        ra_min: float,
        ra_max: float,
        dec_min: float,
        dec_max: float,
        redshift_max: float = 0.3,
        max_galaxies: int = 1000
) -> pd.DataFrame:
    """
    Fetch galaxy data from SDSS DR17 within specified coordinates.
    """
    # Validate parameters
    if not (0 <= ra_min <= 360) or not (0 <= ra_max <= 360):
        raise ValueError("RA must be between 0 and 360 degrees")
    if not (-90 <= dec_min <= 90) or not (-90 <= dec_max <= 90):
        raise ValueError("Dec must be between -90 and 90 degrees")
    if ra_min >= ra_max:
        raise ValueError("ra_min must be less than ra_max")
    if dec_min >= dec_max:
        raise ValueError("dec_min must be less than dec_max")

    # Build query
    query = f"""
      SELECT TOP {max_galaxies}
          p.ra, p.dec, s.z as redshift,
          p.modelMag_g as mag_g, p.modelMag_r as mag_r, p.modelMag_i as mag_i
      FROM PhotoPrimary AS p
      JOIN SpecObj AS s ON s.bestobjid = CONVERT(varchar(24), p.objid, 1)
      WHERE
          p.ra BETWEEN {ra_min} AND {ra_max}
          AND p.dec BETWEEN {dec_min} AND {dec_max}
          AND s.z BETWEEN 0 AND {redshift_max}
          AND p.clean = 1
          AND s.class = 'GALAXY'  -- Proper SQL comment syntax
      """.strip()

    logger.debug(f"SDSS Query:\n{query}")

    try:
        # Use params instead of data for proper encoding
        response = requests.post(
            "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch",
            params={
                'cmd': query,
                'format': 'json'
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "user"
            },
            timeout=30
        )

        # Add debug logging for raw response
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text[:500]}")

        response.raise_for_status()

        data = response.json()

        if not data or "Rows" not in data:
            logger.warning("No galaxies found in this region")
            return pd.DataFrame()

        df = pd.DataFrame(data["Rows"])

        if df.empty:
            return pd.DataFrame()

        # Convert magnitudes to numeric
        for band in ['mag_g', 'mag_r', 'mag_i']:
            df[band] = pd.to_numeric(df[band], errors='coerce')

        return df.dropna()

    except requests.exceptions.RequestException as e:
        logger.error(f"SDSS API request failed: {str(e)}")
        raise RuntimeError(f"SDSS API Error: {str(e)}")
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse SDSS response: {str(e)}")
        raise RuntimeError(f"Data parsing error: {str(e)}")


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