from datetime import datetime
from typing import Dict, Any


def build_audit_log(
    decision_id: str,
    workload: Dict[str, Any],
    result: Dict[str, Any],
    approval_status: str,
) -> Dict[str, Any]:
    """
    Build a standardized audit log for one scheduling decision.
    This object is used for JSON export and MongoDB decision memory.
    """

    best = result["best_option"]
    lowest_carbon = result["lowest_carbon_option"]

    audit_log = {
        "decision_id": decision_id,
        "decision_timestamp": datetime.now().isoformat(),
        "workload": workload["job"],
        "workload_details": {
            "duration_hours": workload["duration_hours"],
            "deadline_hours": workload["deadline_hours"],
            "delay_tolerant": workload["delay_tolerant"],
            "energy_kwh": workload["energy_kwh"],
        },
        "selected_region": best["region"],
        "selected_time": best["hour"],
        "hours_from_now": best.get("hours_from_now"),
        "finish_within_hours": best.get("finish_within_hours"),
        "deadline_violation": best.get("deadline_violation", False),
        "carbon_intensity": best["carbon_intensity"],
        "grid_load": best["grid_load"],
        "latency_score": best["latency_score"],
        "score": best["score"],
        "score_breakdown": best.get("score_breakdown", {}),
        "decision_reason_codes": result.get("decision_reason_codes", []),
        "approval_required": best["approval_required"],
        "approval_status": approval_status,
        "selected_emissions_kg": result["selected_emissions_kg"],
        "lowest_carbon_emissions_kg": result["lowest_carbon_emissions_kg"],
        "carbon_delta_vs_lowest_kg": result["carbon_delta_vs_lowest_kg"],
        "lowest_carbon_region": lowest_carbon["region"],
        "lowest_carbon_time": lowest_carbon["hour"],
        "lowest_carbon_intensity": lowest_carbon["carbon_intensity"],
        "lowest_carbon_grid_load": lowest_carbon["grid_load"],
        "grid_stress_avoided": result["grid_stress_avoided"],
        "data_source": result.get("data_source", "mock_synthetic_mvp"),
        "scheduler_version": "mvp_weighted_scoring_v1",
    }

    return audit_log