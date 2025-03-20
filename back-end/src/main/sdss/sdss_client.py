import logging
from src.main.sdss.client import SDSSClient
from src.main.sdss.processing.parser import parse_to_dataframe, filter_galaxies
from src.main.sdss.processing.preprocessor import convert_to_cartesian, create_voxel_grid

logger = logging.getLogger(__name__)

def fetch_sdss_galaxies(ra_min, ra_max, dec_min, dec_max, **kwargs):
    """High-level interface for galaxy data pipeline"""
    client = SDSSClient()
    try:
        raw_data = client.fetch_galaxies(ra_min, ra_max, dec_min, dec_max, **kwargs)
        df = parse_to_dataframe(raw_data)
        return filter_galaxies(df)
    except Exception as e:
        logger.error(f"Galaxy fetch pipeline failed: {str(e)}")
        raise

def preprocess_to_3d_voxels(df, voxel_size=50):
    """Complete preprocessing pipeline"""
    try:
        coordinates = convert_to_cartesian(df)
        return create_voxel_grid(coordinates, voxel_size)
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        raise