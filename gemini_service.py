from typing import Dict, Any, List, Optional

from google import genai
from google.genai.errors import APIError


MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def get_genai_client(api_key: str):
    return genai.Client(api_key=api_key)


def build_explanation_prompt(
    workload: Dict[str, Any],
    result: Dict[str, Any],
    approval_status: str,
    recent_decisions: Optional[List[Dict[str, Any]]] = None,
) -> str:
    best = result["best_option"]

    recent_context = "No prior MongoDB decisions were provided."
    if recent_decisions:
        recent_context = str(recent_decisions[:3])

    prompt = f"""
You are GridCarbon Guardian, a standards-aware scheduling agent for AI/data-centre workloads.

You must explain the deterministic scheduler result. Do not change the schedule. Do not invent values.
Use only the facts provided below.

Workload:
{workload}

Best selected option:
{best}

Score breakdown:
{best.get("score_breakdown", {})}

Decision reason codes:
{result.get("decision_reason_codes", [])}

All options:
{result["all_options"]}

Selected schedule emissions:
{result["selected_emissions_kg"]} kgCO2e

Lowest-carbon option emissions:
{result["lowest_carbon_emissions_kg"]} kgCO2e

Carbon trade-off vs lowest-carbon option:
{result["carbon_delta_vs_lowest_kg"]} kgCO2e

Lowest-carbon option:
{result["lowest_carbon_option"]}

Grid stress avoided:
{result["grid_stress_avoided"]}

Human approval required:
{best["approval_required"]}

Current approval status:
{approval_status}

Recent MongoDB decision memory:
{recent_context}

Explain in no more than 300 words using exactly this structure:

1. Decision Summary:
Briefly state the selected region/time and why it was chosen.

2. Key Trade-off:
Explain the carbon, grid-stress, deadline, and latency trade-off.

3. Governance Decision:
Explain whether the schedule is auto-approved, pending, approved, or rejected.

4. Audit Note:
Write one concise audit-ready note.
"""
    return prompt


def generate_gemini_explanation(
    client,
    prompt: str,
) -> Dict[str, Any]:
    last_error = None

    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            return {
                "success": True,
                "model": model_name,
                "text": response.text,
                "error": None,
            }

        except APIError as api_error:
            last_error = api_error
            continue

        except Exception as general_error:
            last_error = general_error
            continue

    return {
        "success": False,
        "model": None,
        "text": None,
        "error": str(last_error),
    }


def build_fallback_explanation(workload, result, approval_status):
    best = result["best_option"]

    approval_text = (
        "requires human review"
        if best["approval_required"]
        else "is auto-approved under the current governance policy"
    )

    reason_codes = ", ".join(result.get("decision_reason_codes", []))

    return f"""
1. Decision Summary:
The scheduler selected {best["region"]} at {best["hour"]} for the workload '{workload["job"]}'. This option was selected using the deterministic carbon-grid-deadline scoring model.

2. Key Trade-off:
The selected schedule has carbon intensity of {best["carbon_intensity"]} gCO2/kWh and grid load of {best["grid_load"]}%. The selected emissions are {result["selected_emissions_kg"]} kgCO2e. The carbon trade-off versus the lowest-carbon option is {result["carbon_delta_vs_lowest_kg"]} kgCO2e.

3. Governance Decision:
This schedule {approval_text}. Approval status is currently: {approval_status}.

4. Audit Note:
Decision reason codes: {reason_codes}. This fallback explanation was generated locally because Gemini was unavailable.
"""

