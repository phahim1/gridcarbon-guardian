from typing import Dict, List, Any

from data import workloads, schedule_options


def get_workloads() -> List[Dict[str, Any]]:
    """
    Return available workload definitions.

    MVP: returns static demo workloads from data.py.
    Future: can load workloads from API, database, queue, or user input.
    """
    return workloads


def get_schedule_options(use_live_data: bool = False) -> List[Dict[str, Any]]:
    """
    Return candidate schedule options.

    MVP: returns static/synthetic schedule options from data.py.

    Future:
    - if use_live_data=True, fetch carbon intensity from Electricity Maps API
    - fetch or synthesize grid-load data
    - merge both into candidate scheduling windows
    """

    if use_live_data:
        # Placeholder for future real API integration.
        # For now, return mock/synthetic data safely.
        return schedule_options

    return schedule_options


def get_data_source_label(use_live_data: bool = False) -> str:
    if use_live_data:
        return "mock_fallback_live_mode_not_enabled"

    return "mock_synthetic_mvp"