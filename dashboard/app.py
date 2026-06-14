import streamlit as st

st.set_page_config(
    page_title="IT Helpdesk Analytics — Kelompok 14",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background-color: #F0F2FA !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2D2A7A 0%, #3D3A8A 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #C5C3E8 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Hide default stSidebarNav — kita pakai page_link manual di bawah header */
[data-testid="stSidebarNav"] { display: none !important; }

/* Hapus padding atas agar IT Helpdesk header mepet ke ujung kiri atas */
[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
[data-testid="stSidebarContent"] > div:first-child {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Style page_link buttons agar terlihat seperti nav */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    border-radius: 8px !important;
    margin: 2px 0 !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    color: #C5C3E8 !important;
    text-decoration: none !important;
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(83,74,183,0.5) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: #534AB7 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] svg { display: none !important; }

/* Hide keyboard shortcut widget & toolbar */
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stToolbar"]      { display: none !important; }

/* Hide sidebar collapse/expand buttons (source of "keyboard_double" text) */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stExpandSidebarButton"]   { display: none !important; }
[data-testid="stSidebarHeader"]         { display: none !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

/* Selectbox & multiselect dark styling */
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #A0A0C8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: .07em !important;
    text-transform: uppercase !important;
}

/* Main area padding */
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ── Definisikan navigation ────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/01_overview.py",          title="Overview",          icon="🏠"),
    st.Page("pages/02_sla_analysis.py",      title="SLA Analysis",      icon="📋"),
    st.Page("pages/03_agent_performance.py", title="Agent Performance", icon="👤"),
    st.Page("pages/04_model_results.py",     title="Model Results",     icon="🤖"),
])

# ── Sidebar: Header ───────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding: 16px 8px 8px;">
    <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#534AB7,#1D9E75);
                    border-radius:8px;display:flex;align-items:center;justify-content:center;
                    font-size:18px;flex-shrink:0;">📊</div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#FFFFFF !important;line-height:1.2;">IT Helpdesk</div>
            <div style="font-size:10px;color:#A0A0C8 !important;">Analytics · Kelompok 14</div>
        </div>
    </div>
</div>
<div style="height:1px;background:rgba(255,255,255,0.12);margin:0 8px 8px;"></div>
""", unsafe_allow_html=True)

# ── Sidebar: Nav links (page_link — bisa diklik) ─────────────────────────────
st.sidebar.page_link("pages/01_overview.py",          label="🏠  Overview")
st.sidebar.page_link("pages/02_sla_analysis.py",      label="📋  SLA Analysis")
st.sidebar.page_link("pages/03_agent_performance.py", label="👤  Agent Performance")
st.sidebar.page_link("pages/04_model_results.py",     label="🤖  Model Results")

st.sidebar.markdown("""
<div style="height:1px;background:rgba(255,255,255,0.12);margin:8px 8px 10px;"></div>
""", unsafe_allow_html=True)

# ── Sidebar: Global Filters ───────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding: 0 8px 4px;">
<div style="font-size:10px;color:#A0A0C8;font-weight:700;letter-spacing:.1em;
            text-transform:uppercase;margin-bottom:6px;">Global Filters</div>
</div>
""", unsafe_allow_html=True)

YEARS    = [2016, 2017, 2018, 2019, 2020]
ALL_CATS = ["Software", "Hardware", "Network", "Access"]
ALL_PRIS = ["High", "Medium", "Low"]

col_a, col_b = st.sidebar.columns(2)
with col_a:
    st.selectbox("Year From", YEARS, index=0, key="year_min")
with col_b:
    st.selectbox("Year To", YEARS, index=len(YEARS)-1, key="year_max")

st.sidebar.multiselect("Category", ALL_CATS, default=ALL_CATS, key="sel_cats")
st.sidebar.multiselect("Priority",  ALL_PRIS, default=ALL_PRIS, key="sel_pris")

pg.run()
