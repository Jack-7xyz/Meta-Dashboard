import requests
from datetime import datetime
import dash
from dash import dcc, html
from dash.dash_table import DataTable
from dash.dependencies import Input, Output
import locale

# Set locale for number formatting (commas)
locale.setlocale(locale.LC_ALL, '')

# Configuration
COD_PERCENTAGE = 0.2  # 20%
API_URL = "http://127.0.0.1:5001/api/insights"

# Fetch rolling 30-day data from API
def fetch_insights():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

# Load raw API data
raw_data = fetch_insights()

# Prepare per-row data and compute Contribution Margin values
rows = []
for item in raw_data:
    date = item["date_start"]
    spend = float(item.get("spend", 0.0))
    raw_roas = item.get("purchase_roas", 0.0)
    roas = float(raw_roas[0]["value"]) if isinstance(raw_roas, list) and raw_roas else float(raw_roas)
    revenue = spend * roas
    impressions = int(item.get("impressions", 0))

    # Extract link_clicks for CTR
    link_clicks = 0
    for action in item.get("actions", []):
        if action.get("action_type") == "link_click":
            link_clicks = int(action.get("value", 0))

    cpm = (spend / impressions * 1000) if impressions else 0
    ctr = (link_clicks / impressions * 100) if impressions else 0
    cm = (revenue * (1 - COD_PERCENTAGE)) - spend

    rows.append({
        "Date": date,
        "Spend": spend,
        "ROAS": roas,
        "Revenue": revenue,
        "Impressions": impressions,
        "CPM": cpm,
        "Clicks": link_clicks,
        "CTR (%)": ctr,
        "Contribution Margin": cm
    })

# Month dropdown options
months = sorted({r["Date"][:7] for r in rows})

# Dash app setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Meta Ads Performance Dashboard", style={"textAlign": "center", "fontFamily": "Calibri"}),
    html.H2("Select Month", style={"marginTop": "20px", "fontFamily": "Calibri"}),
    dcc.Dropdown(
        id='month-dropdown',
        options=[{'label': m, 'value': m} for m in months],
        value=months[-1] if months else None,
        clearable=False,
        style={"width": "200px", "fontFamily": "Calibri"}
    ),
    html.H2("Daily Metrics Table", style={"marginTop": "20px", "fontFamily": "Calibri"}),
    DataTable(
        id='metrics-table',
        columns=[
            {"name": c, "id": c, "type": "numeric", "format": {"specifier": ",.0f"}} if c in ["Spend","Revenue","Impressions","CPM","Clicks","Contribution Margin"] else
            {"name": c, "id": c, "type": "numeric", "format": {"specifier": ".2f"}} if c in ["ROAS","CTR (%)"] else
            {"name": c, "id": c}
            for c in ["Date","Spend","ROAS","Revenue","Impressions","CPM","Clicks","CTR (%)","Contribution Margin"]
        ],
        data=[],
        style_header={"backgroundColor": "#294761", "color": "white", "fontFamily": "Calibri"},
        style_data={"backgroundColor": "#EFEFEF", "fontFamily": "Calibri"},
        style_data_conditional=[{
            "if": {"filter_query": "{Date} = 'SUM'"},
            "backgroundColor": "#434343", "color": "white"
        }],
        page_action='none',
        sort_action='native',
        filter_action='native'
    ),
    html.H2("Daily Contribution Margin", style={"marginTop": "40px", "fontFamily": "Calibri"}),
    dcc.Graph(id='cm-chart', style={"backgroundColor": "#294761"}),
    html.H2("Spend ROAS Trend", style={"marginTop": "40px", "fontFamily": "Calibri"}),
    dcc.Graph(id='bar-chart', style={"backgroundColor": "#294761"})
], style={"padding": "20px"})

@app.callback(
    [Output('metrics-table', 'data'), Output('cm-chart', 'figure'), Output('bar-chart', 'figure')],
    [Input('month-dropdown', 'value')]
)
def update_dashboard(selected_month):
    # Filter rows for the month
    month_rows = [r for r in rows if r["Date"].startswith(selected_month)]

    # Aggregate metrics
    sum_spend = sum(r["Spend"] for r in month_rows)
    sum_revenue = sum(r["Revenue"] for r in month_rows)
    sum_impr = sum(r["Impressions"] for r in month_rows)
    sum_clicks = sum(r["Clicks"] for r in month_rows)
    avg_ctr = sum(r["CTR (%)"] for r in month_rows) / len(month_rows) if month_rows else 0
    sum_roas = sum_revenue / sum_spend if sum_spend else 0
    avg_cpm = sum_spend / sum_impr * 1000 if sum_impr else 0
    sum_cm = sum(r["Contribution Margin"] for r in month_rows)

    # SUM row
    sum_row = {
        "Date": "SUM",
        "Spend": f"${sum_spend:,.0f}",
        "ROAS": round(sum_roas,2),
        "Revenue": f"${sum_revenue:,.0f}",
        "Impressions": f"{sum_impr:,}",
        "CPM": f"${avg_cpm:,.0f}",
        "Clicks": f"{sum_clicks:,}",
        "CTR (%)": f"{avg_ctr:.2f}%",
        "Contribution Margin": f"${sum_cm:,.0f}"
    }

    # Format month rows
    formatted = []
    for r in month_rows:
        formatted.append({
            "Date": r["Date"],
            "Spend": f"${r['Spend']:,.0f}",
            "ROAS": round(r['ROAS'],2),
            "Revenue": f"${r['Revenue']:,.0f}",
            "Impressions": f"{r['Impressions']:,}",
            "CPM": f"${r['CPM']:,.0f}",
            "Clicks": f"{r['Clicks']:,}",
            "CTR (%)": f"{r['CTR (%)']:.2f}%",
            "Contribution Margin": f"${r['Contribution Margin']:,.0f}"
        })

    # Chart data
    dates = [r["Date"] for r in month_rows]
    cm_vals = [r["Contribution Margin"] for r in month_rows]
    cm_fig = {
        "data":[{"x":dates,"y":cm_vals,"type":"line","line":{"color":"#D8FF31"}}],
        "layout":{"plot_bgcolor":"#294761","paper_bgcolor":"#294761","font":{"family":"Calibri","color":"#ffffff"},"xaxis":{"title":"Date"},"yaxis":{"title":"Contribution Margin"}}
    }
    sorted_rows = sorted(month_rows, key=lambda x:x['Spend'])
    bar_x = [f"${r['Spend']:,.0f}" for r in sorted_rows]
    bar_y = [r['ROAS'] for r in sorted_rows]
    bar_text = [r['Date'] for r in sorted_rows]
    bar_fig = {
        "data":[{"x":bar_x,"y":bar_y,"type":"bar","marker":{"color":"#D8FF31"},"hovertext":bar_text,"hoverinfo":"text+x+y"}],
        "layout":{"plot_bgcolor":"#294761","paper_bgcolor":"#294761","font":{"family":"Calibri","color":"#ffffff"},"xaxis":{"title":"Spend ($)","type":"category"},"yaxis":{"title":"ROAS"}}
    }

    return [sum_row] + formatted, cm_fig, bar_fig

if __name__ == "__main__":
    app.run(debug=True)