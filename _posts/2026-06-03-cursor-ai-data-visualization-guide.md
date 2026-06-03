---
layout: post
title: "Cursor AI for Data Visualization: A Complete Hands-On Guide"
subtitle: "From environment setup to interactive charts — master the full AI-assisted Python data visualization workflow"
banner: "/assets/images/banners/cursor-data-viz.jpg"
author: zane.deng
categories: [AI Coding]
tags: [Cursor, Data Analysis, AI, Python, Data Visualization]
---

## Why Use Cursor AI for Data Visualization?

Data visualization is the final mile of data analysis — and the most insightful part. The traditional Jupyter Notebook + matplotlib workflow requires developers to memorize numerous APIs. With AI assistance, this compresses into a simple loop: **describe your needs → generate code → debug and run**.

Cursor AI's Composer and Tab features offer solid support for Python's scientific computing stack. Combined with Anaconda or uv environment management, you can accelerate the entire workflow.

## 1. Environment Setup

We'll use a standard Python scientific computing environment. I recommend using **uv** to manage dependencies (10x faster than pip):

```bash
uv venv data-viz-env --python 3.11
source data-viz-env/bin/activate
uv add pandas matplotlib plotly requests jupyterlab
```

I also recommend installing JupyterLab and running `jupyter lab` for a panel-based chart viewing experience.

## 2. Fetching Data: Using Python to Request Public APIs

Let's use World Bank GDP data as an example to demonstrate the complete data fetching workflow:

```python
import requests
import pandas as pd

def fetch_wb_gdp(country_code="CN", start_year=2010, end_year=2023):
    """
    Fetch World Bank GDP data for a specified country (current USD).
    API docs: https://databank.worldbank.org/reports.aspx?source=2
    """
    indicator = "NY.GDP.MKTP.CD"
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 100
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    
    data = resp.json()
    if len(data) < 2 or not data[1]:
        raise ValueError(f"No data returned for country code: {country_code}")
    
    records = [
        {"year": int(item["date"]), "gdp_usd": float(item["value"])}
        for item in data[1]
        if item["value"] is not None
    ]
    df = pd.DataFrame(records).sort_values("year")
    return df

# Test: Fetch China's GDP data
df_gdp = fetch_wb_gdp("CN")
print(df_gdp.head())
print(f"Data range: {df_gdp['year'].min()} - {df_gdp['year'].max()}")
```

## 3. Hands-On Analysis with Cursor AI

In Cursor Composer, enter a natural language prompt:

> "Generate Python code to plot China's GDP trend as a line chart using matplotlib, with dual Y-axes showing GDP absolute value and year-over-year growth rate. Add the chart title 'China GDP Trend (2010-2023)' and display in Chinese."

The code Cursor generates is typically pre-wired to the `df_gdp` DataFrame we fetched earlier — just make minor adjustments and run:

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False

df_gdp["gdp_trillion"] = df_gdp["gdp_usd"] / 1e12
df_gdp["yoy_rate"] = df_gdp["gdp_trillion"].pct_change() * 100

fig, ax1 = plt.subplots(figsize=(10, 6))

# Left axis: GDP in trillions
color1 = "#1f77b4"
ax1.set_xlabel("Year")
ax1.set_ylabel("GDP (Trillion USD)", color=color1)
ax1.plot(df_gdp["year"], df_gdp["gdp_trillion"], 
         color=color1, linewidth=2, marker="o", label="GDP (Trillion USD)")
ax1.tick_params(axis="y", labelcolor=color1)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

# Right axis: YoY growth rate
ax2 = ax1.twinx()
color2 = "#ff7f0e"
ax2.set_ylabel("YoY Growth Rate (%)", color=color2)
ax2.bar(df_gdp["year"], df_gdp["yoy_rate"], 
        color=color2, alpha=0.4, width=0.6, label="YoY Growth Rate")
ax2.tick_params(axis="y", labelcolor=color2)

plt.title("China GDP Trend (2010-2023)", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.savefig("cn_gdp_trend.png", dpi=150)
plt.show()
```

## 4. Advanced: Interactive Charts with Plotly

Static charts are great for reports; interactive charts are better for sharing. Switching from matplotlib to Plotly only requires changing a few lines:

```python
import plotly.express as px
import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_gdp["year"], y=df_gdp["gdp_trillion"],
    mode="lines+markers",
    name="GDP (Trillion USD)",
    line=dict(color="#1f77b4", width=2)
))

fig.add_trace(go.Bar(
    x=df_gdp["year"], y=df_gdp["yoy_rate"],
    name="YoY Growth Rate (%)",
    marker_color="#ff7f0e",
    opacity=0.5,
    yaxis="y2"
))

fig.update_layout(
    title=dict(text="China GDP Trend (2010-2023)", font=dict(size=16)),
    xaxis=dict(title="Year"),
    yaxis=dict(title="GDP (Trillion USD)", side="left"),
    yaxis2=dict(title="YoY Growth Rate (%)", side="right", overlaying="y"),
    template="plotly_white",
    hovermode="x unified"
)

fig.write_html("cn_gdp_interactive.html")  # Opens directly in browser
fig.show()
```

The HTML file generated by Plotly can be embedded anywhere and maintains full interactivity — hover to inspect exact values.

## 5. Data Visualization Best Practices

- **Choose the right chart type**: Use line charts for trends, histograms for distributions, scatter plots for correlations, and grouped bar charts for comparisons.
- **Reduce visual noise**: Remove unnecessary gridlines and legends. Cleaner charts communicate more efficiently.
- **Annotate key points**: Add text comments at anomalous data points or important inflection points.
- **Consistent color scheme**: Use the same brand color palette throughout your report to maintain professionalism.
- **AI-assisted debugging**: When encountering rendering issues (like Chinese character garbling or axis overlap), feed the error message back to Cursor for quick corrections.

## Conclusion

The core value of Cursor AI in data visualization isn't replacing analytical thinking — it's minimizing friction in the "from idea to chart" process. Data fetching, cleaning, visualization, and report generation — the entire pipeline can now be completed efficiently in the Cursor environment.

My recommendation: start with a small dataset, run through the full workflow, then migrate to your actual business data.
