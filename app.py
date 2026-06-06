from audit import build_audit_log
import plotly.graph_objects as go
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




st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background-color: #050807;
        color: #D8FFE3;
        font-family: "DM Sans", sans-serif;
    }

    /* Main container */

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Headings */
    h1, h2, h3 {
        color: #7CFF9B !important;
        letter-spacing: 0.02em;
    }

    /* Normal text */
    p, li, div {
        color: #D8FFE3;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #08110D;
        border-right: 1px solid #1F3D2B;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #7CFF9B !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #0B1510;
        border: 1px solid #1F3D2B;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 0 1px rgba(124, 255, 155, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #9AE6B4 !important;
        font-family: "Space Mono", monospace;
        font-size: 0.85rem;
    }

    div[data-testid="stMetricValue"] {
        color: #7CFF9B !important;
        font-family: "Space Mono", monospace;
    }

    /* Info / warning / success boxes */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        font-family: "DM Sans", sans-serif;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1F3D2B;
        border-radius: 10px;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background-color: #0E1A13;
        color: #7CFF9B;
        border: 1px solid #7CFF9B;
        border-radius: 8px;
        font-family: "Space Mono", monospace;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #14351F;
        color: #B6FFC7;
        border-color: #B6FFC7;
    }

    /* Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #0B1510;
        border-color: #1F3D2B;
        color: #D8FFE3;
    }

    /* JSON/code blocks */
    pre, code {
        background-color: #07100B !important;
        color: #9CFFB8 !important;
        font-family: "Space Mono", monospace !important;
    }

    /* Horizontal divider */
    hr {
        border-color: #1F3D2B;
    }

    /* Caption */
    .stCaption, caption {
        color: #9AE6B4 !important;
    }

    /* Top status bar */
    .top-status-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 12px 16px;
        margin-bottom: 18px;
        background-color: #07100B;
        border: 1px solid #1F3D2B;
        border-radius: 12px;
        font-family: "Space Mono", monospace;
    }

    .brand-block {
        display: flex;
        align-items: center;
        gap: 10px;
        white-space: nowrap;
    }

    .brand-title {
        color: #7CFF9B;
        font-weight: 700;
        letter-spacing: 0.08em;
        font-size: 0.9rem;
    }

    .live-dot {
        width: 10px;
        height: 10px;
        background-color: #7CFF9B;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #7CFF9B;
        animation: pulse 1.4s infinite;
    }

    @keyframes pulse {
        0% { opacity: 0.35; transform: scale(0.85); }
        50% { opacity: 1; transform: scale(1.15); }
        100% { opacity: 0.35; transform: scale(0.85); }
    }

    .nav-tabs {
        display: flex;
        gap: 14px;
        color: #9AE6B4;
        font-size: 0.75rem;
    }

    .nav-tabs span {
        border-bottom: 1px solid transparent;
    }

    .nav-tabs span:first-child {
        color: #7CFF9B;
        border-bottom: 1px solid #7CFF9B;
    }

    .status-pills {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .status-pill {
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 0.68rem;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }

    .status-green {
        color: #7CFF9B;
        border: 1px solid #7CFF9B;
        background-color: rgba(124, 255, 155, 0.08);
    }

    .status-amber {
        color: #FFD166;
        border: 1px solid #FFD166;
        background-color: rgba(255, 209, 102, 0.08);
    }

    /* Selectbox dropdown menu */
    div[data-baseweb="popover"] {
        background-color: #0B1510 !important;
    }

    ul[role="listbox"] {
        background-color: #0B1510 !important;
        border: 1px solid #1F3D2B !important;
    }

    li[role="option"] {
        background-color: #0B1510 !important;
        color: #D8FFE3 !important;
        font-family: "Space Mono", monospace !important;
    }

    li[role="option"]:hover {
        background-color: #14351F !important;
        color: #7CFF9B !important;
    }

    div[data-baseweb="select"] span {
        color: #D8FFE3 !important;
    }

        
    /* Hide Streamlit default header / toolbar white band */
    header[data-testid="stHeader"] {
        background-color: #050807 !important;
        height: 0rem !important;
    }

    div[data-testid="stToolbar"] {
        display: none !important;
    }

    div[data-testid="stDecoration"] {
        display: none !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    
    .hero-title {
        margin-top: 24px;
        margin-bottom: 8px;
        font-size: 3.2rem;
        line-height: 1.05;
        font-weight: 800;
        color: #7CFF9B;
        letter-spacing: 0.03em;
    }

    .hero-subtitle {
        margin-bottom: 28px;
        font-size: 1.65rem;
        line-height: 1.25;
        font-weight: 700;
        color: #7CFF9B;
        max-width: 1050px;
    }

    
    </style>
    """,
    unsafe_allow_html=True,
)



st.markdown(
    """
    <div class="hero-title">GridCarbon Guardian</div>
    <div class="hero-subtitle">
        Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("GridCarbon Guardian")

    st.markdown("### Purpose")
    st.write(
        "Schedule AI/data-centre workloads using carbon, grid-stress, "
        "deadline, and governance signals."
    )

    st.markdown("### Core modes")
    st.markdown("- Flexible workload → auto-approved")
    st.markdown("- Urgent workload → human-reviewed")

    st.markdown("### Built with")
    st.markdown("- Python")
    st.markdown("- Streamlit")
    st.markdown("- Gemini API")
    st.markdown("- Google Gen AI SDK")
    st.markdown("- MongoDB Atlas")
    st.markdown("- PyMongo")
    st.markdown("- JSON fallback audit logging")

    st.divider()

    st.markdown("### Demo flow")
    st.markdown("1. Select a workload")
    st.markdown("2. Review schedule decision")
    st.markdown("3. Generate Gemini explanation")
    st.markdown("4. Approve/reject if required")
    st.markdown("5. Save/download audit log")
                                





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




def build_score_breakdown(best, workload):
    carbon_component = 0.40 * (best["carbon_intensity"] / 600)
    grid_component = 0.30 * (best["grid_load"] / 100)

    if best.get("deadline_violation", False):
        deadline_component = 0.20
    elif workload["delay_tolerant"]:
        deadline_component = 0.04
    else:
        deadline_component = 0.12

    latency_component = 0.10 * (best["latency_score"] / 100)

    return {
        "Carbon": round(carbon_component, 3),
        "Grid": round(grid_component, 3),
        "Deadline": round(deadline_component, 3),
        "Latency": round(latency_component, 3),
    }






# Intro
st.markdown("""
This prototype schedules flexible AI/data-centre workloads by balancing:

- carbon intensity
- grid-load stress
- workload deadline risk
- latency/cost proxy
- human approval requirement
""")




# Workload selector
selected_job = st.selectbox(
    "Select workload",
    [w["job"] for w in workloads]
)

workload = next(w for w in workloads if w["job"] == selected_job)

# Run scheduler
result = recommend_schedule(workload, schedule_options)
best = result["best_option"]



mongodb_connected = bool(os.getenv("MONGODB_URI"))

mongodb_status = "MONGODB MEMORY: CONNECTED" if mongodb_connected else "MONGODB MEMORY: OFFLINE"
mongodb_status_class = "status-green" if mongodb_connected else "status-amber"


# Top status bar
current_grid_load = best["grid_load"] if "best" in locals() else 0

if current_grid_load >= 85:
    grid_status = "HIGH GRID STRESS"
    grid_status_class = "status-amber"
elif current_grid_load >= 70:
    grid_status = "MODERATE GRID STRESS"
    grid_status_class = "status-amber"
else:
    grid_status = "GRID NORMAL"
    grid_status_class = "status-green"

decision_mode = "HUMAN REVIEW" if best["approval_required"] else "AUTO-GOVERNED"



st.markdown(
    f"""
    <div class="top-status-bar">
        <div class="brand-block">
            <span class="live-dot"></span>
            <span class="brand-title">GRIDCARBON GUARDIAN</span>
        </div>
        <div class="nav-tabs">
            <span>DASHBOARD</span>
            <span>WORKLOADS</span>
            <span>AUDIT LOG</span>
            <span>POLICY</span>
        </div>
        <div class="status-pills">
            <span class="status-pill {grid_status_class}">{grid_status}: {current_grid_load}%</span>
            <span class="status-pill {mongodb_status_class}">{mongodb_status}</span>
            <span class="status-pill status-amber">{decision_mode}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


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

# Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Recommended region", best["region"])
col2.metric("Recommended time", best["hour"])
col3.metric("Grid load", f"{best['grid_load']}%")
col4.metric("Carbon intensity", f"{best['carbon_intensity']} gCO₂/kWh")

st.markdown("### Risk Score Breakdown")

score_breakdown = build_score_breakdown(best, workload)

fig = go.Figure(
    data=[
        go.Bar(
            x=list(score_breakdown.keys()),
            y=list(score_breakdown.values()),
            text=list(score_breakdown.values()),
            textposition="auto",
        )
    ]
)

fig.update_layout(
    paper_bgcolor="#050807",
    plot_bgcolor="#050807",
    font=dict(color="#D8FFE3", family="Space Mono"),
    height=320,
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis=dict(
        title="Weighted contribution",
        gridcolor="#1F3D2B",
        zerolinecolor="#1F3D2B",
    ),
    xaxis=dict(
        gridcolor="#1F3D2B",
    ),
)

fig.update_traces(
    marker_line_color="#7CFF9B",
    marker_line_width=1.5,
)

st.plotly_chart(fig, use_container_width=True)

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

Score breakdown:
{best["score_breakdown"]}

Decision reason codes:
{result["decision_reason_codes"]}

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

audit_log = build_audit_log(
    decision_id=decision_id,
    workload=workload,
    result=result,
    approval_status=st.session_state.approval_status,
)

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
