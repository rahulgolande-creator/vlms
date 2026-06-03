import streamlit as st
import pandas as pd
import copy
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VendorLoad — Thermax Enviro",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS  ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

html,body,[class*="css"]{font-family:'DM Sans',sans-serif !important;}

/* wipe streamlit chrome */
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:28px 28px 60px !important; max-width:100% !important;}

/* sidebar */
[data-testid="stSidebar"]{background:#1a1917 !important; min-width:210px !important; max-width:210px !important;}
[data-testid="stSidebar"] *{color:#888 !important; font-family:'DM Sans',sans-serif !important;}
[data-testid="stSidebar"] .stRadio > label{display:none;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{gap:2px;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{
    display:flex; align-items:center; gap:10px;
    padding:9px 20px; cursor:pointer; border-radius:0;
    font-size:13px !important; color:#888 !important;
    border-left:2px solid transparent;
    transition:all .15s;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover{color:#ddd !important; background:#222 !important;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]{background:transparent;}
[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div + div,
[data-testid="stSidebar"] input[type="radio"]:checked ~ * {color:#fff !important;}
/* hide radio circles */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] div[data-testid="stMarkdownContainer"]{display:none;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child{display:none !important;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div{margin:0 !important;}
[data-testid="stSidebar"] p{font-size:11px !important; color:#555 !important;}

/* inputs */
input,select,textarea{
    font-family:'DM Sans',sans-serif !important;
    border-radius:8px !important;
    border:1px solid #ddd !important;
    background:#fafaf8 !important;
    font-size:13px !important;
    color:#1a1917 !important;
}
.stTextInput > label,.stSelectbox > label,.stNumberInput > label{
    font-size:10px !important; font-weight:600 !important;
    color:#999 !important; text-transform:uppercase; letter-spacing:.8px;
}
/* buttons */
.stButton > button{
    font-family:'DM Sans',sans-serif !important;
    font-size:13px !important; font-weight:600 !important;
    border-radius:8px !important; transition:all .15s;
    padding:7px 16px !important;
}
.stButton > button[kind="primary"]{
    background:#1a1917 !important; color:#fff !important;
    border:none !important;
}
.stButton > button[kind="secondary"]{
    background:#f0efe9 !important; color:#1a1917 !important;
    border:1px solid #ddd !important;
}
/* app background */
.stApp{background:#f4f3ef !important;}
/* remove default dataframe styling */
[data-testid="stDataFrame"]{border-radius:10px; overflow:hidden;}
.dvn-scroller{border-radius:10px !important;}
/* hide streamlit's colored header bar at top */
[data-testid="stHeader"]{display:none;}
</style>
""", unsafe_allow_html=True)

# ── SEED DATA ─────────────────────────────────────────────────────────────────
BUYERS   = ["SSS – Shantanu","MN – Mohan","AB – Amit","CH – Chetan","RK – Rahul"]
PRODUCTS = ["ABF","PBF","ESP","ALL"]
REGIONS  = ["Pune","Solapur","Nashik","Aurangabad"]
QAC_LIST = ["A","B","C","D"]
STATUSES = ["HOLD","Loaded","RFD","DSP"]

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
    dict(id="PR-001",project="E142300",buyer="SSS – Shantanu",item="AY01 – Bagfilter Casing & Hopper",product="ABF",weightMT=3.92, vendorId=1, status="Loaded",loadingDate="Apr-25",needBy="May-26",poNo="176440",poAmt=137095),
    dict(id="PR-002",project="E142301",buyer="MN – Mohan",    item="ESP Inlet Duct Assembly",         product="ESP",weightMT=8.5,  vendorId=15,status="RFD",   loadingDate="Mar-25",needBy="Jun-25",poNo="176441",poAmt=310000),
    dict(id="PR-003",project="E142302",buyer="AB – Amit",     item="PBF Casing Module",               product="PBF",weightMT=12.0, vendorId=3, status="Loaded",loadingDate="Apr-25",needBy="Aug-25",poNo="176442",poAmt=520000),
    dict(id="PR-004",project="E142303",buyer="CH – Chetan",   item="ABF Outlet Cone Set",             product="ABF",weightMT=2.1,  vendorId=8, status="HOLD",  loadingDate="",      needBy="Jul-25",poNo="176443",poAmt=89000),
    dict(id="PR-005",project="E142304",buyer="RK – Rahul",    item="ESP Frame Structure",             product="ESP",weightMT=18.6, vendorId=5, status="Loaded",loadingDate="Mar-25",needBy="Sep-25",poNo="176444",poAmt=720000),
    dict(id="PR-006",project="E142305",buyer="SSS – Shantanu",item="ABF Hopper Set",                 product="ABF",weightMT=5.4,  vendorId=4, status="Loaded",loadingDate="Apr-25",needBy="Jul-25",poNo="176445",poAmt=198000),
    dict(id="PR-007",project="E142306",buyer="MN – Mohan",    item="PBF Filter Cage Assembly",       product="PBF",weightMT=3.2,  vendorId=7, status="DSP",   loadingDate="Feb-25",needBy="May-25",poNo="176446",poAmt=115000),
    dict(id="PR-008",project="E142307",buyer="AB – Amit",     item="ABF Access Door Panels",         product="ABF",weightMT=1.8,  vendorId=13,status="HOLD",  loadingDate="",      needBy="Aug-25",poNo="176447",poAmt=62000),
]

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k,v in [("vendors",copy.deepcopy(INIT_VENDORS)),("prs",copy.deepcopy(INIT_PRS)),
            ("override_log",[]),("lf_step",1),("lf_data",{}),("lf_submitted",False),
            ("show_add_pr",False),("show_add_vendor",False)]:
    if k not in st.session_state: st.session_state[k]=v

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_pct(v):
    net = v["loaded"]-v["rfdReleased"]
    return round((net/v["tlCap"])*100) if v["tlCap"]>0 else 999

def bal(v): return round(v["tlCap"]-(v["loaded"]-v["rfdReleased"]),1)

def enrich():
    return [{**v,"pct":load_pct(v),"bal":bal(v)} for v in st.session_state.vendors]

def get_vendor(vid):
    return next((v for v in st.session_state.vendors if v["id"]==vid),None)

def pct_col(p):
    return "#dc2626" if p>100 else "#d97706" if p>70 else "#16a34a"

def pct_lbl(p):
    return "OVERLOADED" if p>100 else "HIGH" if p>70 else "NORMAL" if p>30 else "AVAILABLE"

def pct_bg(p):
    return "#fef2f2" if p>100 else "#fffbeb" if p>70 else "#f0fdf4"

# ── HTML COMPONENTS ───────────────────────────────────────────────────────────
def load_bar(pct, height=8):
    capped = min(abs(pct),100)
    col = pct_col(pct)
    return f"""<div style="display:flex;align-items:center;gap:6px;min-width:140px">
  <div style="flex:1;height:{height}px;background:#e5e7eb;border-radius:4px;overflow:hidden">
    <div style="width:{capped}%;height:100%;background:{col};border-radius:4px;transition:width .4s"></div>
  </div>
  <span style="font-size:11px;font-weight:700;color:{col};min-width:36px;text-align:right">{pct}%</span>
</div>"""

STATUS_BG  = {"HOLD":"#fef3c7","Loaded":"#ede9fe","RFD":"#eff6ff","DSP":"#f0fdf4"}
STATUS_COL = {"HOLD":"#b45309","Loaded":"#6d28d9","RFD":"#1d4ed8","DSP":"#15803d"}

def pill(status):
    return f'<span style="background:{STATUS_BG[status]};color:{STATUS_COL[status]};font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;white-space:nowrap">{status}</span>'

def card(content, extra_style=""):
    return f'<div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;padding:20px;margin-bottom:14px;{extra_style}">{content}</div>'

def kpi_card(value, label, color):
    return f"""<div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;
        border-top:3px solid {color};padding:16px 20px;text-align:left">
      <div style="font-size:28px;font-weight:700;color:{color};line-height:1">{value}</div>
      <div style="font-size:11px;color:#888;margin-top:6px">{label}</div>
    </div>"""

def status_flag(p):
    col = pct_col(p); bg = pct_bg(p); lbl = pct_lbl(p)
    return f'<span style="font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;background:{bg};color:{col}">{lbl}</span>'

def product_badge(prod):
    return f'<span style="font-size:11px;background:#ede9fe;color:#6d28d9;padding:2px 8px;border-radius:20px;font-weight:600">{prod}</span>'

def region_badge(reg):
    return f'<span style="font-size:11px;background:#f0efe9;padding:2px 8px;border-radius:20px;color:#555">{reg}</span>'

def section_title(title, subtitle=""):
    sub = f'<p style="font-size:12px;color:#888;margin:2px 0 20px">{subtitle}</p>' if subtitle else ""
    return f'<h2 style="font-size:22px;font-weight:700;letter-spacing:-.4px;color:#1a1917;margin:0 0 4px">{title}</h2>{sub}'

def change_status(pr_id, new_status):
    for i,p in enumerate(st.session_state.prs):
        if p["id"]!=pr_id: continue
        old=p["status"]; wpm=round(p["weightMT"]/6,2)
        if old=="Loaded" and new_status in("RFD","DSP") and p.get("vendorId"):
            for j,v in enumerate(st.session_state.vendors):
                if v["id"]==p["vendorId"]:
                    st.session_state.vendors[j]["rfdReleased"]=round(v["rfdReleased"]+wpm,2); break
        if old=="Loaded" and new_status=="HOLD" and p.get("vendorId"):
            for j,v in enumerate(st.session_state.vendors):
                if v["id"]==p["vendorId"]:
                    st.session_state.vendors[j]["loaded"]=round(v["loaded"]-wpm,2); break
        st.session_state.prs[i]["status"]=new_status
        if new_status=="Loaded": st.session_state.prs[i]["loadingDate"]="May-25"
        break

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 20px 18px;border-bottom:1px solid #2a2826;margin-bottom:16px">
      <div style="font-size:16px;font-weight:700;color:#fff;letter-spacing:-.3px">⚙ VendorLoad</div>
      <div style="font-size:10px;color:#555;text-transform:uppercase;letter-spacing:1px;margin-top:3px">Thermax Enviro</div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard",
        "📋  PR Tracker",
        "⊕  Load Vendor",
        "⊞  Vendor Master",
        "◎  Audit Log"
    ], label_visibility="collapsed")

    ev_side = enrich()
    overloaded_side = [v for v in ev_side if v["bal"]<0]
    if overloaded_side:
        names = "<br>".join([f"• {v['name']}" for v in overloaded_side])
        st.markdown(f"""
        <div style="margin:16px 8px 0;background:#7f1d1d;border-radius:8px;padding:10px 12px">
          <div style="font-size:11px;font-weight:700;color:#fca5a5">⚠ {len(overloaded_side)} overloaded</div>
          <div style="font-size:10px;color:#f87171;margin-top:4px;line-height:1.6">{names}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="position:fixed;bottom:16px;left:0;width:210px;padding:0 20px">
      <div style="font-size:10px;color:#444;text-transform:uppercase;letter-spacing:.5px">Current month: May-25</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Dashboard":
    ev = enrich()
    overloaded = [v for v in ev if v["bal"]<0]
    active_jobs = sum(1 for p in st.session_state.prs if p["status"]=="Loaded")
    healthy = sum(1 for v in ev if v["pct"]<=70)
    high    = sum(1 for v in ev if 70<v["pct"]<=100)

    st.markdown(section_title("Capacity Dashboard","Live vendor loading status — current month (May-25)"), unsafe_allow_html=True)

    # ── KPI row ──
    k1,k2,k3,k4,k5 = st.columns(5)
    for col,val,lbl,color in [
        (k1,len(ev),"Total Vendors","#1a1917"),
        (k2,healthy,"Healthy (≤70%)","#16a34a"),
        (k3,high,"High Load (70–100%)","#d97706"),
        (k4,len(overloaded),"Overloaded (>100%)","#dc2626"),
        (k5,active_jobs,"Active Jobs","#6d28d9"),
    ]:
        col.markdown(kpi_card(val,lbl,color), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Overloaded alert ──
    if overloaded:
        tags = "".join([
            f'<span style="background:#fff;border:1px solid #fca5a5;border-radius:20px;padding:3px 10px;font-size:12px;color:#991b1b;font-weight:600;margin:2px">'
            f'{v["name"]} &nbsp; {v["pct"]}% &nbsp; ({v["bal"]} MT)</span>'
            for v in overloaded])
        st.markdown(f"""
        <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;
             padding:12px 16px;margin-bottom:16px;display:flex;gap:12px;align-items:flex-start">
          <span style="font-size:20px">⚠️</span>
          <div>
            <div style="font-weight:700;color:#991b1b;font-size:13px;margin-bottom:6px">
              Overloaded vendors — immediate attention required</div>
            <div style="display:flex;flex-wrap:wrap;gap:4px">{tags}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Filters ──
    st.markdown('<p style="font-size:14px;font-weight:700;margin:0 0 10px">Vendor Loading — All Vendors</p>', unsafe_allow_html=True)
    fc1,fc2,fc3 = st.columns([1.5,1.5,3])
    with fc1: f_region  = st.selectbox("Region",  ["ALL"]+REGIONS,  key="d_reg")
    with fc2: f_product = st.selectbox("Product", ["ALL"]+PRODUCTS, key="d_prod")
    with fc3: f_search  = st.text_input("Search vendor", placeholder="Type vendor name…", key="d_search")

    filtered = sorted([
        v for v in ev
        if (f_region=="ALL" or v["region"]==f_region)
        and (f_product=="ALL" or v["product"] in (f_product,"ALL"))
        and f_search.lower() in v["name"].lower()
    ], key=lambda v: v["pct"], reverse=True)

    # ── Vendor table ──
    th_style = "font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#999;padding:8px 12px;border-bottom:1px solid #f0efe9;background:#fff;white-space:nowrap"
    td_style = "font-size:12px;padding:10px 12px;border-bottom:1px solid #f5f4f0;vertical-align:middle"

    rows_html = ""
    for v in filtered:
        row_bg = "#fff5f5" if v["pct"]>100 else "#fffdf0" if v["pct"]>70 else "#fff"
        bal_col = "#dc2626" if v["bal"]<0 else "#d97706" if v["bal"]<10 else "#15803d"
        bal_str = f'{"+" if v["bal"]>0 else ""}{v["bal"]} MT'
        net_loaded = round(v["loaded"]-v["rfdReleased"],1)
        rfd_str = f'+{v["rfdReleased"]} MT' if v["rfdReleased"]>0 else "—"
        name_col = "#991b1b" if v["pct"]>100 else "#1a1917"

        rows_html += f"""
        <tr style="background:{row_bg}">
          <td style="{td_style};font-weight:600;color:{name_col}">{v["name"]}</td>
          <td style="{td_style}">{region_badge(v["region"])}</td>
          <td style="{td_style}">{product_badge(v["product"])}</td>
          <td style="{td_style};min-width:160px">{load_bar(v["pct"])}</td>
          <td style="{td_style}">{v["tlCap"]} MT</td>
          <td style="{td_style}">{net_loaded} MT</td>
          <td style="{td_style};color:#16a34a">{rfd_str}</td>
          <td style="{td_style};font-weight:700;color:{bal_col}">{bal_str}</td>
          <td style="{td_style}">{status_flag(v["pct"])}</td>
        </tr>"""

    table_html = f"""
    <div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;overflow:hidden;margin-bottom:20px">
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse">
          <thead><tr>
            {''.join(f'<th style="{th_style}">{h}</th>' for h in
              ["Vendor","Region","Product","Load %","TL Cap","Loaded","RFD Released","Balance","Status"])}
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>"""
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Top / Bottom ──
    top5 = sorted(ev, key=lambda v:v["pct"], reverse=True)[:5]
    bot5 = sorted(ev, key=lambda v:v["pct"])[:5]

    rc1,rc2 = st.columns(2)
    for col, title, lst in [(rc1,"🔴 Top 5 — Most Loaded",top5),(rc2,"🟢 Bottom 5 — Most Available",bot5)]:
        rows = ""
        for i,v in enumerate(lst):
            rows += f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
              <span style="font-size:11px;color:#bbb;width:16px;font-weight:700">{i+1}</span>
              <span style="flex:1;font-size:12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{v["name"]}</span>
              <div style="width:120px">{load_bar(v["pct"],5)}</div>
            </div>"""
        col.markdown(card(f'<div style="font-size:13px;font-weight:700;margin-bottom:14px">{title}</div>{rows}'), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PR TRACKER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋  PR Tracker":
    hc1,hc2 = st.columns([6,1])
    with hc1: st.markdown(section_title("PR Tracker"), unsafe_allow_html=True)
    with hc2:
        if st.button("+ Add PR", type="primary", use_container_width=True): st.session_state.show_add_pr=True

    fc1,fc2,fc3 = st.columns(3)
    with fc1: f_buyer   = st.selectbox("Buyer",   ["ALL"]+BUYERS,   key="pr_b")
    with fc2: f_status  = st.selectbox("Status",  ["ALL"]+STATUSES, key="pr_s")
    with fc3: f_product = st.selectbox("Product", ["ALL"]+PRODUCTS, key="pr_p")

    # Add PR form
    if st.session_state.show_add_pr:
        st.markdown('<div style="background:#fff;border-radius:12px;border:2px solid #e8c547;padding:20px;margin-bottom:16px">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px;font-weight:700;margin-bottom:14px">New Purchase Requisition</p>', unsafe_allow_html=True)
        a1,a2,a3,a4 = st.columns(4)
        with a1:
            np_proj   = st.text_input("Project No *",    key="np_proj")
            np_weight = st.number_input("Weight (MT) *", min_value=0.0, step=0.1, key="np_wt")
        with a2:
            np_item   = st.text_input("Item Description *", key="np_item")
            np_po     = st.text_input("PO Number",           key="np_po")
        with a3:
            np_buyer  = st.selectbox("Buyer *", BUYERS, key="np_buyer")
            np_needby = st.text_input("Need-By (Mon-YY)",    key="np_nb")
        with a4:
            np_prod   = st.selectbox("Product *", [p for p in PRODUCTS if p!="ALL"], key="np_prod")
            np_amt    = st.number_input("PO Amount (₹)", min_value=0, step=1000, key="np_amt")
        b1,b2,_= st.columns([1,1,5])
        with b1:
            if st.button("Save PR", type="primary"):
                if np_proj and np_item:
                    nid=f"PR-{len(st.session_state.prs)+1:03d}"
                    st.session_state.prs.append(dict(id=nid,project=np_proj,buyer=np_buyer,
                        item=np_item,product=np_prod,weightMT=np_weight,vendorId=None,
                        status="HOLD",loadingDate="",needBy=np_needby,poNo=np_po,poAmt=np_amt))
                    st.session_state.show_add_pr=False
                    st.rerun()
                else: st.error("Project No and Item Description required.")
        with b2:
            if st.button("Cancel"): st.session_state.show_add_pr=False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # PR table
    filtered_prs=[p for p in st.session_state.prs
                  if (f_buyer=="ALL" or p["buyer"]==f_buyer)
                  and (f_status=="ALL" or p["status"]==f_status)
                  and (f_product=="ALL" or p["product"]==f_product)]

    st.markdown(f'<p style="color:#888;font-size:12px;margin-bottom:8px">{len(filtered_prs)} purchase requisitions · click status button to change</p>', unsafe_allow_html=True)

    th = "font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#999;padding:8px 12px;border-bottom:1px solid #f0efe9;white-space:nowrap;background:#fff"
    td = "font-size:12px;padding:10px 12px;border-bottom:1px solid #f5f4f0;vertical-align:middle"

    header_html = "".join(f'<th style="{th}">{h}</th>' for h in
        ["PR ID","Project","Item","Product","Weight","Vendor","Loading Date","Need By","Status"])
    rows_html = ""
    for p in filtered_prs:
        v = get_vendor(p.get("vendorId"))
        vname = v["name"] if v else '<span style="color:#ddd">Unassigned</span>'
        item_short = p["item"][:34]+("…" if len(p["item"])>34 else "")
        rows_html += f"""<tr>
          <td style="{td};font-family:monospace;font-size:11px;color:#888">{p["id"]}</td>
          <td style="{td};font-weight:600">{p["project"]}</td>
          <td style="{td};max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{item_short}</td>
          <td style="{td}">{product_badge(p["product"])}</td>
          <td style="{td}">{p["weightMT"]} MT</td>
          <td style="{td};font-size:11px;color:#555">{vname}</td>
          <td style="{td};font-size:11px;color:#888">{p["loadingDate"] or "—"}</td>
          <td style="{td};font-size:11px;color:#888">{p["needBy"]}</td>
          <td style="{td}">{pill(p["status"])}</td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;overflow:hidden;margin-bottom:4px">
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse">
          <thead><tr>{header_html}</tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>""", unsafe_allow_html=True)

    # Status buttons below the table — one row per PR
    TRANS = {"HOLD":["Loaded"],"Loaded":["HOLD","RFD"],"RFD":["DSP"],"DSP":[]}
    for p in filtered_prs:
        nexts = TRANS.get(p["status"],[])
        if not nexts: continue
        cols = st.columns([2]+[1]*len(nexts)+[8])
        cols[0].markdown(f'<span style="font-size:11px;color:#888;line-height:32px">{p["id"]}</span>', unsafe_allow_html=True)
        for i,ns in enumerate(nexts):
            with cols[i+1]:
                if st.button(f"→ {ns}", key=f"st_{p['id']}_{ns}",
                             use_container_width=True):
                    change_status(p["id"],ns); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# LOADING FORM
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⊕  Load Vendor":
    ev = enrich()
    top5 = sorted(ev, key=lambda v:v["pct"], reverse=True)[:5]
    bot5 = sorted(ev, key=lambda v:v["pct"])[:5]

    st.markdown(section_title("Vendor Loading Form","Assign a PR to a vendor · Live capacity shown"), unsafe_allow_html=True)

    # Step indicator
    step = st.session_state.lf_step
    steps_html = ""
    for s,lbl in [(1,"PR Details"),(2,"Select Vendor"),(3,"Review & Submit")]:
        active = step>=s
        bg = "#1a1917" if active else "#e5e7eb"
        col_txt = "#fff" if active else "#999"
        line_bg = "#1a1917" if step>s else "#e5e7eb"
        steps_html += f'<div style="display:flex;align-items:center;gap:4px">'
        steps_html += f'<div style="width:28px;height:28px;border-radius:50%;background:{bg};color:{col_txt};display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700">{s}</div>'
        if s<3: steps_html += f'<div style="width:24px;height:2px;background:{line_bg}"></div>'
        steps_html += f'</div>'
    label = ["PR Details","Select Vendor","Review & Submit"][step-1]
    st.markdown(f'<div style="display:flex;align-items:center;gap:0;margin-bottom:20px">{steps_html}<span style="font-size:12px;color:#888;margin-left:10px">{label}</span></div>', unsafe_allow_html=True)

    # ── Submitted ──
    if st.session_state.lf_submitted:
        st.markdown(card("""
        <div style="text-align:center;padding:32px 0">
          <div style="font-size:48px;margin-bottom:12px">✅</div>
          <div style="font-size:20px;font-weight:700;margin-bottom:8px">Loading confirmed!</div>
          <div style="color:#888;font-size:14px">Vendor capacity updated. PR status set to Loaded.</div>
        </div>"""), unsafe_allow_html=True)
        if st.button("Load another PR", type="primary"):
            st.session_state.lf_step=1; st.session_state.lf_data={}
            st.session_state.lf_submitted=False; st.rerun()

    # ── Step 1 ──
    elif step==1:
        st.markdown('<div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;padding:20px">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px;font-weight:700;margin-bottom:16px">PR Details</p>', unsafe_allow_html=True)
        d = st.session_state.lf_data
        c1,c2 = st.columns(2)
        with c1:
            proj    = st.text_input("Project Number *",  value=d.get("project",""),  key="lf_proj")
            item    = st.text_input("Item Description *", value=d.get("item",""),    key="lf_item")
            po_no   = st.text_input("PO Number",          value=d.get("poNo",""),    key="lf_po")
            need_by = st.text_input("Need-By (Mon-YY)",   value=d.get("needBy",""),  key="lf_nb")
        with c2:
            buyers_list=[""]+ BUYERS
            bidx=buyers_list.index(d.get("buyer","")) if d.get("buyer","") in buyers_list else 0
            buyer=st.selectbox("Buyer *", buyers_list, index=bidx, key="lf_buyer")
            prods=[p for p in PRODUCTS if p!="ALL"]
            pidx=prods.index(d.get("product","ABF")) if d.get("product","ABF") in prods else 0
            product=st.selectbox("Product Type *", prods, index=pidx, key="lf_prod")
            weight=st.number_input("Total Weight (MT) *", min_value=0.0, step=0.1,
                                   value=float(d.get("weightMT",0) or 0), key="lf_wt")
        if weight>0:
            st.markdown(f'<div style="background:#f8f7f3;border-radius:8px;padding:10px 14px;font-size:12px;color:#888;margin:10px 0">Monthly loading weight = Total weight ÷ 6 = <strong style="color:#1a1917">{weight/6:.2f} MT/month</strong></div>', unsafe_allow_html=True)
        can1 = bool(proj and buyer and weight>0 and item)
        if st.button("Next: Select Vendor →", type="primary", disabled=not can1, key="lf_n1"):
            st.session_state.lf_data.update(dict(project=proj,buyer=buyer,item=item,
                product=product,weightMT=weight,needBy=need_by,poNo=po_no))
            st.session_state.lf_step=2; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Step 2 ──
    elif step==2:
        d   = st.session_state.lf_data
        weight = float(d.get("weightMT",0))
        wpm    = round(weight/6,2)
        product= d.get("product","ABF")
        lf_vendors = sorted([v for v in ev if v["product"] in (product,"ALL")], key=lambda v:v["pct"])

        # Vendor table
        th2="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#999;padding:8px 12px;border-bottom:1px solid #f0efe9;background:#fff;white-space:nowrap"
        td2="font-size:12px;padding:10px 12px;border-bottom:1px solid #f5f4f0;vertical-align:middle"
        sel_id = d.get("selectedVendorId")

        trows=""
        for v in lf_vendors:
            new_bal=round(v["bal"]-wpm,1)
            over=new_bal<0
            sel=(sel_id==v["id"])
            row_bg="#fefde8" if sel else "#fff5f5" if over else "#fff"
            border_left=f"border-left:3px solid #e8c547" if sel else "border-left:3px solid transparent"
            name_col="#991b1b" if over else "#1a1917"
            bal_col="#dc2626" if new_bal<0 else "#d97706" if new_bal<5 else "#15803d"
            bal_str=f'{"+" if new_bal>0 else ""}{new_bal} MT {"⚠" if over else ""}'
            trows+=f"""<tr style="background:{row_bg};{border_left};cursor:pointer">
              <td style="{td2};font-weight:600;color:{name_col}">{v["name"]}</td>
              <td style="{td2}">{region_badge(v["region"])}</td>
              <td style="{td2};min-width:160px">{load_bar(v["pct"])}</td>
              <td style="{td2}">{v["tlCap"]} MT</td>
              <td style="{td2};font-weight:700;color:{bal_col}">{bal_str}</td>
              <td style="{td2}"><span style="font-size:12px;font-weight:700;background:#f0efe9;padding:2px 8px;border-radius:20px">{v["qac"]}</span></td>
              <td style="{td2}"><span style="font-size:11px;color:{'#15803d' if v['regular'] else '#888'}">{'✓ Regular' if v['regular'] else 'Non-reg'}</span></td>
            </tr>"""

        st.markdown(f"""
        <div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;overflow:hidden;margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px 0">
            <span style="font-size:14px;font-weight:700">Select Vendor — {product} · All Regions</span>
            <span style="font-size:12px;color:#888">Adding <strong>{wpm} MT/mo</strong> to vendor balance</span>
          </div>
          <div style="overflow-x:auto;padding:0 0 4px">
            <table style="width:100%;border-collapse:collapse">
              <thead><tr>
                {''.join(f'<th style="{th2}">{h}</th>' for h in ["Vendor","Region","Load %","TL Cap","Balance After","QAC","Regular"])}
              </tr></thead>
              <tbody>{trows}</tbody>
            </table>
          </div>
          <p style="font-size:11px;color:#aaa;padding:8px 16px;margin:0">👆 Select a vendor below using the dropdown</p>
        </div>""", unsafe_allow_html=True)

        # Vendor selector (Streamlit widget)
        vendor_names = ["— select —"] + [v["name"] for v in lf_vendors]
        cur_name = next((v["name"] for v in lf_vendors if v["id"]==sel_id), "— select —")
        cur_idx  = vendor_names.index(cur_name) if cur_name in vendor_names else 0
        chosen = st.selectbox("Select vendor to assign:", vendor_names, index=cur_idx, key="lf_vsel")
        if chosen != "— select —":
            chosen_v = next((v for v in lf_vendors if v["name"]==chosen), None)
            if chosen_v:
                new_bal = round(chosen_v["bal"]-wpm,1)
                over = new_bal<0
                if chosen_v["id"] != sel_id:
                    d["selectedVendorId"]=chosen_v["id"]
                    d["showWarn"]=over
                    d["justification"]=""
                    st.session_state.lf_data=d
                    st.rerun()

        # Top/Bottom panels
        tc1,tc2=st.columns(2)
        for col,title,lst in [(tc1,"🔴 Top loaded — steer away",top5),(tc2,"🟢 Bottom loaded — prefer these",bot5)]:
            rr=""
            for i,v in enumerate(lst):
                rr+=f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px"><span style="font-size:10px;color:#ccc;width:14px">{i+1}</span><span style="font-size:11px;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{v["name"]}</span><div style="width:100px">{load_bar(v["pct"],4)}</div></div>'
            col.markdown(card(f'<div style="font-size:12px;font-weight:700;margin-bottom:10px">{title}</div>{rr}'), unsafe_allow_html=True)

        # Overload warning
        show_warn = d.get("showWarn",False)
        if show_warn and sel_id:
            sel_v=next((v for v in ev if v["id"]==sel_id),None)
            if sel_v:
                new_bal=round(sel_v["bal"]-wpm,1)
                st.markdown(f"""
                <div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:10px;padding:14px 16px;margin:10px 0">
                  <div style="display:flex;gap:10px">
                    <span style="font-size:20px">⚠️</span>
                    <div>
                      <div style="font-weight:700;color:#92400e;font-size:13px;margin-bottom:4px">Capacity warning — {sel_v["name"]}</div>
                      <div style="font-size:12px;color:#78350f;line-height:1.6">
                        Adding {wpm} MT will make balance <strong>{new_bal} MT</strong>.
                        TL capacity: {sel_v["tlCap"]} MT/mo.
                        A justification is required to proceed.
                      </div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
                just=st.text_area("Justification for override (required — min 20 characters)",
                    value=d.get("justification",""),
                    placeholder="e.g. Vendor confirmed availability via phone on 29-May-25, SCM head approved…",
                    height=80, key="lf_just")
                st.session_state.lf_data["justification"]=just
        else:
            just=d.get("justification","")

        justification=st.session_state.lf_data.get("justification","")
        can2 = bool(sel_id) and (not show_warn or len(justification)>=20)

        b1,b2,_=st.columns([1,1.5,6])
        with b1:
            if st.button("← Back", key="lf_b2"): st.session_state.lf_step=1; st.rerun()
        with b2:
            if st.button("Next: Review →", type="primary", disabled=not can2, key="lf_n2"):
                st.session_state.lf_step=3; st.rerun()

    # ── Step 3 ──
    elif step==3:
        d      = st.session_state.lf_data
        weight = float(d.get("weightMT",0))
        wpm    = round(weight/6,2)
        sel_id = d.get("selectedVendorId")
        sel_v  = next((v for v in ev if v["id"]==sel_id),None)

        if sel_v:
            st.markdown('<div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;padding:20px">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:14px;font-weight:700;margin-bottom:16px">Review & Confirm</p>', unsafe_allow_html=True)

            fields=[("Project",d.get("project","")),("Buyer",d.get("buyer","")),
                    ("Item",d.get("item","")),("Product",d.get("product","")),
                    ("Weight",f"{weight} MT"),("Monthly Load",f"{wpm} MT/mo"),
                    ("Need-By",d.get("needBy","")),("PO No",d.get("poNo",""))]
            fc1,fc2=st.columns(2)
            for i,(lbl,val) in enumerate(fields):
                html=f'<div style="background:#fafaf8;border:1px solid #eee;border-radius:8px;padding:10px 14px;margin-bottom:8px"><div style="font-size:10px;color:#999;text-transform:uppercase;letter-spacing:.8px">{lbl}</div><div style="font-size:13px;font-weight:600">{val or "—"}</div></div>'
                (fc1 if i%2==0 else fc2).markdown(html, unsafe_allow_html=True)

            new_bal=round(sel_v["bal"]-wpm,1)
            banner_bg="#fef3c7" if new_bal<0 else "#f0fdf4"
            banner_border="#fbbf24" if new_bal<0 else "#86efac"
            bal_col="#dc2626" if new_bal<0 else "#15803d"
            st.markdown(f"""
            <div style="background:{banner_bg};border:1px solid {banner_border};border-radius:10px;padding:12px 16px;margin:10px 0">
              <div style="font-size:13px;font-weight:700;margin-bottom:6px">Vendor: {sel_v["name"]}</div>
              <div style="font-size:12px;display:flex;gap:24px">
                <span>Current load: <strong>{sel_v["pct"]}%</strong></span>
                <span>TL Cap: <strong>{sel_v["tlCap"]} MT</strong></span>
                <span>Balance after: <strong style="color:{bal_col}">{"+" if new_bal>0 else ""}{new_bal} MT</strong></span>
              </div>
            </div>""", unsafe_allow_html=True)

            if d.get("showWarn") and d.get("justification"):
                st.markdown(f'<div style="background:#fff7ed;border:1px solid #fdba74;border-radius:8px;padding:10px 14px;margin:8px 0;font-size:12px;color:#7c2d12"><strong>Override justification:</strong> {d["justification"]}</div>', unsafe_allow_html=True)

            warn_note = "· Override logged to audit trail" if d.get("showWarn") else ""
            st.markdown(f'<div style="background:#f8f7f3;border-radius:8px;padding:10px 14px;font-size:12px;color:#888;margin:10px 0">On confirm: PR created (status: Loaded) · Vendor balance updated {warn_note}</div>', unsafe_allow_html=True)

            b1,b2,_=st.columns([1,1.5,6])
            with b1:
                if st.button("← Back", key="lf_b3"): st.session_state.lf_step=2; st.rerun()
            with b2:
                if st.button("✓ Confirm Loading", type="primary", key="lf_confirm"):
                    nid=f"PR-{len(st.session_state.prs)+1:03d}"
                    wpm2=round(weight/6,2)
                    st.session_state.prs.append(dict(id=nid,project=d["project"],buyer=d["buyer"],
                        item=d["item"],product=d["product"],weightMT=weight,vendorId=sel_id,
                        status="Loaded",loadingDate="May-25",needBy=d.get("needBy",""),
                        poNo=d.get("poNo",""),poAmt=0))
                    for i,v in enumerate(st.session_state.vendors):
                        if v["id"]==sel_id:
                            st.session_state.vendors[i]["loaded"]=round(v["loaded"]+wpm2,2); break
                    if d.get("showWarn") and d.get("justification"):
                        st.session_state.override_log.append(dict(
                            ts=datetime.now().strftime("%d %b %Y %H:%M"),
                            pr=nid, vendor=sel_v["name"], buyer=d["buyer"],
                            overloadMT=round(-sel_v["bal"]+wpm2,1),
                            justification=d["justification"]))
                    st.session_state.lf_submitted=True
                    st.session_state.lf_step=1
                    st.session_state.lf_data={}
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VENDOR MASTER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⊞  Vendor Master":
    ev = enrich()
    hc1,hc2=st.columns([6,1])
    with hc1: st.markdown(section_title("Vendor Master",f"{len(ev)} vendors · TL capacity, QAC, region, product type"), unsafe_allow_html=True)
    with hc2:
        if st.button("+ Add Vendor", type="primary", use_container_width=True): st.session_state.show_add_vendor=True

    if st.session_state.show_add_vendor:
        st.markdown('<div style="background:#fff;border-radius:12px;border:2px solid #e8c547;padding:20px;margin-bottom:16px">', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14px;font-weight:700;margin-bottom:14px">New Vendor</p>', unsafe_allow_html=True)
        v1,v2,v3,v4=st.columns(4)
        with v1:
            nv_name   = st.text_input("Vendor Name *",              key="nv_name")
            nv_total  = st.number_input("Total Capacity (MT/mo) *", min_value=0.0, step=5.0, key="nv_tc")
        with v2:
            nv_region = st.selectbox("Region",   REGIONS,   key="nv_reg")
            nv_tl     = st.number_input("TL Capacity (MT/mo) *", min_value=0.0, step=5.0, key="nv_tl")
        with v3:
            nv_prod   = st.selectbox("Product Type", PRODUCTS, key="nv_prod")
            nv_cust   = st.selectbox("Customer Mix", ["T","T+O"], key="nv_cust")
        with v4:
            nv_qac    = st.selectbox("QAC Rating", QAC_LIST, index=1, key="nv_qac")
            nv_reg    = st.selectbox("Regular Vendor?", ["Yes – Regular","No – Non-regular"], key="nv_regu")
        b1,b2,_=st.columns([1,1,6])
        with b1:
            if st.button("Save Vendor", type="primary", key="sv_v"):
                if nv_name and nv_tl>0:
                    new_vid=max(v["id"] for v in st.session_state.vendors)+1
                    st.session_state.vendors.append(dict(id=new_vid,name=nv_name,region=nv_region,
                        product=nv_prod,qac=nv_qac,totalCap=nv_total,tlCap=nv_tl,loaded=0,
                        rfdReleased=0,customer=nv_cust,regular=(nv_reg=="Yes – Regular")))
                    st.session_state.show_add_vendor=False; st.rerun()
                else: st.error("Vendor name and TL Capacity required.")
        with b2:
            if st.button("Cancel", key="cv_v"): st.session_state.show_add_vendor=False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Vendor table
    th3="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#999;padding:8px 12px;border-bottom:1px solid #f0efe9;background:#fff;white-space:nowrap"
    td3="font-size:12px;padding:10px 12px;border-bottom:1px solid #f5f4f0;vertical-align:middle"
    vrows=""
    for v in ev:
        bal_col="#dc2626" if v["bal"]<0 else "#d97706" if v["bal"]<10 else "#15803d"
        bal_str=f'{"+" if v["bal"]>0 else ""}{v["bal"]} MT'
        vrows+=f"""<tr>
          <td style="{td3};font-weight:600">{v["name"]}</td>
          <td style="{td3}">{region_badge(v["region"])}</td>
          <td style="{td3}">{product_badge(v["product"])}</td>
          <td style="{td3}"><span style="font-size:12px;font-weight:700;background:#f0fdf4;color:#15803d;padding:2px 8px;border-radius:20px">{v["qac"]}</span></td>
          <td style="{td3}">{v["totalCap"]} MT</td>
          <td style="{td3};font-weight:600">{v["tlCap"]} MT</td>
          <td style="{td3};font-size:11px">{v["customer"]}</td>
          <td style="{td3}"><span style="font-size:11px;color:{'#15803d' if v['regular'] else '#999'}">{'✓ Regular' if v['regular'] else 'Non-reg'}</span></td>
          <td style="{td3};min-width:160px">{load_bar(v["pct"])}</td>
          <td style="{td3};font-weight:700;color:{bal_col}">{bal_str}</td>
        </tr>"""

    st.markdown(f"""
    <div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;overflow:hidden">
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse">
          <thead><tr>
            {''.join(f'<th style="{th3}">{h}</th>' for h in ["Vendor","Region","Product","QAC","Total Cap","TL Cap","Customer","Regular","Current Load","Balance"])}
          </tr></thead>
          <tbody>{vrows}</tbody>
        </table>
      </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "◎  Audit Log":
    st.markdown(section_title("Audit Log","Overload override records — all buyer justifications"), unsafe_allow_html=True)

    if not st.session_state.override_log:
        st.markdown(card("""
        <div style="text-align:center;padding:32px 0">
          <div style="font-size:40px;margin-bottom:12px;color:#ddd">◎</div>
          <div style="font-size:16px;font-weight:600;color:#888">No overrides logged yet</div>
          <div style="font-size:13px;color:#bbb;margin-top:6px">Override justifications appear here when a buyer proceeds past an overload warning</div>
        </div>"""), unsafe_allow_html=True)
    else:
        th4="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;color:#999;padding:8px 12px;border-bottom:1px solid #f0efe9;background:#fff;white-space:nowrap"
        td4="font-size:12px;padding:10px 12px;border-bottom:1px solid #f5f4f0;vertical-align:middle"
        lrows=""
        for r in st.session_state.override_log:
            lrows+=f"""<tr>
              <td style="{td4};font-family:monospace;font-size:11px;color:#888;white-space:nowrap">{r["ts"]}</td>
              <td style="{td4};font-family:monospace;font-size:11px;color:#888">{r["pr"]}</td>
              <td style="{td4};font-weight:600;color:#991b1b">{r["vendor"]}</td>
              <td style="{td4}">{r["buyer"]}</td>
              <td style="{td4};font-weight:700;color:#dc2626">{r["overloadMT"]} MT</td>
              <td style="{td4};font-size:12px;color:#555;max-width:300px">{r["justification"]}</td>
            </tr>"""

        st.markdown(f"""
        <div style="background:#fff;border-radius:12px;border:1px solid #e8e6e0;overflow:hidden;margin-bottom:14px">
          <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse">
              <thead><tr>
                {''.join(f'<th style="{th4}">{h}</th>' for h in ["Timestamp","PR ID","Vendor","Buyer","Overload (MT)","Justification"])}
              </tr></thead>
              <tbody>{lrows}</tbody>
            </table>
          </div>
        </div>""", unsafe_allow_html=True)

        log_df=pd.DataFrame(st.session_state.override_log)
        log_df.columns=["Timestamp","PR ID","Vendor","Buyer","Overload (MT)","Justification"]
        csv=log_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export Audit Log (CSV)", csv, "override_audit_log.csv","text/csv")
