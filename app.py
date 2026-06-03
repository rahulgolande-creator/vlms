import streamlit as st
import pandas as pd
from datetime import datetime
import copy

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VendorLoad — Thermax Enviro",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #f4f3ef; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e8e6e0;
    border-radius: 12px;
    padding: 16px 20px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1a1917 !important;
}
section[data-testid="stSidebar"] * { color: #aaa !important; }
section[data-testid="stSidebar"] .stRadio label { 
    color: #aaa !important; font-size: 14px;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #666 !important; font-size: 11px;
}

/* Tables */
thead tr th {
    background: #1a1917 !important;
    color: white !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}
tbody tr:nth-child(even) { background: #fafaf8; }

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
.stButton > button[kind="primary"] {
    background: #1a1917 !important;
    border: none !important;
    color: white !important;
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stNumberInput input {
    border-radius: 8px !important;
    background: #fafaf8 !important;
    border: 1px solid #ddd !important;
    font-size: 13px !important;
}

/* Cards */
.vlms-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e8e6e0;
    padding: 20px;
    margin-bottom: 16px;
}
.kpi-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #e8e6e0;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 8px;
}
.kpi-num { font-size: 28px; font-weight: 700; line-height: 1; }
.kpi-label { font-size: 11px; color: #888; margin-top: 6px; }

/* Status pills */
.pill-hold   { background:#fef3c7; color:#b45309; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; }
.pill-loaded { background:#ede9fe; color:#6d28d9; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; }
.pill-rfd    { background:#eff6ff; color:#1d4ed8; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; }
.pill-dsp    { background:#f0fdf4; color:#15803d; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; }

/* Load bar */
.load-bar-wrap { background:#e5e7eb; border-radius:4px; height:8px; overflow:hidden; width:100%; }
.load-bar-fill { height:100%; border-radius:4px; }

/* Warn banner */
.warn-banner {
    background: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
}
.alert-banner {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
}
.success-banner {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
}
.info-row {
    background: #f8f7f3;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: #888;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ─── SEED DATA ────────────────────────────────────────────────────────────────
BUYERS   = ["SSS – Shantanu", "MN – Mohan", "AB – Amit", "CH – Chetan", "RK – Rahul"]
PRODUCTS = ["ABF", "PBF", "ESP", "ALL"]
REGIONS  = ["Pune", "Solapur", "Nashik", "Aurangabad"]
QAC_LIST = ["A", "B", "C", "D"]
STATUSES = ["HOLD", "Loaded", "RFD", "DSP"]
MONTHS   = ["Mar-25","Apr-25","May-25","Jun-25","Jul-25","Aug-25"]

INIT_VENDORS = [
    dict(id=1,  name="NIRMANTECH ENGINEERS", region="Pune",       product="ABF", qac="C", totalCap=50,  tlCap=30,  loaded=9.9,  rfdReleased=2.1, customer="T+O", regular=True),
    dict(id=2,  name="AARADHYA INDUSTRIES",  region="Solapur",    product="ABF", qac="B", totalCap=180, tlCap=180, loaded=97.3, rfdReleased=0,   customer="T",   regular=True),
    dict(id=3,  name="SWAMI SAMARTH FAB",    region="Pune",       product="PBF", qac="B", totalCap=200, tlCap=160, loaded=68.8, rfdReleased=5.0, customer="T+O", regular=True),
    dict(id=4,  name="STEEL CRAFT",          region="Pune",       product="ABF", qac="B", totalCap=80,  tlCap=15,  loaded=57.9, rfdReleased=0,   customer="T+O", regular=True),
    dict(id=5,  name="MR ENGINEERING",       region="Nashik",     product="ESP", qac="C", totalCap=40,  tlCap=16,  loaded=47.7, rfdReleased=0,   customer="T+O", regular=False),
    dict(id=6,  name="RAVI INDUSTRIES",      region="Pune",       product="ALL", qac="A", totalCap=300, tlCap=250, loaded=90.0, rfdReleased=12.0,customer="T+O", regular=True),
    dict(id=7,  name="LOKESH ENGINEERING",   region="Aurangabad", product="PBF", qac="B", totalCap=120, tlCap=100, loaded=46.0, rfdReleased=3.5, customer="T",   regular=True),
    dict(id=8,  name="DYNECH DESIGNER",      region="Nashik",     product="ABF", qac="B", totalCap=100, tlCap=100, loaded=27.0, rfdReleased=1.0, customer="T+O", regular=True),
    dict(id=9,  name="ALFA ENGINEERING",     region="Pune",       product="ESP", qac="A", totalCap=100, tlCap=40,  loaded=3.2,  rfdReleased=0,   customer="T+O", regular=True),
    dict(id=10, name="D N ENTERPRISES",      region="Solapur",    product="PBF", qac="C", totalCap=60,  tlCap=60,  loaded=0,    rfdReleased=0,   customer="T",   regular=False),
    dict(id=11, name="GRAVITY ENTERPRISES",  region="Aurangabad", product="ABF", qac="D", totalCap=50,  tlCap=50,  loaded=0,    rfdReleased=0,   customer="T",   regular=False),
    dict(id=12, name="ANNU ENTERPRISES",     region="Solapur",    product="ALL", qac="B", totalCap=60,  tlCap=60,  loaded=15.2, rfdReleased=3.0, customer="T",   regular=True),
    dict(id=13, name="INDRAJIT INDUSTRIES",  region="Pune",       product="ABF", qac="D", totalCap=20,  tlCap=15,  loaded=7.8,  rfdReleased=0,   customer="T+O", regular=True),
    dict(id=14, name="FABTECH ENGINEERING",  region="Nashik",     product="PBF", qac="C", totalCap=80,  tlCap=80,  loaded=7.2,  rfdReleased=0,   customer="T",   regular=True),
    dict(id=15, name="SK ENGINEERING",       region="Aurangabad", product="ESP", qac="B", totalCap=30,  tlCap=30,  loaded=23.7, rfdReleased=0,   customer="T+O", regular=True),
]

INIT_PRS = [
    dict(id="PR-001", project="E142300", buyer="SSS – Shantanu", item="AY01 – Bagfilter Casing & Hopper", product="ABF", weightMT=3.92,  vendorId=1,  status="Loaded", loadingDate="Apr-25", needBy="May-26", poNo="176440", poAmt=137095),
    dict(id="PR-002", project="E142301", buyer="MN – Mohan",     item="ESP Inlet Duct Assembly",          product="ESP", weightMT=8.5,   vendorId=15, status="RFD",    loadingDate="Mar-25", needBy="Jun-25", poNo="176441", poAmt=310000),
    dict(id="PR-003", project="E142302", buyer="AB – Amit",      item="PBF Casing Module",                product="PBF", weightMT=12.0,  vendorId=3,  status="Loaded", loadingDate="Apr-25", needBy="Aug-25", poNo="176442", poAmt=520000),
    dict(id="PR-004", project="E142303", buyer="CH – Chetan",    item="ABF Outlet Cone Set",              product="ABF", weightMT=2.1,   vendorId=8,  status="HOLD",   loadingDate="",       needBy="Jul-25", poNo="176443", poAmt=89000),
    dict(id="PR-005", project="E142304", buyer="RK – Rahul",     item="ESP Frame Structure",              product="ESP", weightMT=18.6,  vendorId=5,  status="Loaded", loadingDate="Mar-25", needBy="Sep-25", poNo="176444", poAmt=720000),
    dict(id="PR-006", project="E142305", buyer="SSS – Shantanu", item="ABF Hopper Set",                  product="ABF", weightMT=5.4,   vendorId=4,  status="Loaded", loadingDate="Apr-25", needBy="Jul-25", poNo="176445", poAmt=198000),
    dict(id="PR-007", project="E142306", buyer="MN – Mohan",     item="PBF Filter Cage Assembly",        product="PBF", weightMT=3.2,   vendorId=7,  status="DSP",    loadingDate="Feb-25", needBy="May-25", poNo="176446", poAmt=115000),
    dict(id="PR-008", project="E142307", buyer="AB – Amit",      item="ABF Access Door Panels",          product="ABF", weightMT=1.8,   vendorId=13, status="HOLD",   loadingDate="",       needBy="Aug-25", poNo="176447", poAmt=62000),
]

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
def init_state():
    if "vendors" not in st.session_state:
        st.session_state.vendors = copy.deepcopy(INIT_VENDORS)
    if "prs" not in st.session_state:
        st.session_state.prs = copy.deepcopy(INIT_PRS)
    if "override_log" not in st.session_state:
        st.session_state.override_log = []
    if "lf_step" not in st.session_state:
        st.session_state.lf_step = 1
    if "lf_data" not in st.session_state:
        st.session_state.lf_data = {}
    if "lf_submitted" not in st.session_state:
        st.session_state.lf_submitted = False

init_state()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def load_pct(v):
    net = v["loaded"] - v["rfdReleased"]
    return round((net / v["tlCap"]) * 100) if v["tlCap"] > 0 else 999

def balance(v):
    return round(v["tlCap"] - (v["loaded"] - v["rfdReleased"]), 1)

def enrich_vendors():
    result = []
    for v in st.session_state.vendors:
        ev = dict(v)
        ev["pct"] = load_pct(v)
        ev["bal"] = balance(v)
        result.append(ev)
    return result

def get_vendor_by_id(vid):
    for v in st.session_state.vendors:
        if v["id"] == vid:
            return v
    return None

def pct_color(p):
    if p > 100: return "#dc2626"
    if p > 70:  return "#d97706"
    return "#16a34a"

def pct_label(p):
    if p > 100: return "OVERLOADED"
    if p > 70:  return "HIGH"
    if p > 30:  return "NORMAL"
    return "AVAILABLE"

def status_pill(s):
    cls = {"HOLD":"pill-hold","Loaded":"pill-loaded","RFD":"pill-rfd","DSP":"pill-dsp"}.get(s,"pill-hold")
    return f'<span class="{cls}">{s}</span>'

def load_bar_html(pct, height=8):
    capped = min(abs(pct), 100)
    col = pct_color(pct)
    return f"""
    <div style="display:flex;align-items:center;gap:8px">
      <div class="load-bar-wrap" style="height:{height}px">
        <div class="load-bar-fill" style="width:{capped}%;background:{col}"></div>
      </div>
      <span style="font-size:11px;font-weight:700;color:{col};min-width:36px;text-align:right">{pct}%</span>
    </div>"""

def change_status(pr_id, new_status):
    for i, p in enumerate(st.session_state.prs):
        if p["id"] != pr_id:
            continue
        old = p["status"]
        wpm = round(p["weightMT"] / 6, 2)
        # RFD release
        if old == "Loaded" and new_status in ("RFD", "DSP") and p.get("vendorId"):
            for j, v in enumerate(st.session_state.vendors):
                if v["id"] == p["vendorId"]:
                    st.session_state.vendors[j]["rfdReleased"] = round(v["rfdReleased"] + wpm, 2)
                    break
        # Re-HOLD reversal
        if old == "Loaded" and new_status == "HOLD" and p.get("vendorId"):
            for j, v in enumerate(st.session_state.vendors):
                if v["id"] == p["vendorId"]:
                    st.session_state.vendors[j]["loaded"] = round(v["loaded"] - wpm, 2)
                    break
        st.session_state.prs[i]["status"] = new_status
        if new_status == "Loaded":
            st.session_state.prs[i]["loadingDate"] = "May-25"
        break

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:0 0 16px;border-bottom:1px solid #333;margin-bottom:20px"><div style="font-size:17px;font-weight:700;color:#fff;letter-spacing:-.3px">⚙ VendorLoad</div><div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-top:3px">Thermax Enviro</div></div>', unsafe_allow_html=True)

    page = st.radio("Navigation", ["📊 Dashboard", "📋 PR Tracker", "⊕ Load Vendor", "⊞ Vendor Master", "◎ Audit Log"], label_visibility="collapsed")

    ev = enrich_vendors()
    overloaded = [v for v in ev if v["bal"] < 0]
    if overloaded:
        st.markdown(f"""
        <div style="background:#7f1d1d;border-radius:8px;padding:10px 12px;margin-top:20px">
          <div style="font-size:11px;font-weight:700;color:#fca5a5">⚠ {len(overloaded)} overloaded</div>
          <div style="font-size:10px;color:#f87171;margin-top:2px">Go to Dashboard</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-size:10px;color:#444">Current month: May-25</p>', unsafe_allow_html=True)

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("## Capacity Dashboard")
    st.markdown('<p style="color:#888;margin-top:-12px;margin-bottom:20px">Live vendor loading status — current month (May-25)</p>', unsafe_allow_html=True)

    ev = enrich_vendors()
    overloaded = [v for v in ev if v["bal"] < 0]
    active_jobs = len([p for p in st.session_state.prs if p["status"] == "Loaded"])

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#1a1917">{len(ev)}</div><div class="kpi-label">Total Vendors</div></div>', unsafe_allow_html=True)
    with c2:
        healthy = len([v for v in ev if v["pct"] <= 70])
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#16a34a">{healthy}</div><div class="kpi-label">Healthy (≤70%)</div></div>', unsafe_allow_html=True)
    with c3:
        high = len([v for v in ev if 70 < v["pct"] <= 100])
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#d97706">{high}</div><div class="kpi-label">High Load (70–100%)</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#dc2626">{len(overloaded)}</div><div class="kpi-label">Overloaded (&gt;100%)</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-num" style="color:#6d28d9">{active_jobs}</div><div class="kpi-label">Active Jobs</div></div>', unsafe_allow_html=True)

    # Overloaded alert
    if overloaded:
        names = "  |  ".join([f"{v['name']}  {v['pct']}%  ({v['bal']} MT)" for v in overloaded])
        st.markdown(f'<div class="alert-banner">⚠️  <strong style="color:#991b1b">Overloaded vendors — immediate attention required</strong><br><span style="font-size:12px;color:#991b1b">{names}</span></div>', unsafe_allow_html=True)

    # Filters
    st.markdown("#### Vendor Load Table")
    fc1, fc2, fc3 = st.columns([1.5, 1.5, 3])
    with fc1:
        f_region = st.selectbox("Region", ["ALL"] + REGIONS, key="dash_region")
    with fc2:
        f_product = st.selectbox("Product", ["ALL"] + PRODUCTS, key="dash_product")
    with fc3:
        f_search = st.text_input("Search vendor", placeholder="Type vendor name…", key="dash_search")

    filtered = [v for v in ev
                if (f_region == "ALL" or v["region"] == f_region)
                and (f_product == "ALL" or v["product"] in (f_product, "ALL"))
                and (f_search.lower() in v["name"].lower())]
    filtered.sort(key=lambda v: v["pct"], reverse=True)

    # Build display dataframe
    rows = []
    for v in filtered:
        col = pct_color(v["pct"])
        rows.append({
            "Vendor": v["name"],
            "Region": v["region"],
            "Product": v["product"],
            "Load %": v["pct"],
            "TL Cap (MT)": v["tlCap"],
            "Loaded (MT)": round(v["loaded"] - v["rfdReleased"], 1),
            "RFD Released": v["rfdReleased"] if v["rfdReleased"] > 0 else 0,
            "Balance (MT)": v["bal"],
            "Status": pct_label(v["pct"]),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        def color_load(val):
            c = pct_color(val)
            return f"color: {c}; font-weight: 700"
        def color_bal(val):
            c = "#dc2626" if val < 0 else "#d97706" if val < 10 else "#15803d"
            return f"color: {c}; font-weight: 700"
        def color_row(row):
            if row["Load %"] > 100: return ["background-color:#fff5f5"]*len(row)
            if row["Load %"] > 70:  return ["background-color:#fffdf0"]*len(row)
            return [""]*len(row)

        styled = (df.style
            .map(color_load, subset=["Load %"])
            .map(color_bal, subset=["Balance (MT)"])
            .apply(color_row, axis=1)
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.info("No vendors match the current filters.")

    # Top / Bottom ranking
    st.markdown("---")
    rc1, rc2 = st.columns(2)
    top5 = sorted(ev, key=lambda v: v["pct"], reverse=True)[:5]
    bot5 = sorted(ev, key=lambda v: v["pct"])[:5]

    with rc1:
        st.markdown("#### 🔴 Top 5 — Most Loaded")
        for i, v in enumerate(top5):
            cc1, cc2, cc3 = st.columns([.3, 2, 1.5])
            with cc1: st.markdown(f'<span style="color:#bbb;font-size:12px">{i+1}</span>', unsafe_allow_html=True)
            with cc2: st.markdown(f'<span style="font-size:12px;font-weight:600">{v["name"]}</span>', unsafe_allow_html=True)
            with cc3: st.markdown(load_bar_html(v["pct"], 5), unsafe_allow_html=True)

    with rc2:
        st.markdown("#### 🟢 Bottom 5 — Most Available")
        for i, v in enumerate(bot5):
            cc1, cc2, cc3 = st.columns([.3, 2, 1.5])
            with cc1: st.markdown(f'<span style="color:#bbb;font-size:12px">{i+1}</span>', unsafe_allow_html=True)
            with cc2: st.markdown(f'<span style="font-size:12px;font-weight:600">{v["name"]}</span>', unsafe_allow_html=True)
            with cc3: st.markdown(load_bar_html(v["pct"], 5), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PR TRACKER
# ════════════════════════════════════════════════════════════
elif page == "📋 PR Tracker":
    st.markdown("## PR Tracker")
    hc1, hc2 = st.columns([4,1])
    with hc2:
        add_pr = st.button("+ Add PR", type="primary", use_container_width=True)

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1: f_buyer = st.selectbox("Buyer", ["ALL"] + BUYERS, key="pr_buyer")
    with fc2: f_status = st.selectbox("Status", ["ALL"] + STATUSES, key="pr_status")
    with fc3: f_product = st.selectbox("Product", ["ALL"] + PRODUCTS, key="pr_product")

    # Add PR form
    if add_pr:
        st.session_state["show_add_pr"] = True
    if st.session_state.get("show_add_pr"):
        with st.container():
            st.markdown('<div class="vlms-card" style="border:2px solid #e8c547">', unsafe_allow_html=True)
            st.markdown("#### New Purchase Requisition")
            npc1, npc2, npc3, npc4 = st.columns(4)
            with npc1:
                np_proj = st.text_input("Project No", key="np_proj")
                np_weight = st.number_input("Weight (MT)", min_value=0.0, step=0.1, key="np_weight")
            with npc2:
                np_item = st.text_input("Item Description", key="np_item")
                np_po = st.text_input("PO Number", key="np_po")
            with npc3:
                np_buyer = st.selectbox("Buyer", BUYERS, key="np_buyer")
                np_needby = st.text_input("Need-By Date (Mon-YY)", key="np_needby")
            with npc4:
                np_product = st.selectbox("Product Type", [p for p in PRODUCTS if p != "ALL"], key="np_product")
                np_poamt = st.number_input("PO Amount (₹)", min_value=0, step=1000, key="np_poamt")

            bc1, bc2 = st.columns([1, 5])
            with bc1:
                if st.button("Save PR", type="primary", key="save_pr"):
                    if np_proj and np_item:
                        new_id = f"PR-{len(st.session_state.prs)+1:03d}"
                        st.session_state.prs.append(dict(
                            id=new_id, project=np_proj, buyer=np_buyer, item=np_item,
                            product=np_product, weightMT=np_weight, vendorId=None,
                            status="HOLD", loadingDate="", needBy=np_needby,
                            poNo=np_po, poAmt=np_poamt
                        ))
                        st.session_state["show_add_pr"] = False
                        st.success(f"PR {new_id} created!")
                        st.rerun()
                    else:
                        st.error("Project No and Item Description are required.")
            with bc2:
                if st.button("Cancel", key="cancel_pr"):
                    st.session_state["show_add_pr"] = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # PR table
    filtered_prs = [p for p in st.session_state.prs
                    if (f_buyer == "ALL" or p["buyer"] == f_buyer)
                    and (f_status == "ALL" or p["status"] == f_status)
                    and (f_product == "ALL" or p["product"] == f_product)]

    st.markdown(f'<p style="color:#888;font-size:13px">{len(filtered_prs)} purchase requisitions</p>', unsafe_allow_html=True)

    for p in filtered_prs:
        vendor = get_vendor_by_id(p.get("vendorId"))
        vname = vendor["name"] if vendor else "—"

        with st.container():
            c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([1, 1.5, 2.5, 0.8, 0.8, 1.8, 0.9, 0.9, 2])
            with c1: st.markdown(f'<span style="font-family:monospace;font-size:11px;color:#888">{p["id"]}</span>', unsafe_allow_html=True)
            with c2: st.markdown(f'<span style="font-weight:600;font-size:12px">{p["project"]}</span>', unsafe_allow_html=True)
            with c3: st.markdown(f'<span style="font-size:12px">{p["item"][:35]}{"…" if len(p["item"])>35 else ""}</span>', unsafe_allow_html=True)
            with c4: st.markdown(f'<span style="font-size:11px;background:#ede9fe;color:#6d28d9;padding:2px 7px;border-radius:20px;font-weight:600">{p["product"]}</span>', unsafe_allow_html=True)
            with c5: st.markdown(f'<span style="font-size:12px">{p["weightMT"]} MT</span>', unsafe_allow_html=True)
            with c6: st.markdown(f'<span style="font-size:11px;color:#555">{vname[:22]}</span>', unsafe_allow_html=True)
            with c7: st.markdown(f'<span style="font-size:11px;color:#888">{p["loadingDate"] or "—"}</span>', unsafe_allow_html=True)
            with c8: st.markdown(status_pill(p["status"]), unsafe_allow_html=True)
            with c9:
                transitions = {"HOLD": ["Loaded"], "Loaded": ["HOLD","RFD"], "RFD": ["DSP"], "DSP": []}
                next_states = transitions.get(p["status"], [])
                if next_states:
                    btn_cols = st.columns(len(next_states))
                    for bi, ns in enumerate(next_states):
                        with btn_cols[bi]:
                            if st.button(f"→ {ns}", key=f"status_{p['id']}_{ns}", use_container_width=True):
                                change_status(p["id"], ns)
                                st.rerun()
                else:
                    st.markdown('<span style="font-size:11px;color:#ccc">Final</span>', unsafe_allow_html=True)

        st.markdown('<hr style="border:0;border-top:1px solid #f5f4f0;margin:4px 0">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# LOADING FORM
# ════════════════════════════════════════════════════════════
elif page == "⊕ Load Vendor":
    st.markdown("## Vendor Loading Form")
    st.markdown('<p style="color:#888;margin-top:-12px">Assign a PR to a vendor · Live capacity shown</p>', unsafe_allow_html=True)

    ev = enrich_vendors()
    top5 = sorted(ev, key=lambda v: v["pct"], reverse=True)[:5]
    bot5 = sorted(ev, key=lambda v: v["pct"])[:5]

    # Step indicator
    step = st.session_state.lf_step
    s1c, s2c, s3c = st.columns([1,1,1])
    for col, s, label in [(s1c,1,"PR Details"),(s2c,2,"Select Vendor"),(s3c,3,"Review & Submit")]:
        with col:
            active_style = "background:#1a1917;color:white" if step >= s else "background:#e5e7eb;color:#999"
            st.markdown(f'<div style="{active_style};border-radius:8px;padding:8px;text-align:center;font-size:12px;font-weight:600">Step {s}: {label}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Submitted confirmation
    if st.session_state.lf_submitted:
        st.markdown('<div class="success-banner" style="text-align:center;padding:48px"><div style="font-size:48px">✅</div><div style="font-size:20px;font-weight:700;margin:12px 0">Loading confirmed!</div><p style="color:#888">Vendor capacity updated. PR status set to Loaded.</p></div>', unsafe_allow_html=True)
        if st.button("Load another PR", type="primary"):
            st.session_state.lf_step = 1
            st.session_state.lf_data = {}
            st.session_state.lf_submitted = False
            st.rerun()

    # ── STEP 1
    elif step == 1:
        with st.container():
            st.markdown("#### PR Details")
            c1, c2 = st.columns(2)
            with c1:
                proj    = st.text_input("Project Number *", value=st.session_state.lf_data.get("project",""))
                item    = st.text_input("Item Description *", value=st.session_state.lf_data.get("item",""))
                po_no   = st.text_input("PO Number", value=st.session_state.lf_data.get("poNo",""))
                need_by = st.text_input("Need-By Date (Mon-YY)", value=st.session_state.lf_data.get("needBy",""))
            with c2:
                buyer_val   = st.session_state.lf_data.get("buyer", "")
                buyer_idx   = BUYERS.index(buyer_val) if buyer_val in BUYERS else 0
                buyer       = st.selectbox("Buyer *", BUYERS, index=buyer_idx)
                prod_val    = st.session_state.lf_data.get("product","ABF")
                prod_opts   = [p for p in PRODUCTS if p != "ALL"]
                prod_idx    = prod_opts.index(prod_val) if prod_val in prod_opts else 0
                product     = st.selectbox("Product Type *", prod_opts, index=prod_idx)
                weight      = st.number_input("Total Weight (MT) *", min_value=0.0, step=0.1, value=float(st.session_state.lf_data.get("weightMT",0) or 0))

            if weight > 0:
                st.markdown(f'<div class="info-row">Monthly loading weight = Total weight ÷ 6 = <strong style="color:#1a1917">{weight/6:.2f} MT/month</strong></div>', unsafe_allow_html=True)

            if st.button("Next: Select Vendor →", type="primary", disabled=not(proj and buyer and weight and item)):
                st.session_state.lf_data.update(dict(project=proj, buyer=buyer, item=item, product=product, weightMT=weight, needBy=need_by, poNo=po_no))
                st.session_state.lf_step = 2
                st.rerun()

    # ── STEP 2
    elif step == 2:
        lfd = st.session_state.lf_data
        weight = float(lfd.get("weightMT", 0))
        wpm = round(weight / 6, 2)
        product = lfd.get("product", "ABF")

        st.markdown(f"#### Select Vendor — {product} · All Regions")
        st.markdown(f'<p style="color:#888;font-size:12px">Adding <strong>{wpm} MT/mo</strong> to vendor balance</p>', unsafe_allow_html=True)

        lf_vendors = [v for v in ev if v["product"] in (product, "ALL")]
        lf_vendors.sort(key=lambda v: v["pct"])

        # Vendor selection table
        rows = []
        for v in lf_vendors:
            new_bal = round(v["bal"] - wpm, 1)
            rows.append({
                "Vendor": v["name"],
                "Region": v["region"],
                "Load %": v["pct"],
                "TL Cap (MT)": v["tlCap"],
                "Balance After (MT)": new_bal,
                "QAC": v["qac"],
                "Regular": "✓ Regular" if v["regular"] else "Non-reg",
                "_id": v["id"],
                "_over": new_bal < 0
            })

        st.markdown('<div class="vlms-card">', unsafe_allow_html=True)
        for row in rows:
            over = row["_over"]
            vid  = row["_id"]
            sel  = (st.session_state.lf_data.get("selectedVendorId") == vid)
            bg = "#fefde8" if sel else "#fff5f5" if over else "#fff"
            bal_color = "#dc2626" if row["Balance After (MT)"] < 0 else "#d97706" if row["Balance After (MT)"] < 5 else "#15803d"
            warn_icon = " ⚠" if over else ""

            vc1,vc2,vc3,vc4,vc5,vc6,vc7,vc8 = st.columns([.4,2.5,1.2,1.5,1.2,1.2,.6,.8])
            with vc1:
                radio_style = "background:#e8c547;border-radius:50%;width:16px;height:16px" if sel else ""
                st.markdown(f'<div style="{radio_style}"></div>', unsafe_allow_html=True)
                if st.button("●" if sel else "○", key=f"sel_v_{vid}", use_container_width=True):
                    st.session_state.lf_data["selectedVendorId"] = vid
                    st.session_state.lf_data["showWarn"] = over
                    st.session_state.lf_data["justification"] = ""
                    st.rerun()
            with vc2: st.markdown(f'<span style="font-weight:600;font-size:12px;color:{"#991b1b" if over else "#1a1917"}">{row["Vendor"]}{warn_icon}</span>', unsafe_allow_html=True)
            with vc3: st.markdown(f'<span style="font-size:11px;background:#f0efe9;padding:2px 7px;border-radius:20px">{row["Region"]}</span>', unsafe_allow_html=True)
            with vc4: st.markdown(load_bar_html(row["Load %"], 6), unsafe_allow_html=True)
            with vc5: st.markdown(f'<span style="font-size:12px">{row["TL Cap (MT)"]} MT</span>', unsafe_allow_html=True)
            with vc6: st.markdown(f'<span style="font-size:12px;font-weight:700;color:{bal_color}">{("+" if row["Balance After (MT)"]>0 else "")}{row["Balance After (MT)"]} MT{warn_icon}</span>', unsafe_allow_html=True)
            with vc7: st.markdown(f'<span style="font-size:12px;font-weight:700;background:#f0efe9;padding:2px 7px;border-radius:20px">{row["QAC"]}</span>', unsafe_allow_html=True)
            with vc8: st.markdown(f'<span style="font-size:11px;color:{"#15803d" if row["Regular"]=="✓ Regular" else "#888"}">{row["Regular"]}</span>', unsafe_allow_html=True)
            st.markdown('<hr style="border:0;border-top:1px solid #f5f4f0;margin:3px 0">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Top / Bottom panels
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown("##### 🔴 Top loaded — steer away")
            for i, v in enumerate(top5):
                st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="color:#ccc;font-size:11px;width:14px">{i+1}</span><span style="font-size:11px;flex:1">{v["name"]}</span></div>' + load_bar_html(v["pct"],4), unsafe_allow_html=True)
        with tc2:
            st.markdown("##### 🟢 Bottom loaded — prefer these")
            for i, v in enumerate(bot5):
                st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="color:#ccc;font-size:11px;width:14px">{i+1}</span><span style="font-size:11px;flex:1">{v["name"]}</span></div>' + load_bar_html(v["pct"],4), unsafe_allow_html=True)

        # Overload warning
        sel_id = st.session_state.lf_data.get("selectedVendorId")
        show_warn = st.session_state.lf_data.get("showWarn", False)
        if show_warn and sel_id:
            sel_v = next((v for v in ev if v["id"] == sel_id), None)
            if sel_v:
                new_bal = round(sel_v["bal"] - wpm, 1)
                st.markdown(f"""
                <div class="warn-banner">
                  ⚠️ <strong style="color:#92400e">Capacity warning — {sel_v["name"]}</strong><br>
                  <span style="font-size:12px;color:#78350f">
                  Adding {wpm} MT will make balance <strong>{new_bal} MT</strong>.
                  TL capacity: {sel_v["tlCap"]} MT/mo. A justification is required to proceed.
                  </span>
                </div>""", unsafe_allow_html=True)
                just = st.text_area("Justification for override (required — min 20 characters)",
                    value=st.session_state.lf_data.get("justification",""),
                    placeholder="e.g. Vendor confirmed availability via phone on 29-May-25, SCM head approved…",
                    key="lf_justification", height=80)
                st.session_state.lf_data["justification"] = just
        else:
            just = st.session_state.lf_data.get("justification","")

        justification = st.session_state.lf_data.get("justification","")
        can_proceed = sel_id and (not show_warn or len(justification) >= 20)

        bc1, bc2, _ = st.columns([1, 1.5, 5])
        with bc1:
            if st.button("← Back", key="lf_back2"):
                st.session_state.lf_step = 1
                st.rerun()
        with bc2:
            if st.button("Next: Review →", type="primary", disabled=not can_proceed, key="lf_next2"):
                st.session_state.lf_step = 3
                st.rerun()

    # ── STEP 3
    elif step == 3:
        lfd = st.session_state.lf_data
        weight = float(lfd.get("weightMT",0))
        wpm = round(weight / 6, 2)
        sel_id = lfd.get("selectedVendorId")
        sel_v = next((v for v in ev if v["id"] == sel_id), None)

        st.markdown("#### Review & Confirm")
        if sel_v:
            rc1, rc2 = st.columns(2)
            fields = [("Project",lfd.get("project","")), ("Buyer",lfd.get("buyer","")),
                      ("Item",lfd.get("item","")), ("Product",lfd.get("product","")),
                      ("Weight",f"{weight} MT"), ("Monthly Load",f"{wpm} MT/mo"),
                      ("Need-By",lfd.get("needBy","")), ("PO No",lfd.get("poNo",""))]
            for i, (label, val) in enumerate(fields):
                with (rc1 if i%2==0 else rc2):
                    st.markdown(f'<div style="background:#fafaf8;border:1px solid #eee;border-radius:8px;padding:10px 14px;margin-bottom:8px"><div style="font-size:10px;color:#999;text-transform:uppercase;letter-spacing:.8px">{label}</div><div style="font-size:13px;font-weight:600">{val or "—"}</div></div>', unsafe_allow_html=True)

            new_bal = round(sel_v["bal"] - wpm, 1)
            banner_bg = "#fef3c7" if new_bal < 0 else "#f0fdf4"
            banner_border = "#fbbf24" if new_bal < 0 else "#86efac"
            bal_color = "#dc2626" if new_bal < 0 else "#15803d"
            st.markdown(f"""
            <div style="background:{banner_bg};border:1px solid {banner_border};border-radius:10px;padding:14px 16px;margin:10px 0">
              <strong style="font-size:13px">Vendor: {sel_v["name"]}</strong><br>
              <span style="font-size:12px">
                Current load: <strong>{sel_v["pct"]}%</strong> &nbsp;|&nbsp;
                TL Cap: <strong>{sel_v["tlCap"]} MT</strong> &nbsp;|&nbsp;
                Balance after: <strong style="color:{bal_color}">{("+" if new_bal>0 else "")}{new_bal} MT</strong>
              </span>
            </div>""", unsafe_allow_html=True)

            if lfd.get("showWarn") and lfd.get("justification"):
                st.markdown(f'<div style="background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:10px 14px;font-size:12px;color:#7c2d12"><strong>Override justification:</strong> {lfd["justification"]}</div>', unsafe_allow_html=True)

            warn_note = "Override logged to audit trail" if lfd.get("showWarn") else ""
            st.markdown(f'<div class="info-row">On confirm: PR created (status: Loaded) · Vendor balance updated {("· " + warn_note) if warn_note else ""}</div>', unsafe_allow_html=True)

            bc1, bc2, _ = st.columns([1, 1.5, 5])
            with bc1:
                if st.button("← Back", key="lf_back3"):
                    st.session_state.lf_step = 2
                    st.rerun()
            with bc2:
                if st.button("✓ Confirm Loading", type="primary", key="lf_confirm"):
                    # Create PR
                    new_id = f"PR-{len(st.session_state.prs)+1:03d}"
                    wpm2 = round(weight / 6, 2)
                    st.session_state.prs.append(dict(
                        id=new_id, project=lfd["project"], buyer=lfd["buyer"],
                        item=lfd["item"], product=lfd["product"], weightMT=weight,
                        vendorId=sel_id, status="Loaded", loadingDate="May-25",
                        needBy=lfd.get("needBy",""), poNo=lfd.get("poNo",""), poAmt=0
                    ))
                    # Update vendor
                    for i, v in enumerate(st.session_state.vendors):
                        if v["id"] == sel_id:
                            st.session_state.vendors[i]["loaded"] = round(v["loaded"] + wpm2, 2)
                            break
                    # Log override
                    if lfd.get("showWarn") and lfd.get("justification"):
                        st.session_state.override_log.append(dict(
                            ts=datetime.now().strftime("%d %b %Y %H:%M"),
                            pr=new_id, vendor=sel_v["name"], buyer=lfd["buyer"],
                            overloadMT=round(-sel_v["bal"] + wpm2, 1),
                            justification=lfd["justification"]
                        ))
                    st.session_state.lf_submitted = True
                    st.session_state.lf_step = 1
                    st.session_state.lf_data = {}
                    st.rerun()

# ════════════════════════════════════════════════════════════
# VENDOR MASTER
# ════════════════════════════════════════════════════════════
elif page == "⊞ Vendor Master":
    ev = enrich_vendors()
    hc1, hc2 = st.columns([4,1])
    with hc1: st.markdown("## Vendor Master")
    with hc2:
        add_v = st.button("+ Add Vendor", type="primary", use_container_width=True)

    if add_v:
        st.session_state["show_add_vendor"] = True
    if st.session_state.get("show_add_vendor"):
        st.markdown('<div class="vlms-card" style="border:2px solid #e8c547">', unsafe_allow_html=True)
        st.markdown("#### New Vendor")
        vc1, vc2, vc3, vc4 = st.columns(4)
        with vc1:
            nv_name = st.text_input("Vendor Name *", key="nv_name")
            nv_total = st.number_input("Total Capacity (MT/mo) *", min_value=0.0, step=5.0, key="nv_total")
        with vc2:
            nv_region = st.selectbox("Region", REGIONS, key="nv_region")
            nv_tl = st.number_input("TL Capacity (MT/mo) *", min_value=0.0, step=5.0, key="nv_tl")
        with vc3:
            nv_product = st.selectbox("Product Type", PRODUCTS, key="nv_product")
            nv_customer = st.selectbox("Customer Mix", ["T","T+O"], key="nv_customer")
        with vc4:
            nv_qac = st.selectbox("QAC Rating", QAC_LIST, index=1, key="nv_qac")
            nv_regular = st.selectbox("Regular Vendor?", ["Yes – Regular","No – Non-regular"], key="nv_regular")

        bc1, bc2 = st.columns([1,5])
        with bc1:
            if st.button("Save Vendor", type="primary", key="save_vendor"):
                if nv_name and nv_tl > 0:
                    new_vid = max(v["id"] for v in st.session_state.vendors) + 1
                    st.session_state.vendors.append(dict(
                        id=new_vid, name=nv_name, region=nv_region, product=nv_product,
                        qac=nv_qac, totalCap=nv_total, tlCap=nv_tl, loaded=0, rfdReleased=0,
                        customer=nv_customer, regular=(nv_regular == "Yes – Regular")
                    ))
                    st.session_state["show_add_vendor"] = False
                    st.success(f"Vendor '{nv_name}' added!")
                    st.rerun()
                else:
                    st.error("Vendor name and TL Capacity are required.")
        with bc2:
            if st.button("Cancel", key="cancel_vendor"):
                st.session_state["show_add_vendor"] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Vendor table
    rows = []
    for v in ev:
        rows.append({
            "Vendor": v["name"],
            "Region": v["region"],
            "Product": v["product"],
            "QAC": v["qac"],
            "Total Cap": f'{v["totalCap"]} MT',
            "TL Cap": f'{v["tlCap"]} MT',
            "Customer": v["customer"],
            "Regular": "✓ Regular" if v["regular"] else "Non-reg",
            "Load %": v["pct"],
            "Balance": v["bal"],
        })
    df = pd.DataFrame(rows)

    def color_pct(val):
        return f"color:{pct_color(val)};font-weight:700"
    def color_bal(val):
        c = "#dc2626" if val < 0 else "#d97706" if val < 10 else "#15803d"
        return f"color:{c};font-weight:700"

    if not df.empty:
        styled = df.style.map(color_pct, subset=["Load %"]).map(color_bal, subset=["Balance"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# AUDIT LOG
# ════════════════════════════════════════════════════════════
elif page == "◎ Audit Log":
    st.markdown("## Audit Log")
    st.markdown('<p style="color:#888;margin-top:-12px">Overload override records — all buyer justifications</p>', unsafe_allow_html=True)

    if not st.session_state.override_log:
        st.markdown("""
        <div class="vlms-card" style="text-align:center;padding:48px">
          <div style="font-size:40px;margin-bottom:12px">◎</div>
          <div style="font-size:16px;font-weight:600;color:#888">No overrides logged yet</div>
          <div style="font-size:13px;color:#bbb;margin-top:6px">Override justifications appear here when a buyer proceeds past an overload warning</div>
        </div>""", unsafe_allow_html=True)
    else:
        log_df = pd.DataFrame(st.session_state.override_log)
        log_df.columns = ["Timestamp","PR ID","Vendor","Buyer","Overload (MT)","Justification"]
        st.dataframe(log_df, use_container_width=True, hide_index=True)

        # Export button
        csv = log_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export Audit Log (CSV)", csv, "override_audit_log.csv", "text/csv")
