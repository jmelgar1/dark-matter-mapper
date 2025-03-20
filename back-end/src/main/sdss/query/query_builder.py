def build_galaxy_query(
    ra_min: float,
    ra_max: float,
    dec_min: float,
    dec_max: float,
    redshift_max: float = 0.3,
    max_galaxies: int = 1000
) -> str:
    """Construct SQL query for galaxy data"""
    return f"""
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
            AND s.class = 'GALAXY'
        """.strip()