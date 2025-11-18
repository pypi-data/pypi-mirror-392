"""HTTP client for Fantasy NBA backend API."""

import httpx
from typing import Dict, Any

BACKEND_API_URL = "https://fantasyaverageweb.onrender.com/api"
TIMEOUT = 10


def make_api_request(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make an API request with error handling.
    
    Args:
        endpoint: API endpoint (e.g., "/teams/", "/players/")
        params: Optional query parameters
    
    Returns:
        JSON response as dictionary or error dict
    """
    try:
        response = httpx.get(
            f"{BACKEND_API_URL}{endpoint}",
            params=params or {},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except httpx.TimeoutException:
        return {"error": "Request timed out. Backend may be slow or unavailable."}
    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {str(e)}"}

