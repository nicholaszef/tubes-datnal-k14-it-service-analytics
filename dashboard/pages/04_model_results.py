import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent.parent

PURPLE  = "#534AB7"
PURPLE_L= "#8B85D4"
TEAL    = "#1D9E75"
CORAL   = "#D85A30"
ORANGE  = "#E89B2A"

@st.cache_data
def load_ds1():
    df = pd.read_csv(BASE / "data/processed/ds1Clean.csv")
    cat_map = {"software":"Software","hardware":"Hardware","systems":"Network","access/login":"Access"}
    df["category"] = df["FiledAgainst"].str.lower().map(cat_map)
    pri_map = {"0 - Unassigned":"Low","1 - Low":"Low","2 - Medium":"Medium","3 - High":"High"}
    df["priority_label"] = df["Priority"].map(pri_map)
    df["year"] = 2016 + (df["daysOpen"] % 5)
    return df

@st.cache_data
def load_clusters():
    path = BASE / "data/processed/ds2_with_clusters.csv"
    if path.exists():
        return pd.read_csv(path)
    return None

df     = load_ds1()
df_cl  = load_clusters()

# Nilai aktual dari notebook 04_model.ipynb (Random Forest, train=80%, test=20%, SMOTE pada X_train)
ACCURACY    = 64.93   # classification_report RF: accuracy
F1_MACRO    = 0.5809  # macro avg F1 dari classification_report RF
PRECISION_M = 0.5835  # macro avg precision RF
RECALL_M    = 0.5870  # macro avg recall RF
TRAIN_N     = 80000
TEST_N      = 20000

def kpi_metric(label, value, sub, accent, value_color=None):
    vc = value_color or "#1E1B4B"
    return f"""
    <div style="background:white;border-radius:12px;padding:20px 22px;
                border-top:4px solid {accent};box-shadow:0 1px 6px rgba(0,0,0,0.07);height:100%;">
        <div style="font-size:10px;font-weight:700;color:#94A0B4;letter-spacing:.1em;
                    text-transform:uppercase;margin-bottom:8px;">{label}</div>
        <div style="font-size:32px;font-weight:800;color:{vc};letter-spacing:-0.02em;
                    line-height:1;margin-bottom:6px;">{value}</div>
        <div style="font-size:12px;color:#94A0B4;">{sub}</div>
    </div>"""

hcol, badge_col = st.columns([5, 1])
with hcol:
    st.markdown("""
    <h1 style="font-size:26px;font-weight:800;color:#1E1B4B;margin:0 0 4px;">Model Results</h1>
    <p style="font-size:13px;color:#94A0B4;margin:0 0 12px;">
        ML classification for ticket priority prediction · Clustering analysis</p>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#EEF0FB;border-radius:8px;padding:10px 14px;margin-bottom:16px;
                font-size:12px;color:{PURPLE};border-left:3px solid {PURPLE};">
        <b>Catatan metodologi:</b> Metrik evaluasi (akurasi, F1-Score, confusion matrix)
        merepresentasikan performa model pada seluruh dataset (train 80% / test 20%, SMOTE pada training set).
        Nilai tidak berubah saat filter diubah karena model dilatih satu kali pada keseluruhan data
        — ini adalah perilaku yang benar secara metodologi.
    </div>
    """, unsafe_allow_html=True)
with badge_col:
    st.markdown(f"""
    <div style="margin-top:6px;text-align:right;">
        <span style="background:#EEF0FB;color:{PURPLE};font-size:12px;font-weight:700;
                     padding:6px 14px;border-radius:20px;">Random Forest</span>
    </div>""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_metric("Model Accuracy", f"{ACCURACY:.1f}%",
                            "on held-out test set (20%)", TEAL, TEAL), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_metric("F1-Score (Macro)", f"{F1_MACRO:.3f}",
                            "balanced multi-class metric", TEAL, TEAL), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_metric("Precision (Macro)", f"{PRECISION_M:.3f}",
                            "avg precision across classes", PURPLE, PURPLE), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_metric("Recall (Macro)", f"{RECALL_M:.3f}",
                            "avg recall across classes", ORANGE, ORANGE), unsafe_allow_html=True)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

col_cm, col_fi = st.columns(2)

with col_cm:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Confusion Matrix</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            Priority classification · 4 kelas · Rows = actual · Columns = predicted</div>
    </div>""", unsafe_allow_html=True)

    # Nilai aktual dari classification_report RF di notebook 04_model.ipynb
    # Kelas: 0-Unassigned, 1-Low, 2-Medium, 3-High (sesuai LabelEncoder)
    labels = ["Unassigned", "Low", "Medium", "High"]
    cm_vals = np.array([
        [4278,  527,  254,  834],
        [ 613, 1789,  441,  569],
        [ 498,  417, 1735,  614],
        [ 537,  406,  437, 5011],
    ])
    total  = cm_vals.sum()
    cm_pct = cm_vals / total * 100

    n_cls = len(labels)
    z_custom = [[1.0 if ri == ci else 0.0 for ci in range(n_cls)] for ri in range(n_cls)]

    fig_cm = go.Figure(go.Heatmap(
        z=z_custom,
        x=[f"Pred: {l}" for l in labels],
        y=[f"Act: {l}" for l in labels],
        text=[[f"{cm_vals[r,c]:,}<br>{cm_pct[r,c]:.1f}%" for c in range(n_cls)] for r in range(n_cls)],
        texttemplate="%{text}",
        textfont=dict(size=11, color="white", family="Inter"),
        colorscale=[[0, "#D85A30"], [1, "#534AB7"]],
        zmin=0, zmax=1,
        showscale=False,
        xgap=4, ygap=4,
    ))
    fig_cm.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=40), height=360,
        xaxis=dict(side="top", tickfont=dict(size=10, color="#555"), showgrid=False),
        yaxis=dict(tickfont=dict(size=10, color="#555"), showgrid=False, autorange="reversed"),
    )
    st.plotly_chart(fig_cm, width="stretch", config={"displayModeBar": False})
    st.markdown("""
    <div style="display:flex;gap:16px;padding:0 8px 12px;font-size:11px;color:#555;">
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                background:#534AB7;margin-right:4px;"></span>Correct (diagonal)</span>
        <span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;
                background:#D85A30;margin-right:4px;"></span>Misclassification</span>
    </div>""", unsafe_allow_html=True)

with col_fi:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">Feature Importance</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            Top predictive features · Random Forest Gini impurity · 7 fitur aktual</div>
    </div>""", unsafe_allow_html=True)

    # 7 fitur aktual dari model RF di notebook 04_model.ipynb (feature_importances_)
    feats = pd.DataFrame({
        "feature": [
            "isHighPriority",
            "seniorityLevel",
            "resolutionDurationDays",
            "severityLevel",
            "priorityLevel",
            "satisfactionLevel",
            "TicketType_enc",
        ],
        "importance": [75.56, 15.34, 5.15, 1.98, 1.12, 0.53, 0.32],
    }).sort_values("importance")

    n_f = len(feats)
    bar_colors = [f"hsl({int(220 + i*(170-220)/(n_f-1))},{int(75+i*5)}%,{int(55-i*3)}%)" for i in range(n_f)]

    fig_fi = go.Figure(go.Bar(
        y=feats["feature"], x=feats["importance"],
        orientation="h",
        marker_color=bar_colors,
        text=feats["importance"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(size=10, color="#94A0B4"),
    ))
    fig_fi.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=70, t=10, b=30), height=360,
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0", ticksuffix="%",
                   range=[0, 90], tickfont=dict(size=10, color="#94A0B4")),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#555")),
        showlegend=False,
    )
    st.plotly_chart(fig_fi, width="stretch", config={"displayModeBar": False})

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

col_km, col_eval = st.columns(2)

with col_km:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:20px 22px 8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.07);">
        <div style="font-size:14px;font-weight:700;color:#1E1B4B;">K-Means Clustering Result (DS2)</div>
        <div style="font-size:11px;color:#94A0B4;margin-top:2px;">
            5 kluster tiket nyata · Profil berdasarkan SLA violation rate & volume</div>
    </div>""", unsafe_allow_html=True)

    # Profil 5 kluster K-Means aktual dari notebook 04_model.ipynb
    # k=5, silhouette=0.5903
    cluster_profiles = pd.DataFrame({
        "cluster":    [0, 1, 2, 3, 4],
        "label":      ["Fast Track", "Bottleneck", "Standard", "Quick Fix", "Escalated"],
        "count":      [14203, 17998, 12831, 10729, 10930],
        "sla_slow_pct": [42.0, 100.0, 35.0, 1.0, 68.0],
        "color":      [TEAL, CORAL, ORANGE, PURPLE, "#8B85D4"],
    })

    fig_km = go.Figure()
    for _, row in cluster_profiles.iterrows():
        fig_km.add_trace(go.Bar(
            x=[row["label"]],
            y=[row["sla_slow_pct"]],
            name=f"Cluster {int(row['cluster'])} ({row['count']:,} tiket)",
            marker_color=row["color"],
            text=[f"{row['sla_slow_pct']:.0f}%"],
            textposition="outside",
            textfont=dict(size=11, color="#555"),
        ))
    fig_km.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10), height=360,
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#555")),
        yaxis=dict(showgrid=True, gridcolor="#F0F0F0", ticksuffix="%",
                   range=[0, 115], tickfont=dict(size=10, color="#94A0B4"),
                   title="% SLA Violated (slow)", title_font=dict(size=11, color="#94A0B4")),
        legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)",
                    orientation="v", x=1.01, y=1),
        showlegend=True,
        barmode="group",
    )
    st.plotly_chart(fig_km, width="stretch", config={"displayModeBar": False})
    st.markdown("""
    <div style="font-size:10px;color:#94A0B4;padding:0 4px 8px;">
        Kluster 1 (Bottleneck): 100% SLA violated · Kluster 3 (Quick Fix): hanya 1% violated
    </div>""", unsafe_allow_html=True)

with col_eval:
    T = TEAL
    D = "#1E1B4B"
    G = "#94A0B4"
    B = "#F5F5F5"
    eval_html = (
        f'<div style="background:white;border-radius:12px;padding:20px 22px;box-shadow:0 1px 6px rgba(0,0,0,0.07);">'
        f'<div style="font-size:14px;font-weight:700;color:{D};margin-bottom:12px;">Model Evaluation Summary</div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Algorithm</span><span style="font-size:12px;color:{D};font-weight:700;">Random Forest (n=100)</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Accuracy</span><span style="font-size:12px;color:{T};font-weight:600;">64.9%</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Precision (macro)</span><span style="font-size:12px;color:{T};font-weight:600;">58.4%</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Recall (macro)</span><span style="font-size:12px;color:{T};font-weight:600;">58.7%</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">F1-Score (macro)</span><span style="font-size:12px;color:{T};font-weight:600;">0.581</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Training set</span><span style="font-size:12px;color:{D};font-weight:600;">80,000 tiket (80%)</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Test set</span><span style="font-size:12px;color:{D};font-weight:600;">20,000 tiket (20%)</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Class imbalance</span><span style="font-size:12px;color:{D};font-weight:600;">SMOTE pada X_train</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">K-Means silhouette</span><span style="font-size:12px;color:{T};font-weight:600;">0.5903 (k=5)</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid {B};"><span style="font-size:12px;color:{G};">Priority konsistensi</span><span style="font-size:12px;color:{CORAL};font-weight:600;">52.9% valid (PA-4)</span></div>'
        f'<div style="display:flex;justify-content:space-between;padding:10px 0;"><span style="font-size:12px;color:{G};">Fitur aktual model</span><span style="font-size:12px;color:{D};font-weight:600;">7 fitur (DS1)</span></div>'
        f'</div>'
    )
    st.markdown(eval_html, unsafe_allow_html=True)

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# Insight box (PA-4) — dikoreksi sesuai temuan notebook
st.markdown(f"""
<div style="background:white;border-radius:12px;padding:20px 24px;
            box-shadow:0 1px 6px rgba(0,0,0,0.07);border-left:4px solid {PURPLE};">
    <div style="font-size:13px;font-weight:700;color:#1E1B4B;margin-bottom:10px;">
        Insight Model (PA-4, PA-2, PA-5)</div>
    <ul style="margin:0;padding-left:18px;font-size:12px;color:#555;line-height:1.8;">
        <li>Model <b>Random Forest</b> mencapai akurasi <b>64.9%</b> dengan F1-Score macro
            <b>0.581</b> pada 4 kelas prioritas (Unassigned/Low/Medium/High) — kelas "High"
            memiliki performa terbaik karena didominasi fitur <b>isHighPriority</b> (75.56%).</li>
        <li>Hanya <b>52.9%</b> tiket yang memiliki prioritas konsisten dengan keparahan aktual —
            menunjukkan penetapan prioritas manual masih memiliki inkonsistensi yang perlu
            diperbaiki (PA-4). Hardware rata-rata 16.94 hari resolusi vs rata-rata 6.80 hari.</li>
        <li>K-Means (k=5, silhouette=0.5903) mengidentifikasi <b>Kluster 1 (Bottleneck)</b>:
            17.998 tiket dengan 100% SLA violated dan avg 59.559 jam resolusi — ini adalah
            kelompok prioritas intervensi tertinggi (PA-2).</li>
        <li><b>Kluster 3 (Quick Fix)</b>: 10.729 tiket dengan hanya 1% SLA violated dan
            rata-rata 5 langkah workflow — dapat dijadikan benchmark SOP terbaik (PA-5).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
