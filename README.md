# 🛒 E-commerce Sales Analysis — Online Retail II

## Overview
End-to-end sales analysis of a UK-based online retail store using the real **Online Retail II** dataset (UCI / Kaggle) — over 1 million transactions across 2 years, 38 countries, and 4,000+ products.

## Dataset
| Property | Value |
|---|---|
| Source | [Kaggle — Online Retail II UCI](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci) |
| Records | ~1,000,000 transactions (2009–2011) |
| Countries | 38 |
| License | CC BY 4.0 |

> **Note:** The script auto-generates a synthetic dataset if the real file isn't present. Place `online_retail_II.xlsx` in the project folder to use real data.

## Key Findings
- **£3.3M+ total revenue** across the analysis period
- **Peak sales** concentrated Thursday–Sunday, 10am–3pm
- **Top 15 products** drive a disproportionate share of revenue — strong Pareto effect
- **RFM Segmentation:** 27% of customers classified as "Champions" generating 46% of total revenue
- **1,035 "At Risk" customers** with £290K in historical spend — prime re-engagement targets

## Techniques Used
| Technique | Description |
|---|---|
| Data Cleaning | Removed cancellations, nulls, negative quantities |
| Revenue Analysis | Monthly trends, country breakdown, top products |
| RFM Segmentation | Recency / Frequency / Monetary scoring (quartile-based) |
| Sales Heatmap | Day-of-week × hour-of-day revenue patterns |

## Tools
`Python` · `matplotlib` · `seaborn` · `openpyxl`·`pandas` · `numpy`

## How to Run
```bash
pip install pandas numpy matplotlib seaborn openpyxl
python ecommerce_analysis.py
```

## Output Files
```
charts/
├── 01_monthly_revenue.png      ← Revenue & orders trend
├── 02_top_products.png         ← Top 15 products by revenue
├── 03_revenue_by_country.png   ← Geographic revenue breakdown
├── 04_rfm_segments.png         ← RFM customer segmentation
└── 05_sales_heatmap.png        ← Sales by day × hour
rfm_segments.csv                ← Full RFM scores per customer
```

## Business Recommendations
1. **Re-engage At Risk customers** — 1,035 customers with proven spend history, likely to convert with a targeted offer
2. **Time promotions** around Thursday–Sunday peak windows for maximum visibility
3. **Inventory priority** on top 15 products — they carry disproportionate revenue weight

---
*Project by Alejandro Pardo — Data Analyst | [LinkedIn](https://linkedin.com/in/alejandro-pardo03a)*
