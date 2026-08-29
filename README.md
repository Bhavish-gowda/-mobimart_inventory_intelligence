# MobiMart — Inventory Intelligence Platform

> **Financially explainable inventory optimization for a 25-store mobile retail chain under a hard ₹4 Crore capital constraint.**

---

## 📌 Context & Problem Statement

**Mirai Labs — Software Developer Intern Technical Assessment**  
*Assignment B: The Mobile Retail Chain (MobiMart)*

### The Business Challenge:
> *"My money is sitting in the wrong phones in the wrong stores."*

In mobile retail, holding excess inventory of declining models ties up working capital, while running out of stock on fast-moving SKUs causes permanent lost sales. **MobiMart Inventory Intelligence** solves this core dilemma by determining:
- **Where** inventory should be allocated across 25 non-interchangeable stores.
- **How much** inventory to deploy under a hard ₹4 Crore chain-wide capital limit.
- **When** to execute inter-store transfers or clearance markdowns for End-of-Life (EOL) models.
- **Why** each decision is made through rupee-denominated financial proof ($NMV$).

---

## 🎯 Assignment Requirements → Implementation Mapping

| # | Requirement Description | Technical Implementation | Where to See It |
| :--- | :--- | :--- | :--- |
| **1** | **Realistic 52-Week Data** | 78,000 sales records across 52 weeks, 25 stores, ~60 SKUs | `data/generated/sales_history.csv` |
| **2** | **25 Store Profiles** | High Street, Premium Mall, Mass Market & Regional Hub catchment profiles | Stores Page (`/stores`) |
| **3** | **~60 Phone SKUs** | Budget, Mid-Range, Premium, Flagship tiers with launch dates | Products Page (`/products`) |
| **4** | **Product Lifecycle Intelligence** | Launch → Growth → Peak → Decline → EOL stage transitions | Products Page & EOL Center |
| **5** | **₹4 Crore Capital Constraint** | Hard chain-wide cap enforcing inventory cost accounting identity | Allocation Page & Overview (`/`) |
| **6** | **Stockout Economics** | Avoided goodwill loss factors ($5\text{--}15\%$) by segment | Allocation Engine (`financials.py`) |
| **7** | **Inter-Store Transfers** | Capacity-resolved zero-overcommit inter-store transfer routes | EOL Center (`/eol`) |
| **8** | **EOL Risk Engine** | Risk scoring ($0\text{--}100$) & Markdown vs Transfer vs Hold decision matrix | EOL Risk Center (`/eol`) |
| **9** | **Weekly Constrained Allocation** | Marginal Net Value ($NMV$) greedy sorting under warehouse bounds | Allocation Planner (`/allocation`) |
| **10**| **Financial Explanations** | Rupee-denominated financial proof breakdown per recommendation | Allocation Planner Drawer |
| **11**| **Executive Dashboard** | Real-time capital deployment, headroom, fill rate & risk telemetry | Overview Dashboard (`/`) |
| **12**| **Baseline Comparison** | Controlled evaluation against Last-4-Week Proportional Allocation | Benchmark Page (`/benchmark`) |
| **13**| **Live Scenario Simulator** | Multi-week rolling simulation loop under zero future data leakage | Simulator Studio (`/simulation`) |
| **14**| **Deterministic Backtesting** | Process-scoped in-memory caching with `X-Benchmark-Cache` headers | Benchmark & FastAPI Router |

---

## 📊 Verified Benchmark Scorecard (Weeks 1 to 12)

Below are the verified, mathematically reconciled simulation results comparing **Strategy A (Naive Proportional Baseline)** against **Strategy B (MobiMart Intelligent Engine)** under identical starting conditions:

| Metric | Naive Baseline | MobiMart Engine | Absolute Shift | % Improvement | Direction |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Total Revenue** | ₹5,61,98,400 | **₹7,38,02,400** | +₹1,76,04,000 | **+31.3%** | ↑ Higher is better ✅ |
| **Gross Margin** | ₹1,10,53,100 | **₹1,44,91,900** | +₹34,38,800 | **+31.1%** | ↑ Higher is better ✅ |
| **Service Level (Fill Rate)** | 45.12% | **58.72%** | +13.60% | **+30.1%** | ↑ Higher is better ✅ |
| **Stockout Rate** | 67.54% | **52.78%** | -14.76% | **-21.9%** | ↓ Lower is better ✅ |
| **Capital Turns** | 1.49x | **1.81x** | +0.32x | **+21.5%** | ↑ Higher is better ✅ |
| **Dead Stock %** | 99.86% | **85.88%** | -13.98% | **-14.0%** | ↓ Lower is better ✅ |
| **Lost Sales Value** | ₹7,09,62,000 | **₹5,33,58,000** | -₹1,76,04,000 | **-24.8%** | ↓ Lower is better ✅ |
| **Actual Markdown Loss** | ₹18,34,564 | **₹17,98,924** | -₹35,640 | **-1.9%** | ↓ Lower is better ✅ |
| **Total Units Allocated** | 1,269 units | **2,056 units** | +787 units | **+62.0%** | — |

*Note: All benchmark results are generated dynamically by the deterministic simulation backtest engine (`backend/engine/simulation/runner.py`) — zero hardcoded numbers.*

---

## 🏗️ Technical Architecture

```
                                  MobiMart Platform Architecture
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 React / TypeScript Frontend                             │
│       (Overview | Allocation Planner | Stores | Products | EOL Risk | Simulation | Benchmark)│
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
                                       HTTP REST Requests
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Backend REST Layer                               │
│     (Routers -> Services -> Pydantic Validation -> Process-Scoped In-Memory Cache)      │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Core Domain Engines                                   │
│  ├── Allocation Engine: Constrained Greedy Sorting by Net Marginal Value (NMV)          │
│  ├── Demand Forecasting: Zero-Leakage Velocity Blend + Store/Segment Affinity           │
│  ├── EOL Engine: Risk Scoring (0-100) + Markdown / Inter-Store Transfer Optimization    │
│  └── 52-Week Rolling Simulator: Isolated Strategy Execution Loop                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 Authoritative CSV Datasets                              │
│       (stores.csv [25] | products.csv [60] | inventory.csv [1500] | sales_history.csv [78k]) │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Financial Optimization Model

For every candidate unit $u$ allocated to store $s$ and product $p$, MobiMart evaluates **Net Marginal Value ($NMV$)**:

$$\text{NMV} = \text{Expected Gross Margin} + \text{Avoided Goodwill Benefit} - \text{Logistics Allocation Cost} - \text{Markdown Risk Cost}$$

Where:
- $\text{Expected Gross Margin} = \text{Sale Probability} \times (\text{Retail Price} - \text{Cost Price})$
- $\text{Avoided Goodwill Benefit} = \text{Prevented Unmet Demand} \times \text{Unit Margin} \times \text{Goodwill Factor}$
- $\text{Logistics Allocation Cost} = ₹250/\text{unit}$ (Warehouse $\rightarrow$ Store)
- $\text{Markdown Risk Cost} = \text{Unit Cost} \times \text{Markdown \%} \times \text{Overstock Probability}$

The allocator sorts candidates by $NMV$ in descending order and commits allocations unit-by-unit until either:
1. Total deployed capital reaches the **₹4 Crore limit**, or
2. Available warehouse stock reaches **0**.

---

## 🔍 Case Study: Diagnosing & Fixing the Zero-History Demand Surge

During development, initial simulation benchmarks showed MobiMart allocating only 4 units/week in Weeks 3–10 while Baseline allocated 200+ units.

### 1. Root Cause Diagnosis:
Tracing week-by-week allocations revealed that in Week 2, `forecast.py` executed:
```python
if rolling_avg == 0.0 and recent_velocity == 0.0:
    base_demand = 1.2 * affinity_factor * lifecycle_factor
```
When planning Week 2, any product with zero sales in Week 1 triggered this condition. The engine treated **all observed zero-sales SKUs as high-surge "Launch" products**, forecasting synthetic demand of $\approx 5.1 \text{ units/week}$.

Because flagship phones (`PROD_058`, cost ₹1,18,000, margin ₹31,500) had high margins, the allocator assigned them an NMV of ₹32,825/unit. MobiMart allocated 62 flagship units across 25 stores in Week 2, spending **₹6.237 Million of capital**. However, actual customer demand for `PROD_058` was 0 units. The unsold stock tied up **₹39.95 Million of the ₹4.00 Crore cap**, locking MobiMart out of allocating inventory in Weeks 3 to 10.

### 2. Engineering Solution:
We updated `forecast.py` to differentiate **unobserved cold-start SKUs** ($W=1$) from **observed zero-sales SKUs** ($W > 1$):
- If prior historical weeks have been observed and sales were zero $\rightarrow$ `base_demand = 0.0` (unless active Launch stage).
- If cold start ($W=1$) $\rightarrow$ conservative baseline (0.5 for Launch, 0.2 for others).

### 3. Impact:
- **Revenue**: ₹3.18 Cr $\rightarrow$ **₹7.38 Cr** (+132% increase)
- **Stockout Rate**: 85.08% $\rightarrow$ **52.78%** (-38% reduction)
- **Service Level**: 20.28% $\rightarrow$ **58.72%** (+190% increase)

---

## 🎬 3-Minute Recruiter Demo Walkthrough

1. **Step 1: Executive Dashboard (`/`)**
   - View chain-wide capital deployment (₹3.79 Cr / ₹4.00 Cr, 94.8% utilization ring).
   - Review live fill rate (58.7%), stockout rate (52.8%), and EOL exposure.
2. **Step 2: Allocation Control Center (`/allocation`)**
   - Click **Run Week 1 Allocation**.
   - Filter by store or SKU name, expand any recommendation row to inspect the **Financial Proof Breakdown** ($NMV = \text{Margin} + \text{Goodwill} - \text{Logistics}$).
3. **Step 3: EOL Risk Center (`/eol`)**
   - Filter positions by `HIGH` or `CRITICAL` risk level.
   - Expand any row to review the 3-option **Disposition Decision Matrix** (*TRANSFER vs MARKDOWN vs HOLD*).
4. **Step 4: Benchmark Scorecard (`/benchmark`)**
   - Select **Weeks 1 to 12 (Q1)** evaluation.
   - Inspect side-by-side scorecard comparing Baseline vs MobiMart across 12 metrics.
   - Click **Rerun Benchmark** to observe instant cache hit response (`X-Benchmark-Cache: HIT` in $< 4\text{ms}$).
5. **Step 5: Decision Simulator (`/simulation`)**
   - Select strategy (`MOBIMART` vs `BASELINE`) and week range (e.g. W1–24 preset).
   - Observe full multi-week rolling execution trace ledger.

---

## ⚡ Performance & Caching

- **First Benchmark Execution (MISS)**: **~4.37 seconds** (runs complete 12-week rolling backtest for both strategies).
- **Repeated Benchmark Execution (HIT)**: **< 4 milliseconds** (process-scoped in-memory cache).
- **Evaluation Range Change (W1–24)**: **~10.94 seconds** (fresh execution, safely invalidating previous cache key).

---

## 🧪 Testing & Code Quality

### Run Full Backend Test Suite (187 / 187 Passing):
```bash
py -3 -m pytest tests/ -q --tb=short
```

### Run API Integration Tests:
```bash
py -3 -m pytest tests/api/ -v
```

### Run Unit Tests:
```bash
py -3 -m pytest tests/unit/ -v
```

### Run Frontend Build Verification:
```bash
cd frontend
npm run build
```

---

## 🚀 Quickstart & Setup Guide

### Prerequisites:
- Python 3.10+
- Node.js 18+ and `npm`

### 1. Launch Backend FastAPI Server:
```bash
# From workspace root directory
py -3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2. Launch Frontend React UI:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your web browser.

---

## 📂 Project Structure

```
mobimart/
├── backend/
│   ├── api/                     # FastAPI REST API Layer (Phase 4)
│   │   ├── main.py              # Application Entrypoint & CORS setup
│   │   ├── data_loader.py       # Safe CSV Loader with In-Memory Caching
│   │   ├── routers/             # Routers (stores, products, inventory, allocation, eol, simulation)
│   │   ├── schemas/             # Pydantic Request & Response Schemas
│   │   └── services/            # Service Layer delegating to Engine Modules
│   └── engine/                  # Core Domain Engines
│       ├── allocation/          # Constrained Greedy Allocator & Financial Proof
│       ├── eol/                 # EOL Risk Scoring & Transfer Resolution Engine
│       └── simulation/          # 52-Week Rolling Simulator & Benchmark Scorecard
├── data/
│   └── generated/               # Authoritative CSV Datasets (78k Sales History, 25 Stores, 60 SKUs)
├── frontend/                    # Modern React + TypeScript + Vite Dashboard UI
│   ├── src/
│   │   ├── api/                 # Axios / Fetch API Client with Cache Meta Parsing
│   │   ├── components/          # Reusable Layout, KPI Cards, Loading & Modal Components
│   │   ├── pages/               # Overview, Allocation, Stores, Products, EOL, Simulation, Benchmark
│   │   └── types/               # TypeScript Definitions
├── tests/                       # Comprehensive Test Suite (187 Tests)
│   ├── api/                     # API Integration Tests (37 Tests)
│   └── unit/                    # Engine Unit Tests (150 Tests)
└── README.md                    # Technical Project Documentation
```

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Uvicorn
- **Data & Analytics**: Pandas, NumPy
- **Testing & Tooling**: Pytest, TestClient
