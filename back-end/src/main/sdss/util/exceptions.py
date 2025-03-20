class SDSSClientError(Exception):
    """Base class for SDSS client exceptions"""


class InvalidCoordinatesError(SDSSClientError):
    """Raised for invalid coordinate parameters"""


class EmptyResponseError(SDSSClientError):
    """Raised when API returns no data"""


class APIRequestError(SDSSClientError):
    """Raised for HTTP/API communication issues"""