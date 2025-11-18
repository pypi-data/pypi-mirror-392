"""
Abacum API Client
Handles OAuth2 authentication and data fetching.
"""

import httpx
import os
import sys
import csv
import json
from io import StringIO
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Abacum API Configuration
ABACUM_API_BASE = "https://api.abacum.io"
ABACUM_TOKEN_URL = f"{ABACUM_API_BASE}/server-authentication/oauth2/token/"

# Token cache (to avoid requesting a new token for every call)
_token_cache = {
    "access_token": None,
    "expires_at": None
}


class ApiError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    def to_dict(self):
        return {
            "error": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


def get_api_credentials() -> (str, str):
    """
    Get Abacum API credentials from environment variables.

    Reads from the variable names specified in the CLIENTS.md setup.
    """
    client_id = os.getenv("ABACUM_API_CLIENT_ID")
    client_secret = os.getenv("ABACUM_API_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ApiError(
            "Abacum API credentials not found. "
            "Please set ABACUM_API_CLIENT_ID and ABACUM_API_CLIENT_SECRET environment variables."
        )
    return client_id, client_secret


async def get_abacum_access_token() -> str:
    """
    Get or refresh the Abacum API access token using OAuth2 client credentials flow.
    Tokens are cached and automatically refreshed when expired.
    """
    # Check if we have a valid cached token
    if _token_cache["access_token"] and _token_cache["expires_at"]:
        if datetime.now() < _token_cache["expires_at"]:
            return _token_cache["access_token"]

    # Get credentials
    client_id, client_secret = get_api_credentials()

    # Request a new token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ABACUM_TOKEN_URL,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx

            token_data = response.json()
            access_token = token_data.get("access_token")

            # Tokens expire in 1 week, cache with a 5-min buffer
            expires_in = token_data.get("expires_in", 604800)  # Default 7 days
            expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            # Cache the token
            _token_cache["access_token"] = access_token
            _token_cache["expires_at"] = expires_at

            return access_token

        except httpx.HTTPStatusError as e:
            raise ApiError(
                f"Failed to get access token: {e.response.status_code}",
                status_code=e.response.status_code,
                details=e.response.text
            )
        except Exception as e:
            raise ApiError(f"Failed to get access token: {str(e)}")


async def _make_api_request(url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Helper function to make authenticated GET requests."""
    access_token = await get_abacum_access_token()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ApiError("Authentication failed. Please check your Abacum API credentials.", 401)
            if e.response.status_code == 403:
                raise ApiError("Access forbidden. You may not have permission.", 403)
            if e.response.status_code == 404:
                raise ApiError("Resource not found.", 404)
            raise ApiError(
                f"API request failed with status {e.response.status_code}",
                status_code=e.response.status_code,
                details=e.response.text
            )
        except Exception as e:
            raise ApiError(f"API request failed: {str(e)}")


async def _fetch_csv_as_json(csv_url: str) -> Optional[str]:
    """Fetches data from a pre-signed CSV URL and converts it to a JSON string."""
    if not csv_url:
        return None

    async with httpx.AsyncClient() as client:
        try:
            csv_response = await client.get(csv_url)
            csv_response.raise_for_status()

            # Read CSV text into a string buffer
            csv_file = StringIO(csv_response.text)

            # Use csv.DictReader to get a list of dictionaries
            reader = csv.DictReader(csv_file)
            data_list = list(reader)

            # Convert list of dicts to JSON string
            return json.dumps(data_list)

        except Exception:
            # Failed to fetch or parse CSV, return None
            return None


async def list_models() -> dict:
    """Fetches all models from Abacum API."""
    data = await _make_api_request(f"{ABACUM_API_BASE}/public-api/models")
    return {
        "success": True,
        "models": data.get("data", []),
        "count": len(data.get("data", [])),
        "timestamp": datetime.now().isoformat()
    }


async def list_scenarios() -> dict:
    """Fetches all scenarios from Abacum API."""
    data = await _make_api_request(f"{ABACUM_API_BASE}/public-api/scenarios")
    return {
        "success": True,
        "scenarios": data.get("data", []),
        "count": len(data.get("data", [])),
        "timestamp": datetime.now().isoformat()
    }


async def _get_model_data(
        endpoint: str,
        model_id: str,
        scenario_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> dict:
    """Generic function to fetch model data (actuals, scenario, rolling)."""

    if (start_date and not end_date) or (end_date and not start_date):
        raise ApiError("Both start_date and end_date must be provided together")

    # Build URL
    if scenario_id:
        url = f"{ABACUM_API_BASE}/public-api/models/{model_id}/{endpoint}/{scenario_id}"
    else:
        url = f"{ABACUM_API_BASE}/public-api/models/{model_id}/{endpoint}"

    params = {}
    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date

    data = await _make_api_request(url, params=params)

    # Fetch CSV data from the pre-signed URL and convert to JSON
    module_data_json = await _fetch_csv_as_json(data.get("data"))

    return {
        "success": True,
        "model_id": model_id,
        "scenario_id": scenario_id,
        "metadata": data.get("metadata"),
        "module_data_json": module_data_json,
        "timestamp": datetime.now().isoformat()
    }


async def get_model_actuals(
        model_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> dict:
    return await _get_model_data(
        "actuals_data", model_id,
        start_date=start_date, end_date=end_date
    )


async def get_scenario_data(
        model_id: str,
        scenario_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> dict:
    return await _get_model_data(
        "scenario_data", model_id, scenario_id,
        start_date=start_date, end_date=end_date
    )


async def get_rolling_data(
        model_id: str,
        scenario_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
) -> dict:
    return await _get_model_data(
        "rolling_data", model_id, scenario_id,
        start_date=start_date, end_date=end_date
    )