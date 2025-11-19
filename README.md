# Dr. Database 🩺🗃️  
_A multi-agent AI “data doctor” for your SQL warehouse_

Dr. Database is a LangChain + LangGraph powered tool that connects to your data warehouse in **read-only** mode, runs automated data quality checks, and uses LLM agents to:

- detect anomalies,
- hypothesize root causes,
- suggest SQL/dbt-style fixes, and
- generate human-readable reports.

Think of it as a **data engineering SRE**: it does not replace your dashboards or ETL, it keeps them healthy.

---

## ✨ Key Features (Planned)

- 🔍 **Automated Data Quality Checks**
  - Row count anomalies (sudden drops/spikes)
  - Freshness delays (stale tables)
  - Null rate spikes
  - Basic schema drift detection

- 🧠 **Multi-Agent Reasoning (LangGraph)**
  - **Detector Agent** – filters real issues from noise and assigns severity
  - **Hypothesis Agent** – suggests likely root causes
  - **Fix Agent** – proposes diagnostic SQL and dbt tests (read-only suggestions)
  - **Reporter Agent** – produces structured Markdown/HTML reports

- 🧱 **Warehouse-Aware**
  - Connects to your Postgres (initially) or other SQL warehouses
  - Uses real metadata and simple statistics, not just guesses

- 🖥️ **Simple Web UI**
  - Configure warehouse connection
  - Run Dr. Database on demand
  - View historical reports
  - Download reports as Markdown/HTML (and JSON via API)

- 🧩 **Extensible**
  - Swap LLM providers (Gemini now, OpenAI/local later)
  - Add more DQ rules
  - Future: dbt integration, Slack alerts, CI hooks, etc.

---

## ⚠️ Safety & Read-Only Guarantees

Dr. Database is designed to be **safe to run against your data warehouse**.

### Read-Only by Default

- Dr. Database connects to your warehouse using standard SQL drivers.
- It only issues **SELECT** queries to:
  - Inspect table schemas
  - Calculate row counts and null ratios
  - Check basic freshness (e.g., max timestamp)
- It does **not** run `INSERT`, `UPDATE`, `DELETE`, `ALTER`, or `DROP`.

### No Automatic Fix Execution

The Fix Agent may generate:

- Diagnostic SQL queries
- Suggested UPDATE/INSERT/ALTER statements
- Suggested dbt test YAML snippets

However:

- These are returned **as suggestions only**.
- Dr. Database **does not execute** any suggested SQL against your warehouse.
- All remediation steps must be manually reviewed and applied by a human.

Each suggested fix includes a disclaimer similar to:

> This SQL is a suggested fix and has not been executed.  
> Please review and test in a safe environment before using.

### Internal vs Warehouse Databases

- Dr. Database stores its own metadata and reports in a separate **internal database** (e.g., a Postgres instance or SQLite file).
- Only this internal database is mutated by the application.
- Your warehouse under diagnosis is treated as **read-only**.

### Recommended Best Practices

- Start by pointing Dr. Database at a **non-production** or staging environment.
- Review all generated SQL in your own editor/IDE.
- Use your existing code review and change management process around any fixes.

---

## 🏗️ High-Level Architecture

At a high level, one run of Dr. Database looks like this:

```text
[Browser UI]
    ↓  (Run Check)
[FastAPI Backend] → [Warehouse Client] → [Metadata Extractor] → [DQ Rules Engine]
                                              ↓
                                        [DQ Signals]
                                              ↓
                                  [LangGraph Multi-Agent Flow]
        Detector → Hypothesis → Fix → Reporter
                                              ↓
                               [Report stored in internal DB]
                                              ↓
              UI (view report) / API (JSON, Markdown, HTML)
