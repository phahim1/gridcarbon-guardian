# GridCarbon Guardian

## Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads

GridCarbon Guardian is a Google Gemini-powered prototype that helps schedule flexible AI and data-centre workloads in a greener, safer, and more accountable way.

Carbon-aware scheduling alone may choose the cleanest electricity window, but that window may still occur during severe grid stress. GridCarbon Guardian adds grid-load awareness, deadline protection, human approval, and audit logging so AI/data-centre workloads can be scheduled with both sustainability and infrastructure resilience in mind.

---

## Problem

AI workloads and data-centre operations are becoming more energy intensive. Many scheduling systems optimize for cost, latency, or carbon intensity, but they often ignore another important factor: grid stress.

A low-carbon electricity window may still occur when the grid is under heavy load. Running compute-heavy workloads during that period may increase the risk of instability, brownouts, or the need for emergency generation.

GridCarbon Guardian addresses this gap by combining:

- carbon intensity
- grid-load stress
- workload deadlines
- workload flexibility
- human approval
- audit-ready decision records

---

## What it does

GridCarbon Guardian recommends when and where an AI/data-centre workload should run.

For each workload, the system:

1. Reads workload requirements.
2. Compares available time-region scheduling options.
3. Calculates a multi-factor risk score.
4. Checks whether the lowest-carbon option is grid-stressed.
5. Checks whether the workload can meet its deadline.
6. Recommends the safest schedule.
7. Uses Gemini to explain the decision.
8. Requires human approval for high-risk cases.
9. Generates a downloadable audit log.
10. Saves decision records into local audit history.

---

## Core innovation

Most carbon-aware schedulers ask:

> When is electricity cleaner?

GridCarbon Guardian also asks:

> Is the grid safe enough, can the workload meet its deadline, and should a human approve this decision?

This makes the system not only carbon-aware, but also grid-resilient and governance-aware.

---

## Demo scenarios

### Scenario 1: Flexible workload — auto-approved

**Workload:** AI batch inference  
**Result:** The lowest-carbon option is rejected because grid load is 94%. The agent selects a grid-safer option that meets the deadline and is auto-approved.

This demonstrates:

- carbon/grid trade-off
- deadline feasibility
- autonomous low-risk scheduling
- audit-ready logging

### Scenario 2: Urgent workload — human-reviewed

**Workload:** Urgent AI model retraining  
**Result:** The workload is urgent and non-delay-tolerant. The system selects the only deadline-feasible option, but because grid load is 94%, human approval is required. The operator can approve or reject the schedule.

This demonstrates:

- deadline-sensitive scheduling
- human-in-the-loop governance
- grid-risk escalation
- auditability of rejected decisions

---

## Scheduling logic

The scheduler scores each available option using:

- carbon intensity score
- grid stress score
- deadline risk score
- latency/cost proxy

The current prototype uses a weighted scoring model:

```text
Total Score =
0.40 × Carbon Intensity Score
+ 0.30 × Grid Stress Score
+ 0.20 × Deadline Risk Score
+ 0.10 × Latency Score

Lower score means a better scheduling option.

Deadline violations are strongly penalized. High grid load, non-delay-tolerant workloads, and high-risk schedules trigger human approval.

---

## Gemini integration

Gemini is used to generate professional, audit-ready explanations of each scheduling decision.

The explanation includes:

* why the selected schedule was chosen
* why grid stress matters
* whether human approval is required
* a short audit-ready note

The app uses the Google Gen AI SDK with fallback model handling.

Primary model:

```text
gemini-2.5-flash
```

Fallback models:

```text
gemini-2.0-flash
gemini-2.0-flash-lite
```

---

## Human-in-the-loop governance

GridCarbon Guardian supports two governance modes:

1. **Auto-approval**
   Low-risk schedules can be automatically approved under governance policy.

2. **Human approval**
   High-risk schedules require operator approval before execution.

The operator can:

* approve schedule
* reject schedule
* reset approval status

Approval status is recorded in the audit log.

---

## Audit logging

Each scheduling decision generates an audit record containing:

* decision ID
* timestamp
* workload name
* selected region
* selected time
* carbon intensity
* grid load
* selected emissions
* lowest-carbon alternative
* carbon trade-off
* approval requirement
* approval status
* grid-stress decision flag

Audit logs can be:

* previewed in the app
* downloaded as JSON
* saved to local audit history

---

## Tech stack

* Python
* Streamlit
* Google Gen AI SDK
* Gemini API
* python-dotenv
* MongoDB Atlas
* PyMongo
* JSON audit logging
* Local audit history


Google Cloud setup prepared:

* Google Cloud project
* Gemini API
* Agent Platform API
* Cloud Run Admin API
* Cloud Build API
* Artifact Registry API
* Secret Manager API
* Firestore API

## MongoDB decision memory

GridCarbon Guardian uses MongoDB Atlas as a persistent decision-memory layer.

Every scheduling decision can be stored in the `gridcarbon_guardian.audit_logs` collection, including:

- workload name
- selected region and time
- carbon intensity
- grid load
- deadline feasibility
- approval requirement
- approval status
- carbon trade-off
- timestamp
- decision ID

This allows the agent to preserve governance history across sessions instead of treating every scheduling decision as isolated.

In the current MVP, MongoDB stores and retrieves audit decisions through a Python integration using PyMongo. The MongoDB-backed audit history is shown inside the app under 

**MongoDB Decision Memory**.

Future work will extend this into a fuller MongoDB MCP-based agent memory layer, allowing the agent to query previous scheduling decisions and use them directly in Gemini-generated rationales.

---

## Project files

```text
gridcarbon-guardian/
│
├── app.py
├── scheduler.py
├── data.py
├── requirements.txt
├── .env
├── README.md
└── audit_logs.json
```

---

## How to run locally

1. Clone or open the project folder.

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

4. Run the app:

```bash
streamlit run app.py
```

5. Open the local app:

```text
http://localhost:8501
```

---

## Requirements

```text
streamlit
python-dotenv
google-genai
pandas
```

---

## Current prototype status

The current MVP demonstrates:

* carbon-aware scheduling
* grid-stress-aware decision logic
* deadline feasibility checking
* Gemini-generated explanations
* human approval workflow
* approval/rejection recording
* downloadable JSON audit logs
* persistent local audit history

---

## Future roadmap

Planned improvements include:

* Firestore or MongoDB audit storage
* Cloud Run deployment
* integration with real carbon-intensity APIs
* integration with grid-load or weather APIs
* sponsor MCP integration
* richer dashboard visualizations
* policy-as-code governance rules
* standards-aware control mapping
* downloadable PDF compliance report

---

## Why it matters

As AI workloads grow, energy scheduling must move beyond cost and carbon alone. Responsible workload orchestration should also consider grid resilience, infrastructure stress, human oversight, and auditability.

GridCarbon Guardian demonstrates how AI agents can support greener, safer, and more accountable digital infrastructure.
