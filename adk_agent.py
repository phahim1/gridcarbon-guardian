from google.adk import Agent

from data_sources import get_workloads, get_schedule_options
from scheduler import recommend_schedule
from audit import build_audit_log
from mongodb_mcp_tools import (
    test_mongodb_memory,
    load_recent_decisions,
    save_carbon_decision,
    load_audit_ledger,
)


def schedule_gridcarbon_workload(workload_name: str) -> dict:
    """
    ADK tool: schedule an AI/data-centre workload using carbon,
    grid-stress, deadline, governance, and MongoDB decision memory.
    """

    workloads = get_workloads()
    schedule_options = get_schedule_options(use_live_data=False)

    workload = next(
        (item for item in workloads if item["job"].lower() == workload_name.lower()),
        workloads[0],
    )

    memory_status = test_mongodb_memory()
    recent_memory = load_recent_decisions(workload["job"], limit=3)

    result = recommend_schedule(workload, schedule_options)

    approval_status = (
        "pending" if result["best_option"]["approval_required"] else "auto-approved"
    )

    audit_log = build_audit_log(
        decision_id=f"ADK-GCG-{workload['job'].replace(' ', '-').lower()}",
        workload=workload,
        result=result,
        approval_status=approval_status,
    )

    save_result = save_carbon_decision(audit_log)

    return {
        "agent": "GridCarbon Guardian ADK Agent",
        "workload": workload,
        "memory_status": memory_status,
        "recent_mongodb_memory": recent_memory,
        "recommended_schedule": result["best_option"],
        "grid_stress_avoided": result["grid_stress_avoided"],
        "approval_status": approval_status,
        "audit_save_result": save_result,
        "audit_log": audit_log,
    }


def view_gridcarbon_audit_ledger(limit: int = 10) -> dict:
    """
    ADK tool: retrieve recent MongoDB audit-ledger records.
    """
    return {
        "agent": "GridCarbon Guardian ADK Agent",
        "ledger": load_audit_ledger(limit=limit),
    }


root_agent = Agent(
    name="gridcarbon_guardian",
    model="gemini-2.0-flash",
    description=(
        "A Gemini-powered carbon-aware and grid-stress-aware scheduling agent "
        "for AI/data-centre workloads with MongoDB decision memory."
    ),
    instruction=(
        "You are GridCarbon Guardian. Help operators schedule AI/data-centre "
        "workloads by considering carbon intensity, grid stress, deadline risk, "
        "human approval, and auditability. Use the available tools to recommend "
        "a schedule, explain the trade-off, and store/retrieve decision memory."
    ),
    tools=[
        schedule_gridcarbon_workload,
        view_gridcarbon_audit_ledger,
    ],
)