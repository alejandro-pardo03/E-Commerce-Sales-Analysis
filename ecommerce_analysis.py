"""
=======================================================
 PROJECT A — E-commerce Sales Analysis
 Dataset: Online Retail II (UCI / Kaggle)
 Tools: Python (pandas, numpy, matplotlib, seaborn)
 Author: Alejandro Pardo
=======================================================

DATASET DOWNLOAD:
    https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci
    File: online_retail_II.xlsx (or .csv)

OUTPUT:
    charts/01_monthly_revenue.png
    charts/02_top_products.png
    charts/03_revenue_by_country.png
    charts/04_rfm_segments.png
    charts/05_sales_heatmap.png
    rfm_segments.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

os.makedirs("charts", exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted")
np.random.seed(42)

print("=" * 60)
print("  E-commerce Sales Analysis — Online Retail II")
print("=" * 60)

# 1. LOAD DATA
def load_real_data():
    for fname in ["online_retail_II.xlsx", "online_retail_II.csv",
                  "Online Retail.xlsx", "data/online_retail_II.xlsx"]:
        try:
            if fname.endswith(".xlsx"):
                df = pd.read_excel(fname, sheet_name="Year 2009-2010")
                df2 = pd.read_excel(fname, sheet_name="Year 2010-2011")
                return pd.concat([df, df2], ignore_index=True)
            else:
                return pd.read_csv(fname, encoding="latin1")
        except:
            continue
    return None

def generate_synthetic_data():
    """Realistic synthetic e-commerce dataset mirroring Online Retail II structure."""
    print("  → Using synthetic dataset (place real Kaggle file in folder to use real data)")

    products = {
        "WHITE HANGING HEART T-LIGHT HOLDER": 2.95,
        "REGENCY CAKESTAND 3 TIER": 12.75,
        "JUMBO BAG RED RETROSPOT": 1.65,
        "PARTY BUNTING": 4.95,
        "LUNCH BAG RED RETROSPOT": 1.65,
        "ASSORTED COLOUR BIRD ORNAMENT": 1.69,
        "PACK OF 72 RETROSPOT CAKE CASES": 0.55,
        "PINK CHERRY LIGHTS": 6.75,
        "KNITTED UNION FLAG HOT WATER BOTTLE": 3.39,
        "HAND WARMER UNION JACK": 1.85,
        "GLASS STAR FROSTED T-LIGHT HOLDER": 1.25,
        "VINTAGE BILLBOARD DRINK ME MUG": 1.25,
        "SET OF 3 CAKE TINS PANTRY DESIGN": 4.95,
        "NATURAL SLATE HEART CHALKBOARD": 2.10,
        "MINI PAINT SET VINTAGE": 0.65,
        "WOODEN FRAME ANTIQUE WHITE": 2.46,
        "PAPER CHAIN KIT VINTAGE CHRISTMAS": 2.95,
        "WOODEN HEART CHRISTMAS SCANDINAVIAN": 1.25,
        "RED WOOLLY HOTTIE WHITE HEART": 3.39,
        "SET OF 4 PANTRY JELLY MOULDS": 1.25,
    }

    countries = {
        "United Kingdom": 0.82, "Germany": 0.05, "France": 0.04,
        "EIRE": 0.03, "Netherlands": 0.02, "Australia": 0.01,
        "Spain": 0.01, "Belgium": 0.01, "Switzerland": 0.005, "Other": 0.005,
    }

    rows = []
    invoice_num = 536365
    customer_ids = list(range(12346, 18300))
    dates = pd.date_range("2009-12-01", "2011-12-09", freq="h")
    dates = dates[dates.hour.isin(range(8, 20))]  # business hours only

    for _ in range(25000):
        date = np.random.choice(dates)
        country = np.random.choice(list(countries.keys()), p=list(countries.values()))
        n_items = np.random.randint(1, 8)
        invoice = f"C{invoice_num}" if np.random.random() < 0.02 else str(invoice_num)
        customer = np.random.choice(customer_ids) if np.random.random() < 0.90 else np.nan
        invoice_num += 1

        for _ in range(n_items):
            product = np.random.choice(list(products.keys()))
            price = products[product] * np.random.uniform(0.95, 1.05)
            qty = np.random.randint(1, 25) if not invoice.startswith("C") else -np.random.randint(1, 10)
            rows.append({
                "Invoice": invoice,
                "StockCode": str(np.random.randint(10000, 99999)),
                "Description": product,
                "Quantity": qty,
                "InvoiceDate": date,
                "Price": round(price, 2),
                "Customer ID": customer,
                "Country": country,
            })

    return pd.DataFrame(rows)

df_raw = load_real_data()
if df_raw is None:
    df_raw = generate_synthetic_data()

print(f"\n  Raw dataset: {len(df_raw):,} rows loaded")

# 2. CLEAN DATA
df = df_raw.copy()

# Standardize column names
df.columns = [c.strip().replace(" ", "_") for c in df.columns]
if "Customer_ID" not in df.columns and "CustomerID" in df.columns:
    df.rename(columns={"CustomerID": "Customer_ID"}, inplace=True)

# Remove cancelled orders (Invoice starts with C)
cancelled = df["Invoice"].astype(str).str.startswith("C")
print(f"  Cancelled orders removed: {cancelled.sum():,}")
df = df[~cancelled]

# Remove rows without Customer ID (can't do RFM without it)
df = df.dropna(subset=["Customer_ID"])
df["Customer_ID"] = df["Customer_ID"].astype(int)

# Remove negative quantities and zero prices
df = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

# Create revenue column
df["Revenue"] = df["Quantity"] * df["Price"]

# Parse dates
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")
df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
df["Hour"] = df["InvoiceDate"].dt.hour

print(f"  Clean dataset: {len(df):,} rows | {df['Customer_ID'].nunique():,} customers")
print(f"  Date range: {df['InvoiceDate'].min().date()} → {df['InvoiceDate'].max().date()}")
print(f"  Total revenue: £{df['Revenue'].sum():,.2f}")
print(f"  Countries: {df['Country'].nunique()}")

# 3. MONTHLY REVENUE TREND
monthly = df.groupby("YearMonth").agg(
    revenue=("Revenue", "sum"),
    orders=("Invoice", "nunique"),
    customers=("Customer_ID", "nunique")
).reset_index()
monthly["YearMonth_dt"] = monthly["YearMonth"].dt.to_timestamp()
monthly["avg_order_value"] = monthly["revenue"] / monthly["orders"]

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

axes[0].plot(monthly["YearMonth_dt"], monthly["revenue"],
             color="#2E86C1", linewidth=2.5, marker="o", markersize=4)
axes[0].fill_between(monthly["YearMonth_dt"], monthly["revenue"], alpha=0.1, color="#2E86C1")
axes[0].set_title("Monthly Revenue", fontweight="bold", fontsize=12)
axes[0].set_ylabel("Revenue (£)")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))

axes[1].bar(monthly["YearMonth_dt"], monthly["orders"],
            color="#1ABC9C", width=20, alpha=0.8)
axes[1].set_title("Monthly Orders", fontweight="bold", fontsize=12)
axes[1].set_ylabel("Number of Orders")
axes[1].tick_params(axis="x", rotation=45, labelsize=8)

plt.suptitle("E-commerce Revenue & Orders — 2009–2011", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("charts/01_monthly_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n  ✓ charts/01_monthly_revenue.png")

# 4. TOP PRODUCTS 
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(top_products["Description"][::-1],
               top_products["Revenue"][::-1],
               color="#2E86C1", edgecolor="white")
ax.set_xlabel("Total Revenue (£)")
ax.set_title("Top 15 Products by Revenue", fontsize=13, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))

for bar, val in zip(bars, top_products["Revenue"][::-1]):
    ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
            f"£{val:,.0f}", va="center", fontsize=8)

plt.tight_layout()
plt.savefig("charts/02_top_products.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ charts/02_top_products.png")

# 5. REVENUE BY COUNTRY
country_rev = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#1A5276" if c == "United Kingdom" else "#2E86C1"
          for c in country_rev["Country"]]
bars = ax.bar(country_rev["Country"], country_rev["Revenue"],
              color=colors, edgecolor="white")
ax.set_title("Revenue by Country (Top 10)", fontsize=13, fontweight="bold")
ax.set_ylabel("Total Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
ax.tick_params(axis="x", rotation=35, labelsize=9)

for bar, val in zip(bars, country_rev["Revenue"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
            f"£{val/1000:.0f}k", ha="center", fontsize=8)

plt.tight_layout()
plt.savefig("charts/03_revenue_by_country.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ charts/03_revenue_by_country.png")

# 6. RFM ANALYSIS 
# Recency, Frequency, Monetary — gold standard customer segmentation

snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Customer_ID").agg(
    Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
    Frequency=("Invoice", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()

# Score each dimension 1–4 (4 = best)
rfm["R_Score"] = pd.qcut(rfm["Recency"],   q=4, labels=[4, 3, 2, 1]).astype(int)
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
rfm["M_Score"] = pd.qcut(rfm["Monetary"],  q=4, labels=[1, 2, 3, 4]).astype(int)
rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

def rfm_segment(score):
    if score >= 10: return "Champions"
    elif score >= 8: return "Loyal Customers"
    elif score >= 6: return "Potential Loyalists"
    elif score >= 4: return "At Risk"
    else: return "Lost"

rfm["Segment"] = rfm["RFM_Score"].apply(rfm_segment)

seg_summary = rfm.groupby("Segment").agg(
    Customers=("Customer_ID", "count"),
    Avg_Recency=("Recency", "mean"),
    Avg_Frequency=("Frequency", "mean"),
    Avg_Monetary=("Monetary", "mean"),
    Total_Revenue=("Monetary", "sum")
).round(1).reset_index()

print("\n  RFM Segments:")
print(seg_summary.to_string(index=False))

seg_colors = {
    "Champions": "#1A5276",
    "Loyal Customers": "#2E86C1",
    "Potential Loyalists": "#1ABC9C",
    "At Risk": "#E67E22",
    "Lost": "#E74C3C",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart: customer count
colors_pie = [seg_colors[s] for s in seg_summary["Segment"]]
ax1.pie(seg_summary["Customers"], labels=seg_summary["Segment"],
        colors=colors_pie, autopct="%1.1f%%", startangle=140,
        textprops={"fontsize": 9})
ax1.set_title("Customer Distribution by RFM Segment", fontweight="bold")

# Bar chart: revenue contribution
bars = ax2.bar(seg_summary["Segment"], seg_summary["Total_Revenue"],
               color=colors_pie, edgecolor="white")
ax2.set_title("Revenue by RFM Segment", fontweight="bold")
ax2.set_ylabel("Total Revenue (£)")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x/1000:.0f}k"))
ax2.tick_params(axis="x", rotation=20, labelsize=9)
for bar, val in zip(bars, seg_summary["Total_Revenue"]):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
             f"£{val/1000:.0f}k", ha="center", fontsize=8)

plt.suptitle("RFM Customer Segmentation", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("charts/04_rfm_segments.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ charts/04_rfm_segments.png")

rfm.to_csv("rfm_segments.csv", index=False)
print("  ✓ rfm_segments.csv")

# 7. SALES HEATMAP (Day × Hour)
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data = df.groupby(["DayOfWeek", "Hour"])["Revenue"].sum().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(day_order)

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(heatmap_data, ax=ax, cmap="YlOrRd", fmt=".0f",
            linewidths=0.3, cbar_kws={"label": "Revenue (£)"})
ax.set_title("Sales Heatmap — Day of Week × Hour of Day",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")
plt.tight_layout()
plt.savefig("charts/05_sales_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  ✓ charts/05_sales_heatmap.png")

# 8. SUMMARY
champions = rfm[rfm["Segment"] == "Champions"]
at_risk = rfm[rfm["Segment"] == "At Risk"]
peak_month = monthly.loc[monthly["revenue"].idxmax(), "YearMonth"]

print()
print("=" * 60)
print("  KEY FINDINGS")
print("=" * 60)
print(f"  Total revenue          : £{df['Revenue'].sum():,.2f}")
print(f"  Total orders           : {df['Invoice'].nunique():,}")
print(f"  Unique customers       : {df['Customer_ID'].nunique():,}")
print(f"  Avg order value        : £{df.groupby('Invoice')['Revenue'].sum().mean():,.2f}")
print(f"  Peak month             : {peak_month}")
print(f"  Top country            : {country_rev.iloc[0]['Country']}")
print()
print(f"  RFM — Champions        : {len(champions):,} customers "
      f"(£{champions['Monetary'].sum():,.0f} revenue)")
print(f"  RFM — At Risk          : {len(at_risk):,} customers "
      f"(£{at_risk['Monetary'].sum():,.0f} revenue)")
print()
print("  Business recommendations:")
print("    → Target 'At Risk' customers with re-engagement campaigns")
print("    → Focus on Thursday–Sunday peak hours for promotions")
print("    → Top 15 products drive disproportionate revenue — prioritize stock")
print("=" * 60)
