import pandas as pd
import os
import json
from datetime import datetime
import streamlit as st

from dotenv import load_dotenv

from google import genai
from google.genai.errors import APIError

from data import workloads, schedule_options
from scheduler import recommend_schedule

from mongo_store import save_audit_log_to_mongodb, load_audit_logs_from_mongodb

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(page_title="GridCarbon Guardian", layout="wide")

st.title("GridCarbon Guardian")
st.subheader("Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads")

with st.sidebar:
    st.header("GridCarbon Guardian")
    st.markdown("""
    **Purpose:**  
    Schedule AI/data-centre workloads using carbon, grid-stress, deadline, and governance signals.

    **Core modes:**  
    - Flexible workload → auto-approved
    - Urgent workload → human-reviewed

    **Built with:**  
    - Python
    - Streamlit
    - Gemini API
    - Google Gen AI SDK
    - JSON audit logging
    """)

    st.divider()

    st.markdown("""
    **Demo flow:**
    1. Select a workload  
    2. Review schedule decision  
    3. Generate Gemini explanation  
    4. Approve/reject if required  
    5. Save/download audit log  
    """)

# Gemini setup
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please add GEMINI_API_KEY to your .env file.")
    st.stop()


@st.cache_resource
def get_genai_client(key: str):
    return genai.Client(api_key=key)


client = get_genai_client(api_key)

AUDIT_LOG_FILE = "audit_logs.json"


def save_audit_log(log_entry):
    existing_logs = []

    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as file:
                existing_logs = json.load(file)
        except json.JSONDecodeError:
            existing_logs = []

    existing_logs.append(log_entry)

    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(existing_logs, file, indent=2)




def load_audit_logs():
    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    try:
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []




# Intro
st.markdown("""
This prototype schedules flexible AI/data-centre workloads by balancing:

- carbon intensity
- grid-load stress
- workload deadline risk
- latency/cost proxy
- human approval requirement
""")


st.info(
    "Carbon-aware scheduling alone may choose the cleanest electricity window, "
    "but that window may still occur during severe grid stress. "
    "GridCarbon Guardian adds grid-load awareness, deadline protection, "
    "human approval, and audit logging so AI/data-centre workloads can be "
    "scheduled in a greener, safer, and more accountable way."
)



st.markdown("### Project Impact Snapshot")

impact_col1, impact_col2, impact_col3 = st.columns(3)

impact_col1.metric(
    "Decision mode",
    "Agent + Human",
    help="Low-risk schedules can be auto-approved; high-risk schedules require human review."
)

impact_col2.metric(
    "Governance layer",
    "Audit-ready",
    help="Every scheduling decision can be downloaded and saved into audit history."
)

impact_col3.metric(
    "Core innovation",
    "Carbon + Grid",
    help="The agent balances carbon intensity with grid stress and workload deadlines."
)



# Workload selector
selected_job = st.selectbox(
    "Select workload",
    [w["job"] for w in workloads]
)

workload = next(w for w in workloads if w["job"] == selected_job)

# Run scheduler
result = recommend_schedule(workload, schedule_options)
best = result["best_option"]

# Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Recommended region", best["region"])
col2.metric("Recommended time", best["hour"])
col3.metric("Grid load", f"{best['grid_load']}%")
col4.metric("Carbon intensity", f"{best['carbon_intensity']} gCO₂/kWh")

st.divider()

# Scheduling decision
st.subheader("Scheduling Decision")

st.write("**Selected workload:**", workload)
st.write("**Best schedule option:**", best)




st.write("**Selected schedule emissions:**", f"{result['selected_emissions_kg']} kgCO₂e")
st.write("**Lowest-carbon option emissions:**", f"{result['lowest_carbon_emissions_kg']} kgCO₂e")
st.write("**Carbon trade-off vs lowest-carbon option:**", f"{result['carbon_delta_vs_lowest_kg']} kgCO₂e")

if result["grid_stress_avoided"]:
    st.warning(
        f"Lowest-carbon option rejected: {result['lowest_carbon_option']['region']} "
        f"had {result['lowest_carbon_option']['grid_load']}% grid load. "
        "The agent selected a grid-safer option instead."
    )

st.write("**Human approval required:**", best["approval_required"])

if best["approval_required"]:
    if best["grid_load"] >= 85:
        st.warning(
            f"Human approval required: selected option has high grid load "
            f"({best['grid_load']}%). Operator must approve before execution."
        )
    elif best.get("deadline_violation", False):
        st.warning(
            "Human approval required: selected option may violate workload deadline."
        )
    else:
        st.warning("Human approval required before execution.")
else:
    st.success("Low-risk schedule. Auto-scheduling allowed.")

# Candidate options
st.subheader("All Candidate Schedule Options")

options_df = pd.DataFrame(result["all_options"])

display_columns = [
    "region",
    "hour",
    "hours_from_now",
    "finish_within_hours",
    "carbon_intensity",
    "grid_load",
    "deadline_violation",
    "score",
    "approval_required",
]

options_df = options_df[display_columns]

options_df = options_df.rename(columns={
    "region": "Region",
    "hour": "Start Time",
    "hours_from_now": "Starts In (h)",
    "finish_within_hours": "Finishes Within (h)",
    "carbon_intensity": "Carbon Intensity",
    "grid_load": "Grid Load (%)",
    "deadline_violation": "Deadline Violation",
    "score": "Risk Score",
    "approval_required": "Approval Required",
})

st.dataframe(options_df, use_container_width=True)


# Gemini explanation
st.subheader("Gemini Explanation")

if st.button("Generate Gemini Explanation"):
    prompt = f"""
You are GridCarbon Guardian, a standards-aware scheduling agent for AI/data-centre workloads.

Explain the following scheduling decision in clear, professional, audit-ready language.

Workload:
{workload}

Best selected option:
{best}

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

Explain in no more than 300 words using this structure:

1. Decision Summary:
Briefly state the selected region/time and why it was chosen.

2. Key Trade-off:
Explain the carbon, grid-stress, and deadline trade-off.

3. Governance Decision:
Explain whether the schedule is auto-approved or requires human approval.

4. Audit Note:
Write one concise audit-ready note.

"""

    with st.spinner("Generating Gemini explanation..."):
        
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ]

        response_text = None
        last_error = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                response_text = response.text
                st.caption(f"Generated using model: {model_name}")
                break

            except APIError as api_err:
                last_error = api_err
                continue

            except Exception as general_err:
                last_error = general_err
                continue

        if response_text:
            st.write(response_text)
        else:
            st.error(f"Gemini explanation could not be generated. Last error: {last_error}")
            st.info("The scheduler and audit log are still working. This is likely temporary model/API demand.")








# Human approval workflow
st.subheader("Human Approval")

if "approval_status" not in st.session_state:
    if best["approval_required"]:
        st.session_state.approval_status = "pending"
    else:
        st.session_state.approval_status = "auto-approved"

# Reset approval status when workload changes
if "last_workload" not in st.session_state:
    st.session_state.last_workload = workload["job"]

if st.session_state.last_workload != workload["job"]:
    st.session_state.last_workload = workload["job"]
    if best["approval_required"]:
        st.session_state.approval_status = "pending"
    else:
        st.session_state.approval_status = "auto-approved"

if best["approval_required"]:
    approval_col1, approval_col2, approval_col3 = st.columns(3)

    with approval_col1:
        if st.button("Approve Schedule"):
            st.session_state.approval_status = "approved"

    with approval_col2:
        if st.button("Reject Schedule"):
            st.session_state.approval_status = "rejected"

    with approval_col3:
        if st.button("Reset Approval"):
            st.session_state.approval_status = "pending"

    if st.session_state.approval_status == "approved":
        st.success("Schedule approved by human operator.")
    elif st.session_state.approval_status == "rejected":
        st.error("Schedule rejected by human operator.")
    else:
        st.warning("Approval status: pending human approval.")
else:
    st.success("Low-risk schedule auto-approved under governance policy.")
    st.session_state.approval_status = "auto-approved"


# Audit log
st.subheader("Audit Log Preview")


if "decision_id" not in st.session_state:
    st.session_state.decision_id = f"GCG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

if "last_decision_workload" not in st.session_state:
    st.session_state.last_decision_workload = workload["job"]

if st.session_state.last_decision_workload != workload["job"]:
    st.session_state.last_decision_workload = workload["job"]
    st.session_state.decision_id = f"GCG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

decision_id = st.session_state.decision_id




audit_log = {
    "decision_id": decision_id,
    "decision_timestamp": datetime.now().isoformat(),
    "workload": workload["job"],
    "selected_region": best["region"],
    "selected_time": best["hour"],
    "carbon_intensity": best["carbon_intensity"],
    "grid_load": best["grid_load"],
    "score": best["score"],
    "approval_required": best["approval_required"],
    "approval_status": st.session_state.approval_status,
    "selected_emissions_kg": result["selected_emissions_kg"],
    "lowest_carbon_emissions_kg": result["lowest_carbon_emissions_kg"],
    "carbon_delta_vs_lowest_kg": result["carbon_delta_vs_lowest_kg"],
    "lowest_carbon_region": result["lowest_carbon_option"]["region"],
    "lowest_carbon_grid_load": result["lowest_carbon_option"]["grid_load"],
    "grid_stress_avoided": result["grid_stress_avoided"],

}



st.json(audit_log)

audit_log_json = json.dumps(audit_log, indent=2)

st.download_button(
    label="Download Audit Log",
    data=audit_log_json,
    file_name=f"{audit_log['decision_id']}_audit_log.json",
    mime="application/json",
)

save_col1, save_col2 = st.columns(2)

with save_col1:
    if st.button("Save Audit Log to MongoDB"):
        saved = save_audit_log_to_mongodb(audit_log)
        if saved:
            st.success("Audit log saved to MongoDB decision memory.")
        else:
            st.error("MongoDB save failed. Check MONGODB_URI in .env.")

with save_col2:
    if st.button("Save Audit Log to Local File"):
        save_audit_log(audit_log)
        st.success(f"Audit log saved to {AUDIT_LOG_FILE}")




st.subheader("MongoDB Decision Memory")

mongodb_logs = load_audit_logs_from_mongodb()

if mongodb_logs:
    st.caption("Retrieved from MongoDB audit_logs collection.")
    st.dataframe(mongodb_logs, use_container_width=True)
else:
    st.info("No MongoDB audit records found yet. Save a decision to MongoDB to create decision memory.")

with st.expander("Local fallback audit history"):
    saved_logs = load_audit_logs()

    if saved_logs:
        st.dataframe(saved_logs, use_container_width=True)
    else:
        st.info("No local audit logs found.")


