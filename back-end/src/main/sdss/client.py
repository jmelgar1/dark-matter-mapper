import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from src.main.sdss.util.exceptions import APIRequestError, EmptyResponseError
from src.main.sdss.util.validators import validate_coordinates
from src.main.sdss.query.query_builder import build_galaxy_query
import logging

logger = logging.getLogger(__name__)


def _parse_response(response_data):
    """Parse raw API response"""
    if not response_data or not isinstance(response_data, list):
        logger.warning("Received empty API response")
        raise EmptyResponseError("No data returned from SDSS API")

    rows = response_data[0].get("Rows", [])
    if not rows:
        raise EmptyResponseError("No galaxies found in response")

    return rows


class SDSSClient:
    BASE_URL = "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch"

    def __init__(self, timeout=30):
        self.timeout = timeout

    @retry(wait=wait_exponential(multiplier=1, min=4, max=60),
           stop=stop_after_attempt(3),
           reraise=True)
    def fetch_galaxies(self, ra_min, ra_max, dec_min, dec_max, **kwargs):
        """
        Main entry point for galaxy data fetching
        """
        validate_coordinates(ra_min, ra_max, dec_min, dec_max)
        query = build_galaxy_query(ra_min, ra_max, dec_min, dec_max, **kwargs)
        return self._execute_query(query)

    def _execute_query(self, query):
        """Execute SQL query against SDSS API"""
        try:
            response = requests.post(
                self.BASE_URL,
                params={'cmd': query, 'format': 'json'},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "DarkMatterMapper/1.0"
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return _parse_response(response.json())

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIRequestError(f"API communication error: {str(e)}")