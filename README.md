# GridCarbon Guardian

## Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads

GridCarbon Guardian is a Gemini-powered scheduling prototype for AI and data-centre workloads. It helps decide when and where workloads should run by balancing carbon intensity, grid-load stress, deadline feasibility, human approval, and auditability.

Carbon-aware scheduling alone may choose the cleanest electricity window, but that window may still occur during severe grid stress. GridCarbon Guardian adds grid-load awareness, deadline protection, human approval, and MongoDB-backed audit logging so AI/data-centre workloads can be scheduled in a greener, safer, and more accountable way.

The MVP currently uses a transparent weighted scoring model, Gemini explanations, human-in-the-loop controls, and MongoDB decision memory. The broader product vision frames this as a research-grade, game-theoretic, bio-inspired, multi-agent system for grid-resilient AI infrastructure.

---

## Problem

AI workloads and data-centre operations are becoming more energy intensive. Many scheduling systems optimize for cost, latency, or carbon intensity, but they often ignore another critical factor: grid stress.

A low-carbon electricity window may still occur when the grid is under heavy load. Running compute-heavy workloads during that period may increase the risk of instability, brownouts, emergency generation, or grid strain.

GridCarbon Guardian addresses this gap by combining:

* carbon intensity
* grid-load stress
* workload deadlines
* workload flexibility
* human approval
* audit-ready decision records
* MongoDB-backed decision memory

### The Gap: Hyperscaler Black Boxes vs. Enterprise Compliance

Hyperscalers such as Google have explored internal carbon-intelligent computing systems that shift flexible workloads toward cleaner electricity windows. But those systems are proprietary, optimized for hyperscale infrastructure, and not easily available to ordinary enterprises, public-sector infrastructure teams, or data-centre operators in emerging economies.

Average enterprises need a transparent version of carbon-aware scheduling that is explainable, auditable, and compatible with compliance workflows.

GridCarbon Guardian is designed to bridge that gap.

### The Herd Effect: Why Simple Carbon Scheduling Fails

If every major data centre in a city uses the same public carbon signal, they may all identify the same “greenest” time window. For example, if 2:00 AM appears to be the cleanest and lowest-stress period, many operators may shift large AI workloads to that exact time.

If everyone does this simultaneously, they can create a new artificial demand peak and overload the grid anyway. This is the **Green Herd Effect**.

Standard carbon-aware schedulers often ignore this. GridCarbon Guardian treats carbon scheduling as a grid-coordination problem, not just a carbon-optimization problem.

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
10. Saves decision records into MongoDB decision memory.
11. Retrieves prior audit records from MongoDB for review.

### Multi-Agent Workflow Vision

GridCarbon Guardian is designed as a multi-agent AI system with three logical agents:

1. **Carbon & Grid Evaluator**
   Evaluates carbon intensity, grid load, and forecasted stress for each time-region option.

2. **Workload Planner**
   Scores scheduling options using carbon, grid stress, deadline risk, and latency/cost proxy.

3. **Governance & Audit Agent**
   Checks approval rules, records the decision, and prepares audit-ready rationale.

The current MVP implements this workflow inside a Streamlit application. The target cloud architecture is to orchestrate these agents through **Google Cloud Agent Builder / Vertex AI Agent Platform**, with Gemini used for rationale generation and MongoDB used as external decision memory.

---

## Core innovation

Most carbon-aware schedulers ask:

> When is electricity cleaner?

GridCarbon Guardian also asks:

> Is the grid safe enough, can the workload meet its deadline, should a human approve this decision, and has a similar decision happened before?

This makes the system not only carbon-aware, but also grid-resilient, governance-aware, and audit-ready.

### Core innovation pillars

GridCarbon Guardian combines five ideas:

1. **Carbon-aware scheduling**
   Shift flexible workloads toward cleaner electricity windows.

2. **Grid-stress-aware scheduling**
   Avoid clean but dangerous windows when grid load is too high.

3. **Game-theoretic routing**
   Use simplified Nash-style balancing to avoid sending all workloads to the same green window.

4. **Bio-inspired workload control**
   Use Honeybee Foraging and Ecological Torpor as design metaphors for adaptive, resilient scheduling.

5. **Audit-ready governance**
   Store decisions in MongoDB decision memory and require human approval for high-risk schedules.

---

## Solution: A Multi-Layer Game-Theoretic Architecture

Instead of scheduling in isolation, GridCarbon Guardian is framed as a multi-layer architecture combining a Stackelberg Game model, simplified Nash Equilibrium routing, adaptive thresholding, and bio-inspired resilience.

The MVP keeps the implementation simple: weighted scoring plus threshold-based approvals. The advanced architecture explains how the system can evolve into a more research-grade multi-agent scheduler.

### Layer 1: Macro-Framework — Stackelberg Game

The relationship between the grid and the scheduling agent can be modeled as a hierarchical Stackelberg Game.

* **Leader:** The grid operator or power system sends grid-stress signals, carbon signals, or dynamic pricing indicators.
* **Follower:** GridCarbon Guardian reacts by adjusting workload scheduling, capacity use, or approval requirements.

Judge-facing explanation:

> GridCarbon Guardian models the power utility as the game leader and the scheduling agent as the strategic follower. The agent translates grid-stress signals into real-time workload scheduling decisions.

### Layer 2: Routing Logic — Nash Equilibrium

If multiple regions or clusters are available, the agent should not blindly send all workloads to the cleanest region. That could overload the same local grid.

A simplified Nash-style routing layer helps distribute workload across regions so no single green window becomes overloaded.

In the MVP, this is represented by comparing carbon, grid load, deadline feasibility, and risk score across regions. Future versions can implement a full game matrix using `numpy` and `scipy`.

Judge-facing explanation:

> GridCarbon Guardian avoids the Green Herd Effect by balancing workloads across regions instead of dumping all jobs into the same clean but stressed window.

### Layer 3: Execution Engine — Online Optimization and Dynamic Thresholds

The current MVP uses a weighted scoring model:

```text
Final Risk Score =
0.40 × Carbon Intensity Score
+ 0.30 × Grid Stress Score
+ 0.20 × Deadline Risk Score
+ 0.10 × Latency Score
```

Future versions can adapt this into a Follow-the-Leader style online optimizer. If recent carbon or grid forecasts are volatile, the system can lower its risk tolerance and require more conservative scheduling.

MVP interpretation:

> The current weighted scoring model is a simplified prototype of adaptive online scheduling.

### Layer 4: Bio-Inspired Resilience — Honeybee Foraging and Ecological Torpor

Nature provides useful metaphors for resilient scheduling.

* **Honeybee Foraging:** Bees search for rich flower patches but avoid overcrowding through distributed signaling. GridCarbon Guardian similarly searches for cleaner energy windows while avoiding overloading one grid region.
* **Ecological Torpor:** Some organisms temporarily lower activity during stress. GridCarbon Guardian can freeze or delay flexible workloads during extreme grid stress, reducing digital infrastructure demand until conditions improve.

MVP interpretation:

> The current prototype demonstrates the torpor concept by delaying or rejecting flexible workloads when the cleanest option is still grid-stressed.

---

## Demo Scenarios

### Scenario 1: Flexible workload — Ecological Torpor / Auto-Approved

**Workload:** AI batch inference
**Type:** Delay-tolerant
**Result:** The lowest-carbon option is rejected because grid load is 94%. The agent selects a grid-safer window that still meets the deadline. The decision is auto-approved.

This demonstrates:

* grid-stress-aware scheduling
* ecological torpor concept for flexible workloads
* rejection of unsafe low-carbon windows
* autonomous low-risk scheduling
* audit-ready logging
* MongoDB-backed decision memory

### Scenario 2: Urgent workload — Human-Reviewed Routing

**Workload:** Urgent AI model retraining
**Type:** Non-delay-tolerant
**Result:** The workload must meet a tight deadline. The system selects the only deadline-feasible option, but because grid load is 94%, human approval is required. The operator can approve or reject the schedule.

This demonstrates:

* deadline-sensitive scheduling
* high grid-stress escalation
* human-in-the-loop governance
* auditability of approval and rejection decisions
* MongoDB-backed governance history

### Future Scenario: Nash Equilibrium Routing

In a fuller version, the agent can split workloads across regions to avoid the Green Herd Effect. For example:

* Region A may be clean but stressed.
* Region B may be dirtier but stable.
* The agent can route only part of the workload to Region A and shift the rest to Region B.

This would demonstrate game-theoretic routing and distributed grid stabilization.

---

## Scheduling Logic

The scheduler scores each available option using:

* carbon intensity score
* grid stress score
* deadline risk score
* latency/cost proxy

The current prototype uses a weighted scoring model:

```text
Total Score =
0.40 × Carbon Intensity Score
+ 0.30 × Grid Stress Score
+ 0.20 × Deadline Risk Score
+ 0.10 × Latency Score
```

Lower score means a better scheduling option.

Deadline violations are strongly penalized. High grid load, non-delay-tolerant workloads, and high-risk schedules trigger human approval.

The scoring engine is intentionally simple for the MVP. It is designed to be transparent, easy to audit, and explainable to non-technical operators.

---

## Gemini Integration

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

### Google Cloud Agent Builder Integration

The target multi-agent workflow is designed for orchestration using **Google Cloud Agent Builder / Vertex AI Agent Platform**.

The intended Agent Builder flow is:

1. Get workload.
2. Fetch carbon and grid data.
3. Score candidate options.
4. Select a schedule.
5. Generate Gemini explanation.
6. Check governance rules.
7. Store decision in MongoDB.
8. Trigger human approval if high-risk.

Logical agents:

* **Carbon & Grid Evaluator**
* **Workload Planner**
* **Governance & Audit Agent**

The current MVP implements these logical roles inside a Streamlit application. A fuller cloud version would externalize orchestration through Agent Builder and expose MongoDB tools through MCP.

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

Approval status is recorded in the audit log and stored in MongoDB decision memory.

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
* saved locally as fallback
* stored in MongoDB Atlas
* retrieved as MongoDB-backed decision history

---

## MongoDB Decision Memory

GridCarbon Guardian uses **MongoDB Atlas** as a persistent decision-memory layer.

Every scheduling decision can be stored in the `gridcarbon_guardian.audit_logs` collection, including:

* workload name
* selected region and time
* carbon intensity
* grid load
* deadline feasibility
* approval requirement
* approval status
* carbon trade-off
* timestamp
* decision ID

This allows the agent to preserve governance history across sessions instead of treating every scheduling decision as isolated.

### Current implementation

The current MVP implements MongoDB decision memory using:

* MongoDB Atlas
* PyMongo
* `gridcarbon_guardian.audit_logs`
* Streamlit dashboard retrieval
* MongoDB-backed audit history

### MongoDB MCP Server alignment

The project is designed to align with the **MongoDB MCP Server** partner track.

In the current code, the Streamlit app writes and reads audit logs through PyMongo. The intended MCP extension is to expose the same `audit_logs` collection to MCP-capable AI clients through the official MongoDB MCP Server.

MCP-aligned agent capabilities:

* query previous scheduling decisions
* store new scheduling decisions
* inspect approval history
* retrieve governance context before generating Gemini rationale

Important implementation note:

> The current MVP uses MongoDB Atlas and PyMongo directly. Full MCP-native operation should be claimed only after the official MongoDB MCP Server is configured and demonstrated.

---

## Data Sources

The current MVP uses mock/synthetic carbon and grid-load data to make the two demo scenarios reproducible.

Target data integrations:

* **Electricity Maps API** for carbon intensity
* regional grid-load API where available
* realistic synthetic grid-stress data where public grid APIs are unavailable

Using mock data is intentional at the MVP stage because the core goal is to prove the scheduling, governance, and audit workflow before integrating live data feeds.

---

## Tech Stack

### Core

* Python
* Streamlit
* pandas
* Google Gen AI SDK
* Gemini API
* python-dotenv
* PyMongo
* JSON fallback audit logging

### Planned analytical extensions

* numpy
* scipy
* game-theoretic routing logic
* adaptive thresholding
* bio-inspired scheduling modules

### Google Cloud

* Gemini API
* Vertex AI Agent Platform / Google Cloud Agent Builder
* Cloud Run
* Secret Manager

### Partner storage / MCP alignment

* MongoDB Atlas
* MongoDB decision memory
* MongoDB MCP Server alignment

### Data Sources

* synthetic carbon and grid-load data in the MVP
* Electricity Maps API for future carbon intensity integration
* grid-load API or synthetic regional grid data

---

## Project Files

Current MVP files:

```text
gridcarbon-guardian/
│
├── app.py                    # Streamlit dashboard
├── scheduler.py              # Weighted scoring and deadline logic
├── data.py                   # Mock workload and schedule data
├── mongo_store.py            # MongoDB Atlas audit memory integration
├── requirements.txt
├── README.md
├── .gitignore
└── audit_logs.json           # Local fallback only, ignored by Git
```

Target architecture files for future extension:

```text
gridcarbon-guardian/
│
├── game_theory.py            # Nash-style routing logic
├── adaptive_optimizer.py     # FTL-style dynamic thresholds
├── bio_inspired.py           # Honeybee Foraging and Torpor logic
├── agent_workflow.yaml       # Agent Builder workflow definition
├── mongodb_mcp_tools.py      # MCP tool wrappers
├── Dockerfile
└── audit_logs/
    └── sample_decisions.json
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
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=gridcarbon_guardian
MONGODB_COLLECTION=audit_logs
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

Current MVP requirements:

```text
streamlit
python-dotenv
google-genai
pandas
pymongo
```

Optional future requirements:

```text
requests
numpy
scipy
plotly
```

---

## Current Prototype Status

The current MVP demonstrates:

* carbon-aware scheduling using reproducible mock data
* grid-stress-aware decision logic
* deadline feasibility checking
* Gemini-generated explanations
* human approval workflow
* approval/rejection recording
* downloadable JSON audit logs
* persistent audit history in MongoDB Atlas
* local JSON fallback audit history
* GitHub-hosted source code

The current MVP does not yet fully implement:

* live Electricity Maps API integration
* full Nash Equilibrium matrix solver
* full Stackelberg optimization layer
* official MongoDB MCP Server runtime integration
* Cloud Run deployment
* full Google Cloud Agent Builder orchestration

These are the next build targets.

---

## Future Roadmap

Planned improvements include:

* Cloud Run deployment
* Secret Manager for production credential handling
* Electricity Maps API integration
* grid-load API or stronger synthetic grid-stress generator
* Plotly carbon/grid timeline visualization
* richer dashboard visualizations
* game-theoretic routing with numpy/scipy
* adaptive thresholds inspired by Follow-the-Leader
* bio-inspired torpor and honeybee workload routing
* policy-as-code governance rules
* standards-aware control mapping
* downloadable PDF compliance report
* Arize or Dynatrace integration for agent behavior observability and performance tracing
* official MongoDB MCP Server demonstration

---

## Why it matters

As AI workloads grow, energy scheduling must move beyond cost and carbon alone. Responsible workload orchestration should also consider grid resilience, infrastructure stress, human oversight, and auditability.

GridCarbon Guardian demonstrates how AI agents can support greener, safer, and more accountable digital infrastructure.

It is especially relevant for grid-stressed regions where clean-energy scheduling decisions cannot be separated from infrastructure reliability.

---

## Devpost Submission Text

### Title

**GridCarbon Guardian**
Carbon-aware, grid-stress-aware scheduling agent for AI/data-centre workloads

### Tagline

A Gemini-powered workload scheduling agent using MongoDB decision memory for grid-resilient, audit-ready AI/data-centre operations.

### Inspiration

AI and data-centre workloads are becoming more energy-intensive. Most carbon-aware schedulers optimize only for carbon intensity, ignoring grid stress.

GridCarbon Guardian is inspired by carbon-aware computing approaches, but extends the idea for grid-resilient and audit-ready workload scheduling. It combines carbon intensity, grid-load stress, deadline feasibility, human approval, and MongoDB-backed decision memory into one transparent scheduling prototype.

The key insight is simple:

> The cleanest electricity window is not always the safest grid window.

### What it does

GridCarbon Guardian:

* evaluates carbon intensity and grid stress for multiple time-region options
* recommends a schedule that balances carbon, grid resilience, and deadlines
* rejects low-carbon options that are too grid-stressed
* escalates urgent high-risk schedules for human approval
* uses Gemini to generate audit-ready explanations
* records every decision in MongoDB decision memory
* allows operators to download JSON audit logs

### How we built it

We built the MVP with:

* Python
* Streamlit
* Gemini API / Google Gen AI SDK
* MongoDB Atlas
* PyMongo
* pandas
* JSON audit logging

The scheduler uses a transparent weighted scoring model:

```text
40% carbon intensity
+ 30% grid stress
+ 20% deadline risk
+ 10% latency/cost proxy
```

Gemini generates the explanation layer, while MongoDB stores the governance memory layer.

### Use of Google Cloud

The project uses Gemini API for explanation generation and is designed for deployment on Google Cloud.

Target Google Cloud architecture:

* Gemini API for reasoning and explanation generation
* Vertex AI Agent Platform / Google Cloud Agent Builder for multi-agent orchestration
* Cloud Run for hosting
* Secret Manager for credentials

### Use of sponsor product

GridCarbon Guardian uses MongoDB Atlas as its decision-memory layer.

The `gridcarbon_guardian.audit_logs` collection stores:

* workload decisions
* approval status
* carbon-grid trade-offs
* grid-load risk
* timestamps
* audit metadata

The project is aligned with the MongoDB MCP Server partner track because the same audit collection can be exposed as agent-accessible memory through MongoDB MCP tools.

### Challenges we ran into

* Balancing carbon optimization with grid-stress risk
* Designing a simple but explainable scoring model
* Handling urgent workloads that cannot wait for cleaner windows
* Making Gemini explanations audit-ready instead of generic
* Creating a persistent decision-memory layer in MongoDB
* Keeping the MVP realistic while designing a more advanced multi-agent architecture

### Accomplishments

* Built a working carbon-grid scheduling prototype
* Implemented deadline feasibility logic
* Added human-in-the-loop approval
* Added Gemini-generated rationale
* Added downloadable JSON audit logs
* Added MongoDB-backed decision memory
* Created two clear demo scenarios: auto-approved flexible workload and human-reviewed urgent workload

### What we learned

* Carbon-aware scheduling without grid-stress awareness can still be risky
* Human-in-the-loop governance is important for critical-infrastructure decisions
* Auditability is essential for trustworthy AI infrastructure operations
* MongoDB can act as a practical decision-memory layer for AI agents
* A simple transparent scoring model can be more trustworthy than a black-box scheduler

### What is next

Next steps include:

* Cloud Run deployment
* Electricity Maps API integration
* official MongoDB MCP Server demonstration
* Agent Builder orchestration
* policy-as-code governance
* game-theoretic routing
* bio-inspired torpor and honeybee scheduling logic
* Arize or Dynatrace observability


## MongoDB MCP / Partner Tool Integration
GridCarbon Guardian uses MongoDB Atlas as the agent’s persistent decision-memory and audit-ledger layer. The project exposes MongoDB-backed tool functions for saving carbon decisions, retrieving recent decisions, loading the audit ledger, and checking memory status. These functions are structured as MCP-aligned partner tools and can be migrated to the official MongoDB MCP Server interface.



## Google ADK / Agent Builder Compatibility

GridCarbon Guardian includes an ADK-compatible agent entrypoint in `adk_agent.py`.

The ADK agent exposes two tools:

1. `schedule_gridcarbon_workload`
   - retrieves workload data
   - checks MongoDB memory
   - scores carbon/grid schedule options
   - applies governance logic
   - creates an audit log
   - stores the decision in MongoDB

2. `view_gridcarbon_audit_ledger`
   - retrieves recent MongoDB audit-ledger records

This provides a code-first Agent Builder / ADK path while the Streamlit app remains the judge-facing web demo.


The current MVP includes:
- a Streamlit web app for the operator interface
- a Google ADK-style Gemini agent definition in adk_agent.py
- MongoDB Atlas decision memory
- MCP-aligned MongoDB tool wrappers
- Cloud Run-ready deployment structure

The MVP does not claim full official MongoDB MCP Server runtime deployment unless that server is separately configured and demonstrated.

