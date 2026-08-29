# MobiMart — Inventory Intelligence Platform

> **An intelligent inventory decision-support platform that helps a multi-store mobile retailer decide what stock to allocate, where to place it, when to move aging stock, and how to maximize revenue under a hard ₹4 Crore capital constraint.**

---

## 📌 What is MobiMart?

Imagine **MobiMart** operates a chain of **25 retail stores** across Karnataka, selling **60 smartphone models** ranging from budget devices (₹10,000) to premium flagships (₹1,20,000+). 

Every week, retail operations managers face a complex puzzle:
- **Which phone models** should we order and ship from the central warehouse?
- **Which specific stores** actually need more inventory this week?
- **How many units** should each store receive?
- **Which stores** are likely to sell high-end flagship phones versus budget models?
- **Which inventory** is becoming outdated or risky as newer phone models launch?
- **Should an aging phone** be transferred to another store, marked down for clearance, or held as-is?
- **How do we make all these decisions** without exceeding our hard **₹4 Crore chain-wide working capital limit**?

### The Business Dilemma:
> *"My money is sitting in the wrong phones in the wrong stores."*

In mobile retail, stocking too many declining models ties up valuable cash in unsold inventory (dead stock). At the same time, running out of stock on high-demand models results in permanent lost revenue and frustrated customers. 

### Our Solution in Easy Words:
**MobiMart turns these high-stakes decisions into a data-driven, financially explainable workflow.** 

Instead of relying on intuition or simple spreadsheets, MobiMart combines:
1. **Demand Forecasting**: Predicting upcoming sales based on historical velocity and store profiles.
2. **Store-Level Intelligence**: Accounting for store location, catchment income, and category affinity.
3. **Constrained Allocation**: Allocating stock to highest-value positions while respecting the ₹4 Crore budget cap.
4. **EOL Risk Detection**: Identifying aging models before they turn into dead stock.
5. **Action Matrix**: Comparing Transfer vs. Markdown vs. Hold options in rupees.
6. **Rolling Simulation**: Testing decisions week-by-week over a full 52-week year.
7. **Fair Benchmarking**: Comparing MobiMart against a traditional baseline strategy.
8. **Executive Dashboard**: Providing real-time visibility into capital, fill rate, and risk exposure.

---

## 💡 Our Solution — In Simple Words

MobiMart guides retail managers through an end-to-end operational workflow:

```
Customer Demand
      │
      ▼
Understand Store Profiles  ──►  (High Street vs. Mall vs. Tier-2)
      │
      ▼
Forecast Upcoming Demand   ──►  (Zero future-data leakage velocity blend)
      │
      ▼
Evaluate Financial Value   ──►  (Calculate Net Marginal Value in Rupees)
      │
      ▼
Enforce ₹4 Crore Cap       ──►  (Sort opportunities by NMV until budget is full)
      │
      ▼
Allocate Inventory         ──►  (Ship recommended quantities from warehouse)
      │
      ▼
Monitor EOL Risk           ──►  (Identify aging SKUs losing market traction)
      │
      ▼
Execute Best Disposition   ──►  (Transfer, Markdown, or Hold based on net rupee impact)
      │
      ▼
Simulate Rolling Weeks     ──►  (Observe Multi-week performance over time)
      │
      ▼
Benchmark vs. Baseline     ──►  (Prove revenue, stockout, and capital efficiency gains)
```

1. **Understand Store Profiles**: Analyzes each store's location, footfall, income index, and tier affinity (e.g. flagship vs. budget).
2. **Forecast Demand**: Calculates expected weekly demand using observed sales history without looking into the future.
3. **Calculate Financial Value**: Measures the Net Marginal Value ($NMV$) of sending one additional phone unit to a specific store.
4. **Enforce Capital Limit**: Ranks every possible store-product candidate by $NMV$ and commits inventory until the **₹4 Crore limit** is reached.
5. **Allocate Inventory**: Recommends exact unit quantities to ship from warehouse to store shelves.
6. **Monitor EOL Risk**: Automatically flags products reaching End-of-Life (EOL) or facing successor launch cannibalization.
7. **Choose EOL Action**: Compares **TRANSFER**, **MARKDOWN**, and **HOLD** options in rupees and picks the best outcome.
8. **Simulate & Benchmark**: Backtests the strategy over 52 weeks and proves its financial superiority against a traditional baseline.

---

## ⭐ What Makes MobiMart Stand Out

- **1. Not Just a Static Dashboard**: MobiMart doesn't just display inventory numbers; it actively recommends specific, actionable inventory decisions.
- **2. Hard ₹4 Crore Capital Constraint**: Treats working capital as a real, strict constraint rather than assuming unlimited inventory funds.
- **3. Financially Explainable Recommendations**: Every single allocation recommendation is backed by a rupee-denominated proof:
  $$\text{Net Marginal Value (NMV)} = \text{Expected Gross Margin} + \text{Avoided Goodwill Loss} - \text{Logistics Allocation Cost}$$
- **4. Store-Aware Intelligence**: Recognizes that stores are not identical. A flagship phone has high demand in a Bangalore Premium Mall but low demand in a Tier-3 regional hub.
- **5. Proactive EOL Risk Detection**: Identifies aging models weeks before successor phones launch, preventing capital from getting trapped in dead stock.
- **6. Multi-Action Financial Matrix**: Rather than blindly marking down old stock, MobiMart evaluates whether an inter-store **TRANSFER** to a high-demand store is more profitable than a **MARKDOWN**.
- **7. Deterministic & Reproducible**: Built on deterministic simulation loops so running the same scenario always yields the exact same benchmark result.
- **8. Honest Baseline Comparison**: Benchmarks MobiMart against a traditional Last-4-Week Proportional Allocation strategy under identical starting conditions.
- **9. Engineering Explainability**: Exposes clear reasoning narratives and math breakdowns for every recommendation instead of operating as a black box.
- **10. Production-Grade Architecture**: Built with a modular Python/FastAPI backend, custom domain engines, Pytest coverage (187 tests passing), and a polished React/TypeScript dashboard.

---

## 📈 How MobiMart Helps the Business

- **Better Inventory Placement**: Puts the right phones in the stores where customers are actively looking to buy them.
- **Fewer Stockouts**: Reduces lost sales by maintaining stock in high-velocity outlets (**Stockout Rate reduced from 67.5% to 52.8%**).
- **Higher Customer Fulfillment**: Boosts fill rate / service level (**Service Level increased from 45.1% to 58.7%**).
- **Increased Top-Line Revenue**: Generates **+31.3% higher revenue** (₹7.38 Cr vs ₹5.62 Cr) from the exact same starting capital.
- **Superior Capital Efficiency**: Increases capital turns from **1.49x to 1.81x**, turning inventory into sales faster.
- **Lower Dead Stock Exposure**: Reduces dead stock percentage from **99.9% down to 85.9%**.
- **Smarter EOL Recoveries**: Saves working capital through capacity-resolved inter-store transfers before resorting to heavy price markdowns.
- **Transparent Operations**: Gives retail executives audit-ready financial reasoning for every rupee allocated.

---

## 🎯 Mirai Labs Assignment B — Requirement Coverage

| # | Recruiter Requirement | Technical Implementation | Where to See It | Status |
| :--- | :--- | :--- | :--- | :---: |
| **1** | **12 Months Sales History** | 78,000 sales records across 52 weeks, 25 stores, ~60 SKUs | `data/generated/sales_history.csv` | **PASS** |
| **2** | **25 Store Profiles** | High Street, Premium Mall, Mass Market, Tier-2 & Tier-3 catchment profiles | Stores Network (`/stores`) | **PASS** |
| **3** | **~60 Phone SKUs** | Budget, Mid-Range, Premium, Flagship tiers with launch dates | Products Page (`/products`) | **PASS** |
| **4** | **Product Lifecycle Intelligence** | Launch → Growth → Peak → Decline → EOL stage tracking | Products & EOL Center | **PASS** |
| **5** | **₹4 Crore Capital Constraint** | Hard chain-wide cap enforcing inventory cost accounting identity | Allocation Page & Overview (`/`) | **PASS** |
| **6** | **Stockout Economics** | Avoided goodwill loss factors ($5\text{--}15\%$) by price segment | Allocation Engine (`financials.py`) | **PASS** |
| **7** | **Inter-Store Transfers** | Capacity-resolved zero-overcommit inter-store transfer ledgers | EOL Risk Center (`/eol`) | **PASS** |
| **8** | **EOL Risk Engine** | Risk scoring ($0\text{--}100$) & Markdown vs Transfer vs Hold decision matrix | EOL Risk Center (`/eol`) | **PASS** |
| **9** | **Weekly Constrained Allocation** | Marginal Net Value ($NMV$) greedy sorting under warehouse bounds | Allocation Planner (`/allocation`) | **PASS** |
| **10**| **Financial Explanations** | Rupee-denominated financial proof breakdown per recommendation | Allocation Planner Drawer | **PASS** |
| **11**| **Owner Dashboard** | Real-time capital deployment, headroom, fill rate & 4-week telemetry | Overview Dashboard (`/`) | **PASS** |
| **12**| **Naive Baseline Comparison** | Controlled evaluation against Last-4-Week Proportional Allocation | Benchmark Page (`/benchmark`) | **PASS** |
| **13**| **Live Scenario Simulator** | Multi-week rolling simulation loop under zero future data leakage | Simulator Studio (`/simulation`) | **PASS** |
| **14**| **Deterministic Backtesting** | Process-scoped in-memory caching with `X-Benchmark-Cache` headers | Benchmark & FastAPI Router | **PASS** |

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

*Note: Benchmark results are generated dynamically by the backtest engine (`backend/engine/simulation/runner.py`) — zero hardcoded numbers.*

---

## 🎬 3-Minute Recruiter Walkthrough

> *If you only have three minutes to demonstrate MobiMart, use these five screens. The walkthrough tells a simple story: **Understand the Business $\rightarrow$ Make an Allocation Decision $\rightarrow$ Manage Risk $\rightarrow$ Prove the Strategy Works $\rightarrow$ Simulate What Happens Over Time.***

---

### 1️⃣ Start with the Executive Overview — *"What is happening in the business?"*

Open the **Executive Overview** (`/`). This dashboard provides an immediate 30-second snapshot of retail operations:

- **Capital Deployment Bar**: Shows how much of the **₹4 Crore limit** is currently committed (e.g. **₹3.79 Cr deployed, 94.8% utilization, ₹20.76 Lakhs headroom**).
- **Past 4-Week Telemetry**: Displays historical performance over the past month (**₹2.76 Cr Revenue, ₹55.09 L Gross Margin, 99.4% Fill Rate**).
- **Fill Rate (Service Level)**: Shows how effectively customer demand was met (**58.7%**).
- **Stockout Rate**: Shows how often stores ran out of requested stock (**52.8%**).
- **EOL Exposure**: Highlights inventory tied up in declining or End-of-Life models (**₹27.60 Lakhs across 10 alert positions**).

#### Why this screen matters:
It answers three core executive questions: *Where is the money right now? Are customers being served? Which inventory is at risk?*

> 🗣️ **What to say to the recruiter:**  
> *"We start at the Executive Overview, which gives retail leadership immediate visibility into our ₹4 Crore capital budget. We can see that ₹3.79 Crore is deployed with ₹20.76 Lakhs in headroom. Over the past 4 weeks, the network generated ₹2.76 Crore in revenue at a 99.4% fill rate, but we have ₹27.60 Lakhs exposed to End-of-Life risk that requires action."*

---

### 2️⃣ Open the Allocation Planner — *"Where should inventory go?"*

Navigate to the **Allocation Planner** (`/allocation`) and click **Run Allocation**:

- **Recommended Quantities**: Recommends exact unit quantities to send to specific store-SKU positions.
- **Store & SKU Search Filters**: Easily filter recommendations by store ID or phone model name.
- **Financial Proof Drawer**: Click on any recommendation row to expand the full financial calculation.
- **Net Marginal Value ($NMV$)**: Explains why the recommendation was selected over thousands of alternatives:
  $$\text{NMV} = \text{Margin Contribution (₹18,500)} + \text{Avoided Goodwill (₹2,775)} - \text{Logistics (₹250)} = \text{₹21,025/unit}$$

#### Why this screen matters:
Instead of distributing stock equally or guessing, the engine calculates the exact rupee gain of every candidate unit and respects the ₹4 Crore budget cap.

> 🗣️ **What to say to the recruiter:**  
> *"Next is the Allocation Planner. Every week, the engine ranks thousands of potential store-product allocations by Net Marginal Value, or NMV. If we expand any row, MobiMart shows the exact financial proof — balancing margin contribution and avoided stockout loss against logistics cost under our ₹4 Crore cap."*

---

### 3️⃣ Open the EOL Risk Center — *"What happens to aging inventory?"*

Navigate to the **EOL Risk Center** (`/eol`):

- **EOL Concept**: As smartphones age or successor models launch, older stock loses value rapidly.
- **Risk Score ($0\text{--}100$)**: Flags products reaching critical risk levels based on weeks of cover and successor launch proximity.
- **3-Option Disposition Matrix**: For every risky position, MobiMart evaluates three choices:
  - **TRANSFER**: Move stock to a higher-demand store (e.g. transfer 15 units from Mysuru to Bangalore).
  - **MARKDOWN**: Discount price to accelerate local clearance sales.
  - **HOLD**: Keep stock in place if immediate action isn't financially justified.
- **Capacity Ledger**: Ensures inter-store transfer routes never overcommit source store stock or exceed destination store storage limits.

#### Why this stands out:
MobiMart doesn't just flag old inventory; it compares multiple recovery actions in rupees and checks if a store transfer is physically possible.

> 🗣️ **What to say to the recruiter:**  
> *"Here in the EOL Risk Center, MobiMart protects capital from dying in slow-moving SKUs. For every at-risk product, the engine compares Transfer, Markdown, and Hold options in rupees. In this case, it approved an inter-store transfer route that saves ₹45,000 compared to holding the stock, while enforcing store capacity constraints."*

---

### 4️⃣ Open the Benchmark Scorecard — *"Can we prove MobiMart is better?"*

Navigate to the **Benchmark Scorecard** (`/benchmark`) and select **Weeks 1 to 12 (Q1)**:

- **Controlled Fair Comparison**: Strategy A (Naive Proportional Baseline) vs. Strategy B (MobiMart Engine) starting with the **exact same inventory snapshot** and facing the **exact same customer demand**.
- **Verified Results**:
  - **Revenue**: Increased by **+31.3%** (from ₹5.62 Cr to **₹7.38 Cr** — an extra **+₹1.76 Crore**).
  - **Stockout Rate**: Decreased by **-21.9%** (from 67.5% down to **52.8%**).
  - **Service Level (Fill Rate)**: Improved by **+30.1%** (from 45.1% to **58.7%**).
  - **Capital Turns**: Increased by **+21.5%** (from 1.49x to **1.81x**).
- **Instant Cache Response**: Click **Rerun Benchmark** to demonstrate process-scoped caching returning results in **< 4 milliseconds** (`X-Benchmark-Cache: HIT`).

#### Why this stands out:
Instead of simply claiming the algorithm works, MobiMart runs both strategies through a zero-future-leakage simulation loop and proves performance on an honest scorecard.

> 🗣️ **What to say to the recruiter:**  
> *"On the Benchmark page, we prove our performance. We run MobiMart against a traditional last-month proportional baseline under identical starting inventory and demand. Over 12 weeks, MobiMart generated ₹7.38 Crore in revenue compared to ₹5.62 Crore for the baseline — a +31.3% revenue gain — while reducing stockout rates from 67.5% to 52.8%."*

---

### 5️⃣ Finish with the Decision Simulator — *"What happens over time?"*

Navigate to the **Decision Simulator** (`/simulation`):

- **Horizon Presets**: Run multi-week rolling simulations for **Q1 (W1–12)**, **H1 (W1–24)**, or **Full Year (W1–52)**.
- **Weekly Trace Ledger**: Inspect week-by-week store cost, allocation additions, customer demand, fulfilled units, and weekly gross margin.
- **Rolling Execution**: Demonstrates how decisions made in Week 1 dynamically shape store stock levels and headroom in Week 2, Week 3, and beyond.

#### Why this matters:
Inventory management is not a single decision; it is a multi-week chain reaction. The simulator proves that MobiMart maintains financial health over an entire 52-week year.

> 🗣️ **What to say to the recruiter:**  
> *"Finally, the Decision Simulator lets us stress-test the inventory network over 12, 24, or 52 weeks. We can trace every single week's allocations, fulfillments, and margins in the trace ledger, verifying zero future-data leakage across the entire rolling horizon."*

---

## 🧠 The Story Behind the Demo

The entire platform follows five simple principles:

```
  UNDERSTAND  ──►  See current capital deployment and stock risk across 25 stores.
      │
    DECIDE    ──►  Allocate inventory to highest Net Marginal Value opportunities under ₹4 Cr limit.
      │
  MANAGE RISK ──►  Proactively transfer, markdown, or hold aging EOL inventory.
      │
    PROVE     ──►  Compare outcomes against a naive baseline under controlled conditions.
      │
   SIMULATE   ──►  Observe multi-week rolling impact across a full 52-week year.
```

---

## 🗣️ 20-Second Final Pitch

> *"MobiMart is an inventory decision-support platform built for a 25-store mobile retail chain operating under a hard ₹4 Crore capital budget limit. Instead of using simple spreadsheets or gut feeling, MobiMart combines demand forecasting, store catchment profiling, and EOL risk management to calculate the exact rupee value of every allocation recommendation. Over a 12-week controlled simulation, MobiMart increased revenue by +31.3% — generating an extra ₹1.76 Crore — while cutting stockouts by 21.9% compared to a traditional baseline. The system is built with FastAPI, React, TypeScript, and a deterministic simulation engine backed by 187 automated tests."*

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

## ⚡ Performance & Caching

- **Overview Page Load**: **~1.08 seconds** (lightweight parallel API calls).
- **First Benchmark Execution (MISS)**: **~4.37 seconds** (runs complete 12-week rolling backtest for both strategies).
- **Repeated Benchmark Execution (HIT)**: **< 4 milliseconds** (process-scoped in-memory cache hit).
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

### 1. Install Backend Dependencies & Launch Server:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI server from workspace root
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
├── requirements.txt             # Python Package Specification
└── README.md                    # Technical Project Documentation
```

---

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend**: Python 3.14, FastAPI, Pydantic v2, Uvicorn
- **Data & Analytics**: Pandas, NumPy
- **Testing & Tooling**: Pytest, TestClient
