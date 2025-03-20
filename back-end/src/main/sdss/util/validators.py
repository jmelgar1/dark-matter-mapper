from src.main.sdss.util.exceptions import InvalidCoordinatesError


def validate_coordinates(ra_min: float, ra_max: float, dec_min: float, dec_max: float):
    """Validate coordinate ranges"""
    if not (0 <= ra_min <= 360) or not (0 <= ra_max <= 360):
        raise InvalidCoordinatesError("RA must be between 0 and 360 degrees")
    if not (-90 <= dec_min <= 90) or not (-90 <= dec_max <= 90):
        raise InvalidCoordinatesError("Dec must be between -90 and 90 degrees")
    if ra_min >= ra_max:
        raise InvalidCoordinatesError("ra_min must be less than ra_max")
    if dec_min >= dec_max:
        raise InvalidCoordinatesError("dec_min must be less than dec_max")