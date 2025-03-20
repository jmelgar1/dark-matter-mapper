import pandas as pd
from src.main.sdss.util.exceptions import EmptyResponseError


def parse_to_dataframe(rows) -> pd.DataFrame:
    """Convert API response rows to DataFrame"""
    if not rows:
        raise EmptyResponseError("No data to parse")

    df = pd.DataFrame(rows)

    if df.empty:
        raise EmptyResponseError("Empty DataFrame after parsing")

    # Clean and type conversion
    for band in ['mag_g', 'mag_r', 'mag_i']:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    return df.dropna()


def filter_galaxies(df, max_redshift=0.3) -> pd.DataFrame:
    """Apply post-processing filters"""
    return df.query(f"redshift <= {max_redshift}")