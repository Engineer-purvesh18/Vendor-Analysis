# Vendor Performance Analysis

An end-to-end data analytics project for evaluating vendor and product performance across purchase, sales, and inventory data. The pipeline ingests raw CSV data into a SQLite database, builds an aggregated summary table, and delivers insights through exploratory analysis and statistical testing — with results visualized in a Power BI dashboard.

---

## Project Structure

```
├── data/                          # Raw CSV source files (not tracked)
├── logs/                          # Log files generated at runtime (not tracked)
├── ingestion_db.py                # Loads all CSVs from data/ into SQLite
├── get_vendor_summary.py          # Builds and cleans the vendor summary table
├── Exploratory Data Analysis.ipynb       # Database exploration & summary table design
├── Vendor Performance Analysis.ipynb     # Full analysis, visualizations & statistics
├── vendor_sales_summary.csv       # Final aggregated output table
├── vendor_performance.pbix        # Power BI dashboard
└── Vendor Performance Report.pdf  # Final report
```

---

## Workflow

### 1. Data Ingestion — `ingestion_db.py`
Reads all `.csv` files from the `data/` directory and loads each one as a table into `inventory.db` (SQLite), using the filename (without extension) as the table name. Logs progress to `logs/ingestion_db.log`.

**Source tables loaded:**
- `purchases` — line-level purchase transactions (vendor, brand, quantity, dollars, date)
- `purchase_prices` — product-level actual and purchase prices
- `vendor_invoice` — vendor-level invoice aggregates including freight cost
- `sales` — sales transactions (brand, quantity, revenue, excise tax)
- `begin_inventory` / `end_inventory` — year-start and year-end inventory snapshots (excluded from analysis)

### 2. Summary Table Creation — `get_vendor_summary.py`
Joins the ingested tables using a multi-CTE SQL query to produce a vendor-brand level summary. Applies data cleaning and engineers derived metrics, then writes the result back to the database as `vendor_sales_summary`.

**Engineered features:**
| Column | Description |
|---|---|
| `GrossProfit` | `TotalSalesDollars - TotalPurchaseDollars` |
| `ProfitMargin` | `(GrossProfit / TotalSalesDollars) × 100` |
| `StockTurnover` | `TotalSalesQuantity / TotalPurchaseQuantity` |
| `SalesToPurchaseRatio` | `TotalSalesDollars / TotalPurchaseDollars` |

**Cleaning steps:** fixes `Volume` dtype (object → float), fills nulls with `0`, strips whitespace from categorical columns.

---

## Analysis

### Exploratory Data Analysis (`Exploratory Data Analysis.ipynb`)
Initial exploration of the raw database tables to understand data distribution, identify relevant tables, and validate the design of the summary query before productionising it in `get_vendor_summary.py`.

### Vendor Performance Analysis (`Vendor Performance Analysis.ipynb`)
Full analytical notebook covering:

- **Summary statistics & distribution analysis** across all numeric columns
- **Outlier detection** via boxplots; filters out negative profit margins and zero-revenue records
- **Correlation analysis** — strong purchase-sales quantity correlation (0.999); weak price-to-profit relationship
- **Top vendors & brands by sales** — identifies highest revenue contributors
- **Vendor purchase concentration** — top 10 vendors account for ~65.7% of total procurement
- **Bulk purchasing impact** — large orders yield ~72% lower unit cost vs. small orders
- **Low inventory turnover** — flags vendors with `StockTurnover < 1` (excess/slow-moving stock)
- **Unsold inventory valuation** — estimates capital locked in unsold stock per vendor
- **Brands needing pricing/promotional action** — low-sales, high-margin products identified via percentile thresholds
- **Confidence intervals** — 95% CI for profit margins: top vendors (30.74%–31.61%) vs. low vendors (40.48%–42.62%)
- **Hypothesis testing** (t-test) — statistically significant difference in profit margins between top and low performers (p-value near zero)

---

## Output

| File | Description |
|---|---|
| `vendor_sales_summary.csv` | ~10,692 rows × 18 columns; final aggregated vendor-brand dataset |
| `vendor_performance.pbix` | Power BI dashboard for interactive exploration |
| `Vendor Performance Report.pdf` | Static summary report |

---

## Setup & Usage

### Prerequisites
```bash
pip install pandas sqlalchemy sqlite3
```

### Run the pipeline

**Step 1 — Place raw CSVs in the `data/` folder**, then ingest into the database:
```bash
python ingestion_db.py
```

**Step 2 — Build the vendor summary table:**
```bash
python get_vendor_summary.py
```

**Step 3 — Open the notebooks** in order for analysis:
1. `Exploratory Data Analysis.ipynb`
2. `Vendor Performance Analysis.ipynb`

> Logs are written to the `logs/` directory. Create this directory before running if it doesn't exist.

---

## Key Findings

- **Top 10 vendors drive 65.7% of total purchases**, creating significant supply chain concentration risk.
- **Bulk purchasing reduces unit cost by ~72%**, making order size a strong lever for margin improvement.
- **Low-performing vendors have higher profit margins** (40–43%) than top performers (30–32%), suggesting premium/niche positioning rather than volume competitiveness.
- **Statistically significant difference** in profit margins between vendor performance tiers (t-test, p ≈ 0).
- Several brands show **high margins but low sales volume**, making them candidates for targeted promotions or pricing adjustments.
