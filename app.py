from historical_validation import (
    load_historical_validation_sample,
    summarize_validation,
)
from textwrap import dedent
from audit import build_audit_log
import plotly.graph_objects as go
import pandas as pd
import os
import json
from datetime import datetime
import streamlit as st

from dotenv import load_dotenv


from gemini_service import (
    get_genai_client,
    build_explanation_prompt,
    generate_gemini_explanation,
    build_fallback_explanation,
)



from data_sources import get_workloads, get_schedule_options, get_data_source_label

from scheduler import recommend_schedule

from mongo_store import (
    save_audit_log_to_mongodb,
    load_audit_logs_from_mongodb,
    load_recent_decisions_by_workload,
    test_mongodb_connection,
)


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

    /* Simple expander styling */
    div[data-testid="stExpander"] {
        background-color: #07100B !important;
        border: 1px solid #1F3D2B !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        margin: 12px 0 18px 0 !important;
    }

    div[data-testid="stExpander"] summary {
        background-color: #07100B !important;
        color: #7CFF9B !important;
        font-family: "Space Mono", monospace !important;
        font-size: 12px !important;
        letter-spacing: 0.03em !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid #1F3D2B !important;
    }

    div[data-testid="stExpanderDetails"] {
        background-color: #07100B !important;
        color: #D8FFE3 !important;
        padding: 12px 14px !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #07100B;
        border-bottom: 1px solid #1F3D2B;
        border-radius: 10px 10px 0 0;
        padding: 4px 8px 0;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #9AE6B4;
        font-family: "Space Mono", monospace;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.04em;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0B1510 !important;
        color: #7CFF9B !important;
        border-top: 2px solid #7CFF9B !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background-color: #050807;
        padding: 20px 0 0;
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


@st.cache_resource
def get_cached_genai_client(key: str):
    return get_genai_client(key)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    client = None
    st.warning("Gemini API key not configured. Running deterministic fallback demo mode.")
else:
    client = get_cached_genai_client(api_key)


AUDIT_LOG_FILE = "audit_logs.json"

USE_LIVE_DATA = False

workloads = get_workloads()
schedule_options = get_schedule_options(use_live_data=USE_LIVE_DATA)
data_source_label = get_data_source_label(use_live_data=USE_LIVE_DATA)



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



def render_html(markup: str):
    st.html(dedent(markup).strip())


def metric_card(label, value, helper_text=None):
    helper_html = ""
    if helper_text:
        helper_html = f"""
        <div style="color:#6FAF84;font-size:10px;margin-top:6px;line-height:1.3;">
            {helper_text}
        </div>
        """

    return f"""
    <div style="
        background:#0B1510;
        border:1px solid #1F3D2B;
        border-radius:10px;
        padding:14px 16px;
        min-height:82px;
        font-family:Space Mono,monospace;
        overflow:visible;
        white-space:normal;
    ">
        <div style="
            color:#9AE6B4;
            font-size:11px;
            letter-spacing:0.08em;
            text-transform:uppercase;
            margin-bottom:8px;
        ">
            {label}
        </div>
        <div style="
            color:#7CFF9B;
            font-size:18px;
            font-weight:700;
            line-height:1.25;
            white-space:normal;
            overflow-wrap:anywhere;
        ">
            {value}
        </div>
        {helper_html}
    </div>
    """



def summary_card(title, items):
    rows = ""
    for label, value in items.items():
        rows += f"""
        <div style="display:flex;justify-content:space-between;gap:16px;
        border-bottom:1px solid rgba(31,61,43,0.55);padding:7px 0;">
            <span style="color:#9AE6B4;font-size:11px;">{label}</span>
            <span style="color:#D8FFE3;font-size:12px;text-align:right;">{value}</span>
        </div>
        """

    return f"""
    <div style="
        background:#0B1510;
        border:1px solid #1F3D2B;
        border-radius:10px;
        padding:14px 16px;
        margin:10px 0 12px 0;
        font-family:Space Mono,monospace;
    ">
        <div style="
            color:#7CFF9B;
            font-size:12px;
            letter-spacing:0.08em;
            text-transform:uppercase;
            margin-bottom:10px;
        ">
            {title}
        </div>
        {rows}
    </div>
    """


# UI HELPER: compact status pill
def status_pill(label, value, color="#7CFF9B"):
    return (
        f'<span style="display:inline-block;border:1px solid {color};'
        f'color:{color};background:rgba(124,255,155,0.06);'
        f'border-radius:999px;padding:4px 8px;margin:3px 4px 3px 0;'
        f'font-family:Space Mono,monospace;font-size:10px;'
        f'letter-spacing:0.04em;">{label}: {value}</span>'
    )


# UI HELPER: reason-code pill colors
def reason_code_pill(code):
    if code in [
        "DEADLINE_FEASIBLE",
        "AUTO_APPROVED_LOW_RISK",
        "LOWEST_CARBON_REJECTED_GRID_STRESS",
    ]:
        color = "#4ade80"
    elif code in [
        "MODERATE_OR_HIGH_GRID_LOAD",
        "FLEXIBLE_WORKLOAD_SHIFTED_AWAY_FROM_GRID_STRESS",
    ]:
        color = "#FFD166"
    elif code in [
        "HIGH_GRID_STRESS",
        "HUMAN_APPROVAL_REQUIRED",
        "DEADLINE_VIOLATION",
    ]:
        color = "#ef4444"
    else:
        color = "#9AE6B4"

    return (
        f'<span style="display:inline-block;border:1px solid {color};'
        f'color:{color};background:rgba(255,255,255,0.03);'
        f'border-radius:999px;padding:4px 8px;margin:3px 4px 3px 0;'
        f'font-family:Space Mono,monospace;font-size:10px;">'
        f'{code}</span>'
    )



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




def alert_card(title, message, tone="green"):
    colors = {
        "green": ("#4ade80", "#07140C"),
        "amber": ("#FFD166", "#171204"),
        "red": ("#ef4444", "#1a0a0a"),
    }

    color, bg = colors.get(tone, colors["green"])

    return f"""
    <div style="
        border-left:3px solid {color};
        background:{bg};
        padding:14px 18px;
        border-radius:0 8px 8px 0;
        font-family:Space Mono,monospace;
        margin:10px 0 14px 0;
    ">
        <div style="
            color:{color};
            font-size:12px;
            letter-spacing:0.08em;
            text-transform:uppercase;
            margin-bottom:6px;
        ">
            {title}
        </div>
        <div style="
            color:#D8FFE3;
            font-size:12px;
            line-height:1.5;
        ">
            {message}
        </div>
    </div>
    """

def build_carbon_liability_record(decision_id, workload, result, approval_status, audit_log):
    best = result["best_option"]

    return {
        "liability_record_id": f"CCLR-{decision_id}",
        "decision_id": decision_id,
        "record_type": "compute_carbon_liability_record",

        "workload": {
            "workload_id": decision_id,
            "workload_name": workload["job"],
            "duration_hours": workload["duration_hours"],
            "deadline_hours": workload["deadline_hours"],
            "delay_tolerant": workload["delay_tolerant"],
            "energy_kwh": workload["energy_kwh"],
        },

        "selected_schedule": {
            "region": best["region"],
            "time_window": best["hour"],
            "hours_from_now": best["hours_from_now"],
            "finish_within_hours": best["finish_within_hours"],
        },

        "carbon_accounting": {
            "carbon_intensity_gco2_per_kwh": best["carbon_intensity"],
            "gross_compute_carbon_liability_kgco2e": result["selected_emissions_kg"],
            "lowest_carbon_option_emissions_kgco2e": result["lowest_carbon_emissions_kg"],
            "carbon_tradeoff_vs_lowest_kgco2e": result["carbon_delta_vs_lowest_kg"],
            "calculation_method": "energy_kwh * carbon_intensity_gco2_per_kwh / 1000",
            "methodology": "MVP workload-level operational emissions estimate",
        },

        "grid_governance": {
            "grid_load_percent": best["grid_load"],
            "lowest_carbon_grid_load_percent": result["lowest_carbon_option"]["grid_load"],
            "grid_stress_avoided": result["grid_stress_avoided"],
            "approval_required": best["approval_required"],
            "approval_status": approval_status,
            "decision_reason_codes": result.get("decision_reason_codes", []),
        },

        "assurance": {
            "assurance_status": "self-declared_future-auditable",
            "verification_status": "not_third_party_verified",
            "evidence_reference": decision_id,
            "data_source": result["data_source"],
            "scheduler_version": audit_log["scheduler_version"],
        },

        "timestamps": {
            "created_at": audit_log["decision_timestamp"],
        },
    }

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ Mission",
    "📊 Analysis",
    "🧠 Gemini",
    "🔐 Governance",
    "📋 Ledger"
])





with tab1:
    st.markdown(
        """
        <div class="hero-title">GridCarbon Guardian</div>
        <div class="hero-subtitle">
            Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    result["data_source"] = data_source_label
    best = result["best_option"]

    mongodb_connected = test_mongodb_connection()

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

    if "decision_id" not in st.session_state:
        st.session_state.decision_id = f"GCG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    if "last_decision_workload" not in st.session_state:
        st.session_state.last_decision_workload = workload["job"]

    if st.session_state.last_decision_workload != workload["job"]:
        st.session_state.last_decision_workload = workload["job"]
        st.session_state.decision_id = f"GCG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    decision_id = st.session_state.decision_id

    st.caption(f"Data source mode: {data_source_label}")

    # HEALTH STRIP
    gemini_health = "READY/FALLBACK"
    mongo_health = "CONNECTED" if mongodb_connected else "OFFLINE"
    scheduler_health = "OK"
    cloud_health = "CLOUD RUN" if os.getenv("K_SERVICE") else "LOCAL / HOSTED DEMO"
    data_health = data_source_label

    render_html(f"""
    <div style="background:#07100B;border:1px solid #1F3D2B;border-radius:10px;
    padding:10px 14px;margin:8px 0 18px 0;font-family:Space Mono,monospace;">
        {status_pill("SCHEDULER", scheduler_health, "#4ade80")}
        {status_pill("GEMINI", gemini_health, "#FFD166")}
        {status_pill("MONGODB", mongo_health, "#4ade80" if mongodb_connected else "#FFD166")}
        {status_pill("DATA", data_health, "#9AE6B4")}
        {status_pill("RUNTIME", cloud_health, "#4ade80")}
    </div>
    """)

    render_html(alert_card(
        "How GridCarbon Guardian works",
        "Carbon-aware scheduling alone may choose the cleanest electricity window, "
        "but that window may still occur during severe grid stress. "
        "GridCarbon Guardian adds grid-load awareness, deadline protection, "
        "human approval, and audit logging so AI/data-centre workloads can be "
        "scheduled in a greener, safer, and more accountable way.",
        "green",
    ))

    st.markdown("### Project Impact Snapshot")

    impact_col1, impact_col2, impact_col3 = st.columns(3)

    with impact_col1:
        render_html(metric_card(
            "Decision mode",
            "Agent + Human",
            "Auto-approval for low-risk jobs; review for high-risk jobs."
        ))

    with impact_col2:
        render_html(metric_card(
            "Governance layer",
            "Audit-ready",
            "Every decision can be exported and stored."
        ))

    with impact_col3:
        render_html(metric_card(
            "Core innovation",
            "Carbon + Grid",
            "Balances emissions, grid stress, and deadlines."
        ))

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_html(metric_card("Recommended region", best["region"]))

    with col2:
        render_html(metric_card("Recommended time", best["hour"]))

    with col3:
        grid_note = "High stress" if best["grid_load"] >= 85 else "Grid-safe"
        render_html(metric_card("Grid load", f"{best['grid_load']}%", grid_note))

    with col4:
        render_html(metric_card("Carbon intensity", f"{best['carbon_intensity']} gCO₂/kWh"))

    render_html("""
    <div style="margin:24px 0 8px;padding:14px 18px;background:#07100B;
    border:1px solid #1F3D2B;border-radius:10px;font-family:Space Mono,monospace;
    font-size:11px;color:#9AE6B4;letter-spacing:0.06em;text-align:center;">
    → OPEN THE 📊 ANALYSIS TAB TO SEE THE FULL DECISION
    </div>""")


with tab2:
    # PROOF OF DECISION PANEL
    approval_status_preview = (
        "HUMAN REVIEW REQUIRED"
        if best["approval_required"]
        else "AUTO-APPROVED"
    )

    approval_color = "#FFD166" if best["approval_required"] else "#4ade80"

    reason_pills = "".join(
        reason_code_pill(code)
        for code in result.get("decision_reason_codes", [])
    )

    render_html(f"""
    <div style="background:#0B1510;border:1px solid #1F3D2B;border-radius:12px;
    padding:16px 18px;margin:18px 0 20px 0;font-family:Space Mono,monospace;">

        <div style="color:#9AE6B4;font-size:11px;letter-spacing:0.12em;
        text-transform:uppercase;margin-bottom:14px;">
            PROOF OF DECISION
        </div>

        <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
        gap:12px;margin-bottom:14px;">

            <div>
                <div style="color:#9AE6B4;font-size:10px;">SELECTED REGION</div>
                <div style="color:#D8FFE3;font-size:14px;">{best["region"]}</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">SELECTED TIME</div>
                <div style="color:#D8FFE3;font-size:14px;">{best["hour"]}</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">GRID LOAD</div>
                <div style="color:#D8FFE3;font-size:14px;">{best["grid_load"]}%</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">CARBON INTENSITY</div>
                <div style="color:#D8FFE3;font-size:14px;">{best["carbon_intensity"]} gCO₂/kWh</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">RISK SCORE</div>
                <div style="color:#D8FFE3;font-size:14px;">{best["score"]}</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">APPROVAL MODE</div>
                <div style="color:{approval_color};font-size:14px;">{approval_status_preview}</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">DATA SOURCE</div>
                <div style="color:#D8FFE3;font-size:14px;">{data_source_label}</div>
            </div>

            <div>
                <div style="color:#9AE6B4;font-size:10px;">GRID STRESS AVOIDED</div>
                <div style="color:#D8FFE3;font-size:14px;">{result["grid_stress_avoided"]}</div>
            </div>
        </div>

        <div style="color:#9AE6B4;font-size:10px;margin-bottom:6px;">
            REASON CODES
        </div>

        <div>{reason_pills}</div>
    </div>
    """)





    st.markdown("### Risk Score Breakdown")

    score_breakdown = {
        "Carbon": best["score_breakdown"]["carbon_component"],
        "Grid": best["score_breakdown"]["grid_component"],
        "Deadline": best["score_breakdown"]["deadline_component"],
        "Latency": best["score_breakdown"]["latency_component"],
    }


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



    bar_colors = [
        "#4ade80",  # Carbon
        "#ef4444" if score_breakdown["Grid"] > 0.25 else "#FFD166",  # Grid
        "#FFD166",  # Deadline
        "#4ade80",  # Latency
    ]

    fig.update_traces(
        marker_color=bar_colors,
        marker_line_color=bar_colors,
        marker_line_width=1.5,
        textfont=dict(color="#D8FFE3"),
    )



    st.plotly_chart(fig, use_container_width=True)

    st.divider()


    # HISTORICAL UI FIX 1 — Historical Validation Snapshot
    historical_df = load_historical_validation_sample()
    historical_summary = summarize_validation(historical_df)

    carbon_only_hour = historical_summary["carbon_only_hour"]
    guardian_hour = historical_summary["guardian_hour"]

    st.markdown("### Historical Validation Snapshot")

    render_html(f"""
    <div style="
        margin-top:8px;
        margin-bottom:14px;
        font-family:Space Mono,monospace;
    ">
        <div style="
            color:#9AE6B4;
            font-size:11px;
            letter-spacing:0.12em;
            text-transform:uppercase;
            margin-bottom:6px;
        ">
            Why carbon-only scheduling can still overload the grid
        </div>
        <div style="
            color:#D8FFE3;
            font-size:12px;
            line-height:1.5;
            max-width:980px;
        ">
            Demo validation sample based on historical-style carbon/load patterns.
            The live scheduler remains deterministic for reliability.
        </div>
    </div>
    """)

    render_html(f"""
    <div style="
        background:#0B1510;
        border:1px solid #1F3D2B;
        border-radius:12px;
        padding:18px 20px;
        margin:16px 0 22px 0;
        font-family:Space Mono,monospace;
    ">
        <div style="
            color:#9AE6B4;
            font-size:11px;
            letter-spacing:0.12em;
            text-transform:uppercase;
            margin-bottom:14px;
        ">
            Real-World Logic Check
        </div>

        <div style="
            display:grid;
            grid-template-columns:1fr 1fr;
            gap:18px;
            margin-bottom:16px;
        ">
            <div style="
                border:1px solid #FFD166;
                border-left:4px solid #ef4444;
                border-radius:10px;
                padding:14px 16px;
                background:#171204;
            ">
                <div style="
                    color:#FFD166;
                    font-size:11px;
                    letter-spacing:0.08em;
                    text-transform:uppercase;
                    margin-bottom:10px;
                ">
                    Carbon-only scheduler
                </div>
                <div style="color:#D8FFE3;font-size:13px;line-height:1.7;">
                    <span style="color:#9AE6B4;">Selected window:</span>
                    <span style="color:#FFD166;"> {historical_summary["carbon_only_hour"]}</span><br>
                    <span style="color:#9AE6B4;">Carbon intensity:</span>
                    {historical_summary["carbon_only_carbon"]} gCO₂/kWh<br>
                    <span style="color:#9AE6B4;">Grid load:</span>
                    <span style="color:#ef4444;"> {historical_summary["carbon_only_grid"]}%</span><br>
                    <span style="color:#9AE6B4;">Status:</span>
                    <span style="color:#FFD166;"> Clean but grid-stressed</span>
                </div>
            </div>

            <div style="
                border:1px solid #4ade80;
                border-left:4px solid #4ade80;
                border-radius:10px;
                padding:14px 16px;
                background:#07140C;
            ">
                <div style="
                    color:#4ade80;
                    font-size:11px;
                    letter-spacing:0.08em;
                    text-transform:uppercase;
                    margin-bottom:10px;
                ">
                    GridCarbon Guardian
                </div>
                <div style="color:#D8FFE3;font-size:13px;line-height:1.7;">
                    <span style="color:#9AE6B4;">Selected window:</span>
                    <span style="color:#4ade80;"> {historical_summary["guardian_hour"]}</span><br>
                    <span style="color:#9AE6B4;">Carbon intensity:</span>
                    {historical_summary["guardian_carbon"]} gCO₂/kWh<br>
                    <span style="color:#9AE6B4;">Grid load:</span>
                    <span style="color:#4ade80;"> {historical_summary["guardian_grid"]}%</span><br>
                    <span style="color:#9AE6B4;">Status:</span>
                    <span style="color:#4ade80;"> Safer grid window</span>
                </div>
            </div>
        </div>

        <div style="
            display:grid;
            grid-template-columns:repeat(3,1fr);
            gap:12px;
            margin-top:12px;
        ">
            <div style="
                border:1px solid #4ade80;
                border-radius:8px;
                padding:10px 12px;
                background:#07140C;
            ">
                <div style="color:#9AE6B4;font-size:10px;text-transform:uppercase;">
                    Grid-load reduction
                </div>
                <div style="color:#4ade80;font-size:16px;font-weight:700;margin-top:4px;">
                    {historical_summary["grid_load_reduction"]} percentage points
                </div>
            </div>

            <div style="
                border:1px solid #FFD166;
                border-radius:8px;
                padding:10px 12px;
                background:#171204;
            ">
                <div style="color:#9AE6B4;font-size:10px;text-transform:uppercase;">
                    Carbon trade-off
                </div>
                <div style="color:#FFD166;font-size:16px;font-weight:700;margin-top:4px;">
                    +{historical_summary["carbon_tradeoff"]} gCO₂/kWh
                </div>
            </div>

            <div style="
                border:1px solid #1F3D2B;
                border-radius:8px;
                padding:10px 12px;
                background:#07100B;
            ">
                <div style="color:#9AE6B4;font-size:10px;text-transform:uppercase;">
                    Decision
                </div>
                <div style="color:#7CFF9B;font-size:16px;font-weight:700;margin-top:4px;">
                    Grid-safe deferral preferred
                </div>
            </div>
        </div>
    </div>
    """)

    # HISTORICAL UI FIX 2 — Improved historical validation chart
    validation_fig = go.Figure()

    historical_bar_colors = []
    historical_marker_colors = []

    for _, row in historical_df.iterrows():
        hour = row["hour"]

        if hour == carbon_only_hour:
            historical_bar_colors.append("#FFD166")
            historical_marker_colors.append("#ef4444")
        elif hour == guardian_hour:
            historical_bar_colors.append("#4ade80")
            historical_marker_colors.append("#4ade80")
        else:
            historical_bar_colors.append("#2f9f5f")
            historical_marker_colors.append("#FFD166")

    validation_fig.add_trace(
        go.Bar(
            x=historical_df["hour"],
            y=historical_df["carbon_intensity"],
            name="Carbon intensity",
            marker_color=historical_bar_colors,
            marker_line_color=historical_bar_colors,
            marker_line_width=1.2,
            text=historical_df["carbon_intensity"],
            textposition="outside",
            textfont=dict(color="#D8FFE3", family="Space Mono", size=10),
        )
    )

    validation_fig.add_trace(
        go.Scatter(
            x=historical_df["hour"],
            y=historical_df["grid_load"],
            name="Grid load",
            mode="lines+markers+text",
            line=dict(color="#FFD166", width=3),
            marker=dict(
                size=10,
                color=historical_marker_colors,
                line=dict(color="#050807", width=1),
            ),
            text=[f"{value}%" for value in historical_df["grid_load"]],
            textposition="top center",
            textfont=dict(color="#FFD166", family="Space Mono", size=10),
            yaxis="y2",
        )
    )

    validation_fig.add_annotation(
        x=carbon_only_hour,
        y=historical_summary["carbon_only_carbon"],
        text="Carbon-only picks lowest carbon<br>but grid load is 94%",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#ef4444",
        ax=-70,
        ay=-55,
        font=dict(color="#FFD166", family="Space Mono", size=10),
        bgcolor="#171204",
        bordercolor="#FFD166",
        borderwidth=1,
    )

    validation_fig.add_annotation(
        x=guardian_hour,
        y=historical_summary["guardian_carbon"],
        text="GridCarbon picks<br>safer grid window",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#4ade80",
        ax=55,
        ay=-55,
        font=dict(color="#4ade80", family="Space Mono", size=10),
        bgcolor="#07140C",
        bordercolor="#4ade80",
        borderwidth=1,
    )

    validation_fig.update_layout(
        paper_bgcolor="#050807",
        plot_bgcolor="#050807",
        font=dict(color="#D8FFE3", family="Space Mono"),
        height=400,
        margin=dict(l=30, r=40, t=65, b=40),

        xaxis=dict(
            title=dict(
                text="Historical-style time window",
                font=dict(color="#A7B3AA", family="Space Mono", size=11),
            ),
            gridcolor="#1F3D2B",
            tickfont=dict(color="#A7B3AA", family="Space Mono", size=10),
        ),

        yaxis=dict(
            title=dict(
                text="Carbon intensity (gCO₂/kWh)",
                font=dict(color="#A7B3AA", family="Space Mono", size=11),
            ),
            gridcolor="#1F3D2B",
            zerolinecolor="#1F3D2B",
            tickfont=dict(color="#A7B3AA", family="Space Mono", size=10),
        ),

        yaxis2=dict(
            title=dict(
                text="Grid load (%)",
                font=dict(color="#A7B3AA", family="Space Mono", size=11),
            ),
            overlaying="y",
            side="right",
            range=[0, 105],
            gridcolor="#1F3D2B",
            tickfont=dict(color="#A7B3AA", family="Space Mono", size=10),
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="right",
            x=1,
            bgcolor="rgba(5,8,7,0)",
            font=dict(color="#D8FFE3", family="Space Mono", size=10),
        ),
    )



    st.plotly_chart(validation_fig, use_container_width=True)

    # HISTORICAL UI FIX 3 — Interpretation note
    render_html(f"""
    <div style="
        background:#07100B;
        border-left:3px solid #FFD166;
        border-radius:0 8px 8px 0;
        padding:14px 18px;
        margin:12px 0 24px 0;
        font-family:Space Mono,monospace;
    ">
        <div style="
            color:#FFD166;
            font-size:11px;
            letter-spacing:0.1em;
            text-transform:uppercase;
            margin-bottom:6px;
        ">
            Interpretation
        </div>
        <div style="
            color:#D8FFE3;
            font-size:12px;
            line-height:1.6;
        ">
            This validation snapshot supports the logic that carbon-aware scheduling alone is incomplete.
            The lowest-carbon window can coincide with high grid stress. GridCarbon Guardian accepts
            a controlled carbon trade-off to avoid pushing critical workloads into a
            <span style="color:#ef4444;">94% grid-load window</span>.
        </div>
    </div>
    """)




    # Scheduling decision
    st.subheader("Scheduling Decision")



    render_html(summary_card(
        "Selected Workload",
        {
            "Job": workload["job"],
            "Duration": f'{workload["duration_hours"]} hours',
            "Deadline": f'{workload["deadline_hours"]} hours',
            "Delay tolerant": workload["delay_tolerant"],
            "Energy": f'{workload["energy_kwh"]} kWh',
        }
    ))

    with st.expander("View raw workload JSON", expanded=False):
        st.code(json.dumps(workload, indent=2), language="json")

    render_html(summary_card(
        "Best Schedule Option",
        {
            "Region": best["region"],
            "Start time": best["hour"],
            "Grid load": f'{best["grid_load"]}%',
            "Carbon intensity": f'{best["carbon_intensity"]} gCO₂/kWh',
            "Risk score": best["score"],
            "Approval required": best["approval_required"],
        }
    ))


    with st.expander("View raw schedule JSON", expanded=False):
        st.code(json.dumps(best, indent=2), language="json")

    st.write("**Selected schedule emissions:**", f"{result['selected_emissions_kg']} kgCO₂e")
    st.write("**Lowest-carbon option emissions:**", f"{result['lowest_carbon_emissions_kg']} kgCO₂e")
    st.write("**Carbon trade-off vs lowest-carbon option:**", f"{result['carbon_delta_vs_lowest_kg']} kgCO₂e")

    if result["grid_stress_avoided"]:
        render_html(alert_card(
            "Lowest-carbon option rejected",
            f"{result['lowest_carbon_option']['region']} had "
            f"{result['lowest_carbon_option']['grid_load']}% grid load. "
            "The agent selected a grid-safer option instead.",
            "amber",
        ))




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
        render_html(alert_card(
        "Auto-governed schedule",
        "Low-risk schedule. Auto-scheduling allowed under the current governance policy.",
        "green",
        ))
    

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


with tab3:
    # Gemini explanation
    st.subheader("Gemini Explanation")

    render_html(summary_card("Current scheduling context", {
        "Workload": workload["job"],
        "Selected region": best["region"],
        "Selected time": best["hour"],
        "Grid load": f'{best["grid_load"]}%',
        "Approval mode": "HUMAN REVIEW" if best["approval_required"] else "AUTO-GOVERNED",
    }))


    if st.button("Generate Gemini Explanation"):

        recent_decisions = load_recent_decisions_by_workload(
            workload_name=workload["job"],
            limit=3,
        )

        prompt = build_explanation_prompt(
            workload=workload,
            result=result,
            approval_status=st.session_state.get("approval_status", "unknown"),
            recent_decisions=recent_decisions,
        )

        with st.spinner("Generating Gemini explanation..."):
            gemini_result = generate_gemini_explanation(
                client=client,
                prompt=prompt,
            )

        if gemini_result["success"]:
            st.caption(f"Generated using model: {gemini_result['model']}")
            st.write(gemini_result["text"])
    
    


        else:
            st.warning(
                f"Gemini explanation could not be generated. "
                f"Last error: {gemini_result['error']}"
            )

            st.info(
                "Showing deterministic fallback explanation generated from scheduler facts."
            )

            fallback_text = build_fallback_explanation(
                workload=workload,
                result=result,
                approval_status=st.session_state.get("approval_status", "unknown"),
            )

            st.write(fallback_text)


with tab4:
    # Human approval workflow
    st.subheader("Human Approval")

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
            render_html(alert_card(
                "Schedule rejected",
                f"{workload['job']} · operator rejection recorded in the audit log.",
                "red",
            ))

        else:
            render_html(alert_card(
                "Pending human approval",
                "This high-risk schedule requires operator approval before execution.",
                "amber",
            ))

    else:
        render_html(alert_card(
            "Auto-governed schedule",
            "Low-risk schedule auto-approved under governance policy.",
            "green",
        ))
        st.session_state.approval_status = "auto-approved"

    render_html(summary_card("Governance record", {
        "Decision ID": decision_id,
        "Workload": workload["job"],
        "Approval required": str(best["approval_required"]),
        "Current status": st.session_state.get("approval_status", "unknown"),
        "Grid stress avoided": str(result["grid_stress_avoided"]),
    }))


audit_log = build_audit_log(
    decision_id=decision_id,
    workload=workload,
    result=result,
    approval_status=st.session_state.approval_status,
)

carbon_liability_record = build_carbon_liability_record(
    decision_id=decision_id,
    workload=workload,
    result=result,
    approval_status=st.session_state.approval_status,
    audit_log=audit_log,
)

audit_log["compute_carbon_liability_record"] = carbon_liability_record

audit_log_json = json.dumps(audit_log, indent=2)
carbon_liability_record_json = json.dumps(carbon_liability_record, indent=2)

with tab5:
    # Audit log
    
    st.subheader("Agent Tool Trace")

    render_html(summary_card("Agent Tool Trace", {
        "Tool 1": "MongoDB memory check",
        "Tool 2": "Load recent decisions",
        "Tool 3": "Score schedule options",
        "Tool 4": "Generate Gemini explanation",
        "Tool 5": "Save carbon decision to MongoDB ledger",
    }))

    # Audit log
    st.subheader("Compute Carbon Liability Record")

    render_html(summary_card(
        "Compute Carbon Liability Record",
        {
            "Liability Record ID": carbon_liability_record["liability_record_id"],
            "Workload ID": carbon_liability_record["workload"]["workload_id"],
            "Workload": carbon_liability_record["workload"]["workload_name"],
            "Energy": f'{carbon_liability_record["workload"]["energy_kwh"]} kWh',
            "Selected region": carbon_liability_record["selected_schedule"]["region"],
            "Selected time": carbon_liability_record["selected_schedule"]["time_window"],
            "Carbon intensity": f'{carbon_liability_record["carbon_accounting"]["carbon_intensity_gco2_per_kwh"]} gCO₂/kWh',
            "Gross compute carbon liability": f'{carbon_liability_record["carbon_accounting"]["gross_compute_carbon_liability_kgco2e"]} kgCO₂e',
            "Lowest-carbon option emissions": f'{carbon_liability_record["carbon_accounting"]["lowest_carbon_option_emissions_kgco2e"]} kgCO₂e',
            "Carbon trade-off": f'{carbon_liability_record["carbon_accounting"]["carbon_tradeoff_vs_lowest_kgco2e"]} kgCO₂e',
            "Grid-stress avoided": str(carbon_liability_record["grid_governance"]["grid_stress_avoided"]),
            "Approval status": carbon_liability_record["grid_governance"]["approval_status"],
            "Assurance": carbon_liability_record["assurance"]["assurance_status"],
            "Evidence": carbon_liability_record["assurance"]["evidence_reference"],
        }
    ))

    with st.expander("View raw carbon liability JSON", expanded=False):
        st.code(carbon_liability_record_json, language="json")

    st.subheader("AI Compute Carbon Liability Statement")

    render_html(summary_card(
        "AI Compute Carbon Liability Statement",
        {
            "Opening compute carbon liability": "0.0 kgCO₂e",
            "New workload emissions": f'{result["selected_emissions_kg"]} kgCO₂e',
            "Carbon avoided/traded off": f'{result["carbon_delta_vs_lowest_kg"]} kgCO₂e',
            "Residual compute carbon liability": f'{result["selected_emissions_kg"]} kgCO₂e',
            "Approval status": st.session_state.approval_status,
            "Evidence reference": decision_id,
            "Assurance status": "self-declared_future-auditable",
        }
    ))

    st.subheader("Audit Log Preview")

    render_html(summary_card(
        "Audit Log Summary",
        {
            "Decision ID": audit_log["decision_id"],
            "Workload": audit_log["workload"],
            "Selected region": audit_log["selected_region"],
            "Selected time": audit_log["selected_time"],
            "Approval status": audit_log["approval_status"],
            "Grid stress avoided": audit_log["grid_stress_avoided"],
            "Scheduler version": audit_log["scheduler_version"],
        }
    ))

    with st.expander("View raw audit JSON", expanded=False):
        st.code(json.dumps(audit_log, indent=2), language="json")

    st.download_button(
        label="Download Audit Log",
        data=audit_log_json,
        file_name=f"{audit_log['decision_id']}_audit_log.json",
        mime="application/json",
    )

    save_col1, save_col2 = st.columns(2)

    with save_col1:
        if st.button("Save Audit Log to MongoDB"):
            save_result = save_audit_log_to_mongodb(audit_log)

            if save_result["success"]:
                st.success(save_result["message"])
            else:
                st.error(save_result["message"])

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
            st.code(json.dumps(saved_logs, indent=2), language="json")
        else:
            st.info("No local audit logs found.")







