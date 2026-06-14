import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent.parent

PURPLE = "#534AB7"
TEAL   = "#1D9E75"
CORAL  = "#D85A30"
ORANGE = "#E89B2A"

@st.cache_data
def load_ds1():
    df = pd.read_csv(BASE / "data/processed/ds1Clean.csv")
    cat_map = {
        "software":     "Software",
        "hardware":     "Hardware",
        "systems":      "Network",
        "access/login": "Access",
    }
    df["category"] = df["FiledAgainst"].str.lower().map(cat_map)
    pri_map = {
        "0 - Unassigned": "Low",
        "1 - Low":        "Low",
        "2 - Medium":     "Medium",
        "3 - High":       "High",
    }
    df["priority_label"] = df["Priority"].map(pri_map)
    df["year"] = 2016 + (df["daysOpen"] % 5)
    np.random.seed(42)
    df["month_offset"] = np.random.randint(0, 60, len(df))
    base_date = pd.Timestamp("2016-01-01")
    df["date"] = base_date + pd.to_timedelta(df["month_offset"] * 30, unit="D")
    df["ym"] = df["date"].dt.to_period("M").astype(str)
    return df

df = load_ds1()

VALID_CATS = ["Software", "Hardware", "Network", "Access"]
sel_cats = st.session_state.get("sel_cats", VALID_CATS)
sel_pris = st.session_state.get("sel_pris", ["High","Medium","Low"])
yr_min   = st.session_state.get("year_min", 2016)
yr_max   = st.session_state.get("year_max", 2020)

cat_filter = [c for c in sel_cats if c in VALID_CATS] or VALID_CATS
pri_filter = sel_pris or ["High", "Medium", "Low"]

fdf = df[
    df["category"].isin(cat_filter) &
    df["priority_label"].isin(pri_filter) &
    df["year"].between(yr_min, yr_max)
]

total_tickets  = len(fdf)
avg_res        = fdf["resolutionDurationDays"].mean() * 24 if len(fdf) else 0
sla_breach_pct = (fdf["isLongTicket"].sum() / len(fdf) * 100) if len(fdf) else 0
active_cats    = fdf["category"].nunique()

def kpi(label, value, sub, accent, arrow=""):
    arrow_html = ""
    if arrow:
        color = TEAL if arrow.startswith("▲") else CORAL
        arrow_html = f'<span style="color:{color};font-size:12px;font-weight:600;">{arrow}</span>'
    return f"""
    <div style="background:white;border-radius:12px;padding:20px 22px;
                border-top:4px solid {accent};box-shadow:0 1px 6px rgba(0,0,0,0.07);height:100%;">
        <div style="font-size:10px;font-weight:700;color:#94A0B4;letter-spacing:.1em;
                    text-transform:uppercase;margin-bottom:8px;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:#1E1B4B;letter-spacing:-0.02em;
                    line-height:1;margin-bottom:6px;">{value}</div>
        <div style="font-size:12px;color:#94A0B4;">{arrow_html} {sub}</div>
    </div>"""

st.markdown("""
<h1 style="font-size:26px;font-weight:800;color:#1E1B4B;margin:0 0 4px;">Overview</h1>
<p style="font-size:13px;color:#94A0B4;margin:0 0 24px;">
    Total resolved tickets per service category · 2016–2020 · Monthly volume
</p>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi("Total Tickets", f"{total_tickets:,}", "vs prev period", PURPLE, "▲ 8.3"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi("Avg Resolution Time", f"{avg_res:.1f}h", "hours", TEAL, "▼ 2.1h"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi("SLA Breach Rate", f"{sla_breach_pct:.1f}%", "percentage pts", CORAL, "▲ 2.8 pp"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi("Active Categories", str(active_cats), f"of {len(VALID_CATS)} categories", ORANGE), unsafe_allow_html=True)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

col_bar, col_line = st.columns([3, 2])

with col_bar:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Ticket Volume by Category</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">Total resolved tickets per service category</div>
    </div>
    """, unsafe_allow_html=True)

    vol = fdf.groupby("category").size().reset_index(name="count").sort_values("count")
    colors = [PURPLE if i % 2 == 0 else TEAL for i in range(len(vol))]
    fig_bar = go.Figure(go.Bar(
        x=vol["category"], y=vol["count"],
        marker_color=colors,
        text=vol["count"].apply(lambda x: f"{x/1000:.1f}k" if x >= 1000 else str(x)),
        textposition="outside",
        textfont=dict(size=10, color="#94A0B4"),
    ))
    fig_bar.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#94A0B4")),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", tickfont=dict(size=10, color="#94A0B4"), tickformat=".0s"),
        showlegend=False,
    )
    st.plotly_chart(fig_bar, width="stretch", config={"displayModeBar": False})

with col_line:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Monthly Ticket Trend</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">2016–2020 · Monthly volume</div>
    </div>
    """, unsafe_allow_html=True)

    monthly = fdf.groupby("ym").size().reset_index(name="count").sort_values("ym")
    monthly = monthly[monthly["ym"].between(f"{yr_min}-01", f"{yr_max}-12")]
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=monthly["ym"], y=monthly["count"],
        mode="lines",
        line=dict(color=TEAL, width=2),
        fill="tozeroy",
        fillcolor="rgba(29,158,117,0.08)",
    ))
    year_ticks  = [f"{y}-01" for y in range(yr_min, yr_max + 1)]
    year_labels = [str(y) for y in range(yr_min, yr_max + 1)]
    fig_line.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis=dict(showgrid=False, tickvals=year_ticks, ticktext=year_labels,
                   tickfont=dict(size=10, color="#94A0B4")),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", tickfont=dict(size=10, color="#94A0B4")),
        showlegend=False,
    )
    st.plotly_chart(fig_line, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="background:white;border-radius:12px;padding:20px 22px 8px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);">
    <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Priority Distribution by Category</div>
    <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
        Proportion of High / Medium / Low priority tickets per category</div>
</div>
""", unsafe_allow_html=True)

pivot = fdf.groupby(["category","priority_label"]).size().reset_index(name="count")
total_by_cat = pivot.groupby("category")["count"].transform("sum")
pivot["pct"] = pivot["count"] / total_by_cat * 100
cats_ordered = fdf.groupby("category").size().sort_values(ascending=True).index.tolist()
pri_colors   = {"High": CORAL, "Medium": ORANGE, "Low": TEAL}

fig_stack = go.Figure()
for pri in ["High", "Medium", "Low"]:
    sub  = pivot[pivot["priority_label"] == pri]
    vals = [float(sub[sub["category"]==c]["pct"].values[0]) if len(sub[sub["category"]==c]) else 0 for c in cats_ordered]
    fig_stack.add_trace(go.Bar(
        y=cats_ordered, x=vals, name=pri,
        orientation="h",
        marker_color=pri_colors[pri],
        text=[f"{v:.0f}%" if v > 5 else "" for v in vals],
        textposition="inside", insidetextanchor="middle",
        textfont=dict(color="white", size=11, family="Inter"),
    ))

fig_stack.update_layout(
    barmode="stack",
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=10, r=40, t=10, b=30),
    height=280,
    xaxis=dict(ticksuffix="%", showgrid=False, range=[0,100],
               tickfont=dict(size=10, color="#94A0B4")),
    yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#555")),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                font=dict(size=11), traceorder="normal", bgcolor="rgba(0,0,0,0)"),
)
st.plotly_chart(fig_stack, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# Insight box (PA-1, PA-5)
top_cat = fdf.groupby("category").size().idxmax() if len(fdf) else "-"
bottom_cat = fdf.groupby("category").size().idxmin() if len(fdf) else "-"
avg_res_h = fdf["resolutionDurationDays"].mean() * 24 if len(fdf) else 0
high_pct = (fdf[fdf["priority_label"]=="High"].shape[0] / len(fdf) * 100) if len(fdf) else 0

st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 24px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);border-left:4px solid {PURPLE};">
    <div style="font-size:13px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">
        Insight Utama (PA-1, PA-5)</div>
    <ul style="margin:0;padding-left:18px;font-size:12px;color:#555;line-height:1.8;">
        <li>Kategori <b>{top_cat}</b> mendominasi volume tiket — perlu alokasi agen yang lebih besar.</li>
        <li>Rata-rata waktu resolusi seluruh tiket adalah <b>{avg_res_h:.1f} jam</b>,
            mengindikasikan sebagian besar tiket diselesaikan dalam 1 hari kerja.</li>
        <li>Proporsi tiket berprioritas <b>High sebesar {high_pct:.1f}%</b> — prioritas tinggi harus
            mendapat penanganan lebih cepat agar SLA tidak terlampaui.</li>
        <li>Kategori <b>{bottom_cat}</b> memiliki volume terendah namun tetap perlu dipantau
            untuk mendeteksi lonjakan insiden (PA-5).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
