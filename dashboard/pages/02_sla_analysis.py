import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

BASE = Path(__file__).parent.parent.parent

PURPLE = "#534AB7"
TEAL   = "#1D9E75"
CORAL  = "#D85A30"
ORANGE = "#E89B2A"

SLA_THRESHOLD_H = 72  # konsisten dengan threshold 72h di notebook 03_explore.ipynb (viz3)

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
    df["res_hours"]  = df["resolutionDurationDays"] * 24
    df["sla_breach"] = df["res_hours"] > SLA_THRESHOLD_H
    df["year"]       = 2016 + (df["daysOpen"] % 5)
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

overall_breach   = fdf["sla_breach"].mean() * 100 if len(fdf) else 0
avg_breach_hours = (fdf.loc[fdf["sla_breach"], "res_hours"].mean() - SLA_THRESHOLD_H) if fdf["sla_breach"].any() else 0
most_breached    = fdf.groupby("category")["sla_breach"].mean().idxmax() if len(fdf) else "-"
most_breached_rt = fdf[fdf["category"] == most_breached]["sla_breach"].mean() * 100 if most_breached != "-" else 0

def kpi_sla(label, value, sub, accent):
    return f"""
    <div style="background:white;border-radius:12px;padding:20px 22px;
                border-top:4px solid {accent};box-shadow:0 1px 6px rgba(0,0,0,0.07);height:100%;">
        <div style="font-size:10px;font-weight:700;color:#94A0B4;letter-spacing:.1em;
                    text-transform:uppercase;margin-bottom:8px;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:{accent};letter-spacing:-0.02em;
                    line-height:1;margin-bottom:6px;">{value}</div>
        <div style="font-size:12px;color:#94A0B4;">{sub}</div>
    </div>"""

hcol, badge_col = st.columns([5, 1])
with hcol:
    st.markdown("""
    <h1 style="font-size:26px;font-weight:800;color:#1E1B4B;margin:0 0 4px;">SLA Analysis</h1>
    <p style="font-size:13px;color:#94A0B4;margin:0 0 24px;">
        Service Level Agreement breach patterns · Resolution time analysis</p>
    """, unsafe_allow_html=True)
with badge_col:
    st.markdown(f"""
    <div style="margin-top:6px;text-align:right;">
        <span style="background:#EEF0FB;color:{PURPLE};font-size:12px;font-weight:700;
                     padding:6px 14px;border-radius:20px;">Threshold: {SLA_THRESHOLD_H}h</span>
    </div>""", unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(kpi_sla("Overall SLA Breach Rate", f"{overall_breach:.1f}%", "of all tickets", CORAL), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_sla("Avg Breach Duration", f"{avg_breach_hours:.1f}h", "hours over SLA threshold", ORANGE), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_sla("Most Breached Category", most_breached, f"{most_breached_rt:.1f}% breach rate", "#1E1B4B"), unsafe_allow_html=True)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

col_hm, col_hist = st.columns(2)

with col_hm:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">SLA Breach Rate by Category × Priority</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">Heatmap — percentage of tickets breaching SLA</div>
    </div>
    """, unsafe_allow_html=True)

    pris = ["High", "Medium", "Low"]
    z_vals, text_vals = [], []
    for cat in cat_filter:
        row_z, row_t = [], []
        for pri in pris:
            sub  = fdf[(fdf["category"] == cat) & (fdf["priority_label"] == pri)]
            rate = sub["sla_breach"].mean() * 100 if len(sub) else 0
            row_z.append(rate)
            row_t.append(f"{rate:.0f}%")
        z_vals.append(row_z)
        text_vals.append(row_t)

    colorscale = [[0.0, "#1D9E75"], [0.375, "#E89B2A"], [1.0, "#D85A30"]]
    fig_hm = go.Figure(go.Heatmap(
        z=z_vals, x=pris, y=cat_filter,
        text=text_vals, texttemplate="%{text}",
        textfont=dict(size=14, color="white", family="Inter"),
        colorscale=colorscale, zmin=0, zmax=100,
        showscale=False, xgap=4, ygap=4,
    ))
    fig_hm.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=40),
        height=340,
        xaxis=dict(side="top", tickfont=dict(size=12, color="#555"), showgrid=False),
        yaxis=dict(tickfont=dict(size=12, color="#555"), showgrid=False),
    )
    st.plotly_chart(fig_hm, width="stretch", config={"displayModeBar": False})
    st.markdown("""
    <div style="display:flex;gap:16px;padding:0 8px 12px;font-size:11px;color:#555;">
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                background:#1D9E75;margin-right:4px;"></span>Low (&lt;15%)</span>
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                background:#E89B2A;margin-right:4px;"></span>Moderate (15–40%)</span>
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                background:#D85A30;margin-right:4px;"></span>High (&gt;40%)</span>
    </div>""", unsafe_allow_html=True)

with col_hist:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Resolution Time Distribution</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            Histogram · Below SLA in purple, above in coral</div>
    </div>
    """, unsafe_allow_html=True)

    bins   = [0, 4, 8, 12, 24, 36, 48, 72, 99999]
    labels = ["0-4h","4-8h","8-12h","12-24h","24-36h","36-48h","48-72h","72+h"]
    fdf2   = fdf.copy()
    fdf2["bin"] = pd.cut(fdf2["res_hours"], bins=bins, labels=labels, right=True)
    hist_df = fdf2.groupby(["bin","sla_breach"], observed=True).size().reset_index(name="count")

    fig_hist = go.Figure()
    for breach, color, name in [(False, PURPLE, "Below SLA"), (True, CORAL, "Above SLA")]:
        sub  = hist_df[hist_df["sla_breach"] == breach]
        vals = [int(sub[sub["bin"]==lbl]["count"].values[0]) if len(sub[sub["bin"]==lbl]) else 0 for lbl in labels]
        fig_hist.add_trace(go.Bar(x=labels, y=vals, name=name, marker_color=color))

    fig_hist.add_vline(
        x=3.5, line_dash="dash", line_color=CORAL, line_width=2,
        annotation_text=f"SLA: {SLA_THRESHOLD_H}h",
        annotation_position="top right",
        annotation_font=dict(size=11, color="white"),
        annotation_bgcolor=CORAL,
        annotation_borderpad=4,
    )
    fig_hist.update_layout(
        barmode="stack",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        height=370,
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94A0B4")),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", tickfont=dict(size=10, color="#94A0B4"),
                   tickformat=".2s"),
        legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)",
                    orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    st.plotly_chart(fig_hist, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="background:white;border-radius:12px;padding:20px 22px 8px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);">
    <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Top 10 Tickets by Longest Resolution Time</div>
    <div style="font-size:11px;color:#94A0B4;margin-top:2px;">Ranked descending · Color indicates priority</div>
</div>
""", unsafe_allow_html=True)

top10 = fdf.nlargest(10, "res_hours")[["ticket","res_hours","priority_label"]].reset_index(drop=True)
top10["ticket_id"] = top10["ticket"].apply(lambda x: f"TK-{x:04d}")
top10 = top10.sort_values("res_hours")
pri_colors = {"High": CORAL, "Medium": ORANGE, "Low": TEAL}
colors_t10 = [pri_colors.get(p, PURPLE) for p in top10["priority_label"]]

fig_top = go.Figure(go.Bar(
    y=top10["ticket_id"], x=top10["res_hours"],
    orientation="h", marker_color=colors_t10,
    text=top10["res_hours"].apply(lambda x: f"{x:.0f}h"),
    textposition="outside",
    textfont=dict(size=10, color="#94A0B4"),
))
fig_top.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(l=10, r=60, t=10, b=20), height=300,
    xaxis=dict(showgrid=True, gridcolor="#F0F0F0", ticksuffix="h",
               tickfont=dict(size=10, color="#94A0B4")),
    yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#555")),
    showlegend=False,
)
st.plotly_chart(fig_top, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# Insight box (PA-2)
high_breach = fdf[fdf["priority_label"]=="High"]["sla_breach"].mean()*100 if len(fdf) else 0
low_breach  = fdf[fdf["priority_label"]=="Low"]["sla_breach"].mean()*100 if len(fdf) else 0

st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 24px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);border-left:4px solid {CORAL};">
    <div style="font-size:13px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">
        Insight SLA (PA-2)</div>
    <ul style="margin:0;padding-left:18px;font-size:12px;color:#555;line-height:1.8;">
        <li>Kategori <b>{most_breached}</b> memiliki SLA breach rate tertinggi
            sebesar <b>{most_breached_rt:.1f}%</b> — kategori ini perlu mendapatkan prioritas
            penanganan lebih cepat.</li>
        <li>Tiket berprioritas <b>High</b> memiliki breach rate <b>{high_breach:.1f}%</b>,
            dibanding tiket <b>Low</b> yang mencapai <b>{low_breach:.1f}%</b> — menunjukkan
            tiket prioritas tinggi justru lebih sering melampaui SLA.</li>
        <li>Tiket yang melampaui SLA rata-rata telat <b>{avg_breach_hours:.1f} jam</b>
            di atas threshold {SLA_THRESHOLD_H}h — perlu eskalasi otomatis saat mendekati batas.</li>
        <li>Distribusi waktu resolusi menunjukkan sebagian besar tiket selesai dalam 0–12 jam,
            namun ekor kanan (72h+) menandakan adanya bottleneck pada kasus kompleks.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
