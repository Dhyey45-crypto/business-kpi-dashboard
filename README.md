# 📊 KPI Dashboard — Streamlit + Plotly + TextBlob
### 🔗 [Launch the Live App](https://business-kpi-dashboard-9urqxcanzfjufpe4cnpz98.streamlit.app/)

An interactive business KPI dashboard with Revenue, Profit, and Customer
Growth KPIs, monthly trend charts, interactive filters, and customer
feedback sentiment analysis powered by TextBlob.

---

## 📁 Project Structure

```
kpi_dashboard/
├── app.py                 # Main Streamlit application
├── generate_data.py        # (Optional) script to regenerate sample data
├── requirements.txt         # Python dependencies
├── data/
│   └── sales_data.csv       # Pre-generated sample dataset (1500 orders)
└── README.md                 # This file
```

---

## ✅ Features

- **Revenue KPI** — total revenue with % change vs. previous period
- **Profit KPI** — total profit and profit margin
- **Customer Growth KPI** — unique customer count and growth %
- **Monthly Trends** — Revenue/Profit line chart, customer growth bar chart, orders trend
- **Interactive Filters** — date range, region, category, product (sidebar)
- **Plotly Charts** — line, bar, pie, and treemap visualizations
- **Sentiment Analysis** — TextBlob-based polarity scoring of customer feedback (Positive/Neutral/Negative)
- **Data Export** — download the filtered dataset as CSV directly from the app

---

## 🛠️ Setup Instructions (VS Code)

### 1. Prerequisites
- Python 3.9+ installed
- VS Code installed
- (Recommended) VS Code Python extension installed

### 2. Get the project
Unzip the downloaded project folder, then open it in VS Code:

```bash
cd kpi_dashboard
code .
```

### 3. Create a virtual environment (recommended)

Open a terminal inside VS Code (`` Ctrl+` `` or `View > Terminal`):

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `streamlit`, `pandas`, `plotly`, `textblob`, `numpy`.

> **Note (first time only):** TextBlob may ask you to download NLTK corpora.
> If you see a related warning, run:
> ```bash
> python -m textblob.download_corpora
> ```

### 5. (Optional) Regenerate sample data

A ready-to-use dataset already exists at `data/sales_data.csv`. If you want
fresh random data instead, run:

```bash
python generate_data.py
```

### 6. Run the dashboard

```bash
streamlit run app.py
```

### 7. View in browser

Streamlit will automatically open your default browser. If it doesn't,
manually navigate to the URL shown in the terminal, typically:

```
Local URL: http://localhost:8501
Network URL: http://<your-ip>:8501
```

---

## 🧪 Quick Test Checklist

- [ ] Sidebar filters (date range, region, category, product) update all charts
- [ ] KPI cards at the top show Revenue, Profit, Customer Growth, Avg Order Value
- [ ] "Monthly Trends" tabs show Revenue & Profit, Customer Growth, Orders
- [ ] Region bar chart, Category pie chart, and Category→Product treemap render
- [ ] Sentiment pie chart and sentiment trend chart render
- [ ] "View sample feedback with sentiment scores" expander shows data
- [ ] "View filtered raw data" expander + CSV download button work

---

## 🩹 Troubleshooting

| Issue | Fix |
|---|---|
| `streamlit: command not found` | Ensure your virtual environment is activated, then re-run `pip install -r requirements.txt` |
| Port 8501 already in use | Run `streamlit run app.py --server.port 8502` |
| TextBlob corpora warning | Run `python -m textblob.download_corpora` |
| Blank charts / "No data matches filters" | Widen the date range or select more regions/categories in the sidebar |
| `data/sales_data.csv` not found | Run `python generate_data.py` to regenerate it |

---

## 🔧 Customizing with Your Own Data

Replace `data/sales_data.csv` with your own file, keeping these columns
(rename in `app.py` if your schema differs):

| Column | Type | Description |
|---|---|---|
| `order_id` | string | Unique order identifier |
| `order_date` | date (YYYY-MM-DD) | Order date |
| `customer_id` | string | Unique customer identifier |
| `region` | string | Sales region |
| `category` | string | Product category |
| `product` | string | Product name |
| `quantity` | int | Units sold |
| `unit_price` | float | Price per unit |
| `revenue` | float | quantity × unit_price |
| `cost` | float | Cost of goods sold |
| `profit` | float | revenue − cost |
| `customer_feedback` | string | Free-text customer feedback (used for sentiment analysis) |

---

## 📦 Tech Stack

- [Streamlit](https://streamlit.io/) — web app framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [TextBlob](https://textblob.readthedocs.io/) — sentiment analysis
- [Pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — data processing
