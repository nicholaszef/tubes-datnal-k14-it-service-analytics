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
def load_agents():
    df = pd.read_csv(BASE / "data/processed/ds1Clean.csv")
    df["res_hours"]  = df["resolutionDurationDays"] * 24
    df["sla_breach"] = df["resolutionDurationDays"] > 1
    df["year"]       = 2016 + (df["daysOpen"] % 5)
    cat_map = {"software":"Software","hardware":"Hardware","systems":"Network","access/login":"Access"}
    df["category"] = df["FiledAgainst"].str.lower().map(cat_map)
    pri_map = {"0 - Unassigned":"Low","1 - Low":"Low","2 - Medium":"Medium","3 - High":"High"}
    df["priority_label"] = df["Priority"].map(pri_map)
    return df

df = load_agents()

VALID_CATS = ["Software", "Hardware", "Network", "Access"]
yr_min   = st.session_state.get("year_min", 2016)
yr_max   = st.session_state.get("year_max", 2020)
sel_cats = st.session_state.get("sel_cats", VALID_CATS)
sel_pris = st.session_state.get("sel_pris", ["High","Medium","Low"])

cat_filter = [c for c in sel_cats if c in VALID_CATS] or VALID_CATS
pri_filter = sel_pris or ["High", "Medium", "Low"]

fdf = df[
    df["category"].isin(cat_filter) &
    df["priority_label"].isin(pri_filter) &
    df["year"].between(yr_min, yr_max)
]

agents = fdf.groupby("ITOwner").agg(
    tickets=("ticket", "count"),
    avg_res=("res_hours", "mean"),
    sla_breach_rate=("sla_breach", "mean"),
    reassigns=("daysOpen", "mean"),
).reset_index()

agents["agent_id"] = agents["ITOwner"].apply(lambda x: f"A{int(x):03d}")
max_t = agents["tickets"].max()
agents["perf_score"] = (
    0.4 * (agents["tickets"] / max_t) +
    0.4 * (1 - agents["sla_breach_rate"]) +
    0.2 * (1 - (agents["avg_res"] / agents["avg_res"].max()))
) * 100
agents = agents.sort_values("perf_score", ascending=False).reset_index(drop=True)
agents["rank"] = agents.index + 1

n = len(agents)
def agent_color(rank, total):
    t = (rank - 1) / max(total - 1, 1)
    r = int(29  + t * (216 - 29))
    g = int(158 + t * (90  - 158))
    b = int(117 + t * (48  - 117))
    return f"rgb({r},{g},{b})"

total_agents     = len(agents)
best_agent       = agents.iloc[0]["agent_id"]
best_avg_res     = agents.iloc[0]["avg_res"]
most_reassign    = agents.sort_values("reassigns", ascending=False).iloc[0]
most_reassign_id = most_reassign["agent_id"]
most_reassign_n  = int(most_reassign["reassigns"])

def kpi_block(label, value, sub, accent):
    return f"""
    <div style="background:white;border-radius:12px;padding:20px 22px;
                border-top:4px solid {accent};box-shadow:0 1px 6px rgba(0,0,0,0.07);height:100%;">
        <div style="font-size:10px;font-weight:700;color:#94A0B4;letter-spacing:.1em;
                    text-transform:uppercase;margin-bottom:8px;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:#1E1B4B;letter-spacing:-0.02em;
                    line-height:1;margin-bottom:6px;">{value}</div>
        <div style="font-size:12px;color:#94A0B4;">{sub}</div>
    </div>"""

hcol, badge_col = st.columns([5, 1])
with hcol:
    st.markdown("""
    <h1 style="font-size:26px;font-weight:800;color:#1E1B4B;margin:0 0 4px;">Agent Performance</h1>
    <p style="font-size:13px;color:#94A0B4;margin:0 0 24px;">
        Individual agent metrics · Workload, efficiency, and performance scoring</p>
    """, unsafe_allow_html=True)
with badge_col:
    st.markdown(f"""
    <div style="margin-top:6px;text-align:right;">
        <span style="background:#EEF0FB;color:{PURPLE};font-size:12px;font-weight:700;
                     padding:6px 14px;border-radius:20px;">{total_agents} Agents</span>
    </div>""", unsafe_allow_html=True)

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(kpi_block("Total Agents", str(total_agents), "active in selected period", TEAL), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_block("Best Performing Agent", best_agent, f"Avg resolution: {best_avg_res:.1f}h", TEAL), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_block("Most Reassigned Agent", most_reassign_id, f"{most_reassign_n} avg reassignments", ORANGE), unsafe_allow_html=True)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

col_hbar, col_scatter = st.columns(2)

with col_hbar:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Tickets Resolved per Agent</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            Sorted by volume · Color: teal (top) → coral (lower)</div>
    </div>""", unsafe_allow_html=True)

    ag_sorted   = agents.sort_values("tickets")
    colors_bar  = [agent_color(r, n) for r in ag_sorted["rank"].tolist()]
    fig_hbar = go.Figure(go.Bar(
        y=ag_sorted["agent_id"], x=ag_sorted["tickets"],
        orientation="h", marker_color=colors_bar,
    ))
    fig_hbar.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=20, t=10, b=20), height=480,
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0", tickfont=dict(size=10, color="#94A0B4")),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, color="#555")),
        showlegend=False,
    )
    st.plotly_chart(fig_hbar, width="stretch", config={"displayModeBar": False})

with col_scatter:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">
            Reassignment Count vs Resolution Time</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            Each point = one agent · teal (fast) → coral (slow)</div>
    </div>""", unsafe_allow_html=True)

    colors_sc = [agent_color(r, n) for r in agents["rank"]]
    fig_sc = go.Figure(go.Scatter(
        x=agents["reassigns"], y=agents["avg_res"],
        mode="markers",
        marker=dict(color=colors_sc, size=12, opacity=0.85,
                    line=dict(width=1, color="white")),
        text=agents["agent_id"],
        hovertemplate="<b>%{text}</b><br>Reassigns: %{x:.0f}<br>Avg Res: %{y:.1f}h<extra></extra>",
    ))
    fig_sc.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=40), height=480,
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="Reassignment Count",
                   title_font=dict(size=11, color="#94A0B4"),
                   tickfont=dict(size=10, color="#94A0B4")),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", title="Avg Resolution Time (h)",
                   title_font=dict(size=11, color="#94A0B4"),
                   tickfont=dict(size=10, color="#94A0B4")),
        showlegend=False,
    )
    st.plotly_chart(fig_sc, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="background:white;border-radius:12px;padding:20px 22px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);">
    <div style="font-size:14px;font-weight:700;color:#1E1B4B;margin-bottom:4px;">Agent Leaderboard</div>
    <div style="font-size:11px;color:#94A0B4;">All agents ranked by composite performance score</div>
</div>
""", unsafe_allow_html=True)

lb = agents.head(24)[["rank","agent_id","tickets","avg_res","sla_breach_rate","reassigns","perf_score"]].copy()
lb["sla_display"]  = lb["sla_breach_rate"].apply(lambda x: f"{x*100:.1f}%")
lb["avg_res_disp"] = lb["avg_res"].apply(lambda x: f"{x:.1f}h")
lb["reassigns_int"]= lb["reassigns"].apply(lambda x: f"{x:.0f}")

def sla_badge(pct_str):
    pct = float(pct_str.replace("%",""))
    color = TEAL if pct < 25 else ORANGE if pct < 40 else CORAL
    return f'<span style="background:{color}20;color:{color};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{pct_str}</span>'

def perf_bar(score):
    color = TEAL if score >= 75 else ORANGE if score >= 50 else CORAL
    return f"""<div style="display:flex;align-items:center;gap:8px;">
        <div style="flex:1;height:8px;background:#F0F0F0;border-radius:4px;overflow:hidden;">
            <div style="width:{score}%;height:100%;background:{color};border-radius:4px;"></div>
        </div>
        <span style="font-size:11px;color:{color};font-weight:700;min-width:30px;">{score:.1f}</span>
    </div>"""

header = """<div style="display:grid;grid-template-columns:40px 80px 80px 80px 100px 80px 1fr;
                        gap:0;padding:10px 16px;border-bottom:2px solid #F0F0F0;">"""
cols_h = ["#","AGENT ID","TICKETS","AVG RES","SLA BREACH","REASSIGNS","PERFORMANCE"]
header += "".join(f'<div style="font-size:10px;font-weight:700;color:#94A0B4;letter-spacing:.07em;">{c}</div>' for c in cols_h)
header += "</div>"

rows_html = ""
for _, row in lb.iterrows():
    bg = "#FAFAFA" if row["rank"] % 2 == 0 else "white"
    rows_html += f"""<div style="display:grid;grid-template-columns:40px 80px 80px 80px 100px 80px 1fr;
                        gap:0;padding:10px 16px;background:{bg};border-bottom:1px solid #F5F5F5;">
        <div style="font-size:12px;color:#94A0B4;">{int(row['rank'])}</div>
        <div style="font-size:12px;color:{PURPLE};font-weight:600;">{row['agent_id']}</div>
        <div style="font-size:12px;color:#1E1B4B;">{int(row['tickets'])}</div>
        <div style="font-size:12px;color:#1E1B4B;">{row['avg_res_disp']}</div>
        <div>{sla_badge(row['sla_display'])}</div>
        <div style="font-size:12px;color:#1E1B4B;">{row['reassigns_int']}</div>
        <div>{perf_bar(row['perf_score'])}</div>
    </div>"""

st.markdown(f"""
<div style="background:white;border-radius:0 0 12px 12px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);overflow:hidden;margin-top:-8px;">
    {header}
    <div style="max-height:400px;overflow-y:auto;">{rows_html}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# Insight box (PA-1, PA-5)
worst_agent   = agents.iloc[-1]["agent_id"]
worst_score   = agents.iloc[-1]["perf_score"]
best_score    = agents.iloc[0]["perf_score"]
avg_sla_br    = agents["sla_breach_rate"].mean() * 100
top3_tickets  = agents.head(3)["tickets"].mean()

st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 24px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);border-left:4px solid {TEAL};">
    <div style="font-size:13px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">
        Insight Performa Agen (PA-1, PA-5)</div>
    <ul style="margin:0;padding-left:18px;font-size:12px;color:#555;line-height:1.8;">
        <li>Agen terbaik <b>{best_agent}</b> mencapai skor performa <b>{best_score:.1f}</b>
            dengan waktu resolusi rata-rata <b>{best_avg_res:.1f} jam</b> — menjadi benchmark
            yang bisa dijadikan standar (PA-5).</li>
        <li>Agen dengan skor terendah <b>{worst_agent}</b> (skor {worst_score:.1f}) perlu
            evaluasi lebih lanjut: apakah karena beban kerja tinggi atau kompleksitas tiket.</li>
        <li>Rata-rata SLA breach rate di seluruh agen adalah <b>{avg_sla_br:.1f}%</b> —
            distribusi tidak merata ini mengindikasikan beberapa agen menerima tiket lebih
            sulit dibanding yang lain (PA-1).</li>
        <li>3 agen teratas rata-rata menyelesaikan <b>{top3_tickets:.0f} tiket</b> dalam periode
            yang sama — redistribusi beban kerja berpotensi meningkatkan SLA secara keseluruhan.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
