"""
MCP Tool Definitions
Wraps API functions with @mcp.tool()
"""

from typing import Optional
from .server import mcp  # Import the mcp instance from server.py
from . import api       # Import the API logic

async def _call_api_safely(api_func, *args, **kwargs):
    """Wrapper to catch ApiErrors and return them as dicts."""
    try:
        return await api_func(*args, **kwargs)
    except api.ApiError as e:
        return e.to_dict()
    except Exception as e:
        return {
            "error": "An unexpected error occurred",
            "details": str(e)
        }

@mcp.tool()
async def list_abacum_models() -> dict:
    """
    List all models from Abacum API.

    Returns a list of models with their details including:
    - id: Model unique identifier
    - name: Model name
    - code: Model code
    - restricted: Whether the model is restricted
    - last_actuals_date: Date of last actuals
    - created_at: Creation timestamp
    - updated_at: Last update timestamp

    Returns:
        Dictionary containing list of models and metadata
    """
    return await _call_api_safely(api.list_models)

@mcp.tool()
async def list_abacum_scenarios() -> dict:
    """
    List all scenarios from Abacum API.

    Returns a list of scenarios with their details including:
    - id: Scenario unique identifier
    - version_name: Version name
    - version_category: Category (Forecast/Budget)
    - version_active: Whether version is active
    - scenario_name: Scenario name
    - scenario_default: Whether it's the default scenario
    - starts: Start date
    - ends: End date
    - is_locked: Whether scenario is locked

    Returns:
        Dictionary containing list of scenarios and metadata
    """
    return await _call_api_safely(api.list_scenarios)


@mcp.tool()
async def get_abacum_model_actuals(
    model_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get actuals data for a specific Abacum model.

    Args:
        model_id: The ID of the model to retrieve actuals for
        start_date: Optional start date in YYYY-MM format (e.g., "2024-01")
        end_date: Optional end date in YYYY-MM format (e.g., "2024-12")

    Returns:
        Dictionary containing:
        - model_data_url: temporary URL to download the actuals data
        - metadata: Schema information about the data structure
    """
    return await _call_api_safely(
        api.get_model_actuals,
        model_id=model_id, start_date=start_date, end_date=end_date
    )

@mcp.tool()
async def get_abacum_scenario_data(
    model_id: str,
    scenario_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get scenario data for a specific Abacum model and scenario.

    Args:
        model_id: The ID of the model
        scenario_id: The ID of the scenario to retrieve data for
        start_date: Optional start date in YYYY-MM format (e.g., "2024-01")
        end_date: Optional end date in YYYY-MM format (e.g., "2024-12")

    Returns:
        Dictionary containing:
        - model_data_url: temporary URL to download the actuals data
        - metadata: Schema information about the data structure
    """
    return await _call_api_safely(
        api.get_scenario_data,
        model_id=model_id, scenario_id=scenario_id,
        start_date=start_date, end_date=end_date
    )

@mcp.tool()
async def get_abacum_rolling_data(
    model_id: str,
    scenario_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get rolling forecast data for a specific Abacum model and scenario.

    Args:
        model_id: The ID of the model
        scenario_id: The ID of the scenario to retrieve rolling data for
        start_date: Optional start date in YYYY-MM format (e.g., "2024-01")
        end_date: Optional end date in YYYY-MM format (e.g., "2024-12")

    Returns:
        Dictionary containing:
        - model_data_url: temporary URL to download the actuals data
        - metadata: Schema information about the data structure
    """
    return await _call_api_safely(
        api.get_rolling_data,
        model_id=model_id, scenario_id=scenario_id,
        start_date=start_date, end_date=end_date
    )