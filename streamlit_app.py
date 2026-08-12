"""
streamlit_app.py  –  AgroScan  |  Premium Streamlit Frontend
Talks to the Flask backend running on http://localhost:5000
"""

import streamlit as st
import requests
import base64
import io
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────
API = "http://localhost:5000"

st.set_page_config(
    page_title="AgroScan",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
for key, val in {
    "logged_in": False,
    "user": None,
    "page": "scan",
    "last_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Shared request helper ─────────────────────────────────────────────────────
_session = requests.Session()

def api(method: str, path: str, **kwargs):
    try:
        return getattr(_session, method)(f"{API}{path}", timeout=15, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot reach Flask backend. Make sure `app.py` is running on port 5000.")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS  –  injected directly at module level (must be after set_page_config)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>""", unsafe_allow_html=True)
st.markdown("""<style>
    /* ═══ RESET & BASE ═══ */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Inter', sans-serif !important;
        background: #0d1f0f !important;
    }
    [data-testid="stMainBlockContainer"] {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    * { box-sizing: border-box; }

    /* ═══ SIDEBAR ═══ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071209 0%, #0f2d12 40%, #163d1a 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] > div { padding-top: 0 !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div { color: #c8e6c9 !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e8f5e9 !important;
        border-radius: 12px !important;
        width: 100% !important;
        padding: 10px 16px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(76,175,80,0.25) !important;
        border-color: rgba(76,175,80,0.5) !important;
        transform: translateX(4px) !important;
    }

    /* ═══ HEADINGS ═══ */
    h1, h2, h3 { font-family: 'Inter', sans-serif !important; color: #e8f5e9 !important; }

    /* ═══ INPUTS ═══ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1.5px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        color: #e8f5e9 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        padding: 12px 16px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4caf50 !important;
        box-shadow: 0 0 0 3px rgba(76,175,80,0.15) !important;
    }
    .stTextInput label, .stTextArea label {
        color: #a5d6a7 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
    }

    /* ═══ BUTTONS ═══ */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #2e7d32, #43a047) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 28px !important;
        font-family: 'Inter', sans-serif !important;
        box-shadow: 0 4px 20px rgba(76,175,80,0.4) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.4px !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(76,175,80,0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.07) !important;
        border: 1.5px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #c8e6c9 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ═══ TABS ═══ */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 14px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        color: #81c784 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        font-family: 'Inter', sans-serif !important;
        padding: 8px 18px !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2e7d32, #43a047) !important;
        color: white !important;
        box-shadow: 0 3px 12px rgba(76,175,80,0.35) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 16px !important;
    }

    /* ═══ FILE UPLOADER ═══ */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03) !important;
        border: 2px dashed rgba(76,175,80,0.35) !important;
        border-radius: 16px !important;
        padding: 8px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(76,175,80,0.65) !important;
    }
    [data-testid="stFileUploader"] label { color: #a5d6a7 !important; }
    [data-testid="stFileUploaderDropzone"] > div { color: #81c784 !important; }

    /* ═══ CAMERA INPUT ═══ */
    [data-testid="stCameraInput"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 2px dashed rgba(76,175,80,0.35) !important;
    }

    /* ═══ EXPANDER ═══ */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stExpander"] summary {
        color: #c8e6c9 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* ═══ RADIO ═══ */
    .stRadio > div { gap: 8px !important; }
    .stRadio label { color: #a5d6a7 !important; font-size: 0.88rem !important; }

    /* ═══ ALERTS ═══ */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ═══ DIVIDER ═══ */
    hr { border-color: rgba(255,255,255,0.08) !important; }

    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(76,175,80,0.3); border-radius: 3px; }

    /* ═══ HIDE BRANDING ═══ */
    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stDecoration"] { display: none !important; }
    </style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HTML COMPONENT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def glass_card(content_html: str, extra_style: str = "") -> str:
    return f"""
    <div style="
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        {extra_style}
    ">{content_html}</div>"""


def stat_card(icon: str, value: str, label: str, color: str = "#4caf50") -> str:
    return f"""
    <div style="
        flex:1; min-width:130px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 18px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    ">
        <div style="font-size:1.8rem;margin-bottom:6px">{icon}</div>
        <div style="font-size:2rem;font-weight:800;color:{color};
                    font-family:'Inter',sans-serif;line-height:1">{value}</div>
        <div style="font-size:0.75rem;color:#81c784;margin-top:6px;
                    text-transform:uppercase;letter-spacing:1px;font-weight:600">{label}</div>
    </div>"""


def conf_bar(confidence: float, is_healthy: bool) -> str:
    color = "linear-gradient(90deg,#66bb6a,#2e7d32)" if is_healthy \
            else "linear-gradient(90deg,#ef9a9a,#c62828)"
    text_color = "#66bb6a" if is_healthy else "#ef5350"
    return f"""
    <div style="margin:14px 0 8px">
        <div style="display:flex;justify-content:space-between;
                    font-size:0.78rem;color:#90a4ae;margin-bottom:8px;font-weight:500">
            <span>Detection Confidence</span>
            <span style="color:{text_color};font-weight:700;font-size:0.92rem">{confidence}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.08);border-radius:20px;
                    height:10px;overflow:hidden;">
            <div style="width:{confidence}%;height:100%;border-radius:20px;
                        background:{color};
                        box-shadow:0 0 10px rgba(76,175,80,0.4);
                        transition:width 0.8s ease"></div>
        </div>
    </div>"""


def badge(is_healthy: bool) -> str:
    if is_healthy:
        return """<span style="background:rgba(76,175,80,0.2);color:#66bb6a;
                               border:1px solid rgba(76,175,80,0.4);padding:4px 14px;
                               border-radius:20px;font-weight:700;font-size:0.78rem;
                               letter-spacing:0.5px">✅ HEALTHY</span>"""
    return """<span style="background:rgba(239,83,80,0.18);color:#ef9a9a;
                           border:1px solid rgba(239,83,80,0.35);padding:4px 14px;
                           border-radius:20px;font-weight:700;font-size:0.78rem;
                           letter-spacing:0.5px">⚠️ DISEASED</span>"""

# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_auth():
    # Full-page gradient backdrop
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(ellipse at 20% 50%, #0d2e0f 0%, #071209 50%, #050e06 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 2.2, 1])
    with col_mid:
        # ── Brand header ────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center;padding:40px 0 8px">
            <div style="display:inline-flex;align-items:center;justify-content:center;
                        width:80px;height:80px;border-radius:24px;font-size:2.5rem;
                        background:linear-gradient(135deg,#1b5e20,#43a047);
                        box-shadow:0 8px 32px rgba(76,175,80,0.45);margin-bottom:16px">
                🌿
            </div>
            <h1 style="font-size:2.6rem;font-weight:800;
                       background:linear-gradient(135deg,#81c784,#c8e6c9);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       margin:0 0 6px;font-family:'Inter',sans-serif">AgroScan</h1>
            <p style="color:#66a068;font-size:1rem;font-weight:400;margin:0 0 36px">
                AI-powered plant disease detection
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Feature pills row ────────────────────────────────────────────
        st.markdown("""
        <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:32px">
            <div style="background:rgba(76,175,80,0.12);border:1px solid rgba(76,175,80,0.25);
                        border-radius:20px;padding:6px 14px;font-size:0.78rem;color:#81c784;font-weight:600">
                📷 Instant Detection
            </div>
            <div style="background:rgba(76,175,80,0.12);border:1px solid rgba(76,175,80,0.25);
                        border-radius:20px;padding:6px 14px;font-size:0.78rem;color:#81c784;font-weight:600">
                🧠 38 Disease Classes
            </div>
            <div style="background:rgba(76,175,80,0.12);border:1px solid rgba(76,175,80,0.25);
                        border-radius:20px;padding:6px 14px;font-size:0.78rem;color:#81c784;font-weight:600">
                📊 Scan History
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Auth card ────────────────────────────────────────────────────
        st.markdown("""
        <div style="background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);
                    border:1px solid rgba(255,255,255,0.1);border-radius:24px;
                    padding:32px 32px 24px;box-shadow:0 16px 60px rgba(0,0,0,0.5)">
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔑  Sign In", "🌱  Create Account"])

        # ── Login ────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<p style='color:#90a4ae;font-size:0.88rem;margin-bottom:4px'>Welcome back! Sign in to continue.</p>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                email    = st.text_input("Email Address", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit   = st.form_submit_button("Sign In →", use_container_width=True)
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    r = api("post", "/api/login", json={"email": email, "password": password})
                    if r is not None:
                        if r.ok:
                            st.session_state.logged_in = True
                            st.session_state.user = r.json()
                            st.success("✅ Signed in successfully!")
                            st.rerun()
                        else:
                            st.error(r.json().get("error", "Login failed."))

        # ── Register ─────────────────────────────────────────────────────
        with tab_reg:
            st.markdown("<p style='color:#90a4ae;font-size:0.88rem;margin-bottom:4px'>Create your free account in seconds.</p>", unsafe_allow_html=True)
            with st.form("register_form", clear_on_submit=False):
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    full_name = st.text_input("Full Name", placeholder="Jane Doe")
                with r_col2:
                    phone = st.text_input("Phone (optional)", placeholder="9876543210", max_chars=10)
                r_email   = st.text_input("Email Address", placeholder="you@example.com")
                location  = st.text_input("Location / Farm Area", placeholder="Pune, Maharashtra")
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    r_pass = st.text_input("Password", type="password", placeholder="Min. 8 characters")
                with p_col2:
                    r_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter")
                reg_submit = st.form_submit_button("Create Account →", use_container_width=True)

            if reg_submit:
                errors = []
                if not full_name:  errors.append("Full name is required.")
                if not r_email:    errors.append("Email is required.")
                if not location:   errors.append("Location is required.")
                if not r_pass:     errors.append("Password is required.")
                elif r_pass != r_confirm: errors.append("Passwords do not match.")
                if errors:
                    for e in errors: st.error(e)
                else:
                    r = api("post", "/api/register", json={
                        "full_name": full_name, "email": r_email, "phone": phone,
                        "location": location,   "password": r_pass,
                    })
                    if r is not None:
                        if r.ok:
                            st.session_state.logged_in = True
                            st.session_state.user = {"name": full_name, "email": r_email}
                            st.success("✅ Account created! Welcome to AgroScan!")
                            st.rerun()
                        else:
                            st.error(r.json().get("error", "Registration failed."))

        st.markdown("</div>", unsafe_allow_html=True)

        # Footer note
        st.markdown("""
        <p style='text-align:center;color:#4a7a4c;font-size:0.75rem;margin-top:20px'>
            🔒 Your data is secure and never shared
        </p>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding:28px 20px 20px;border-bottom:1px solid rgba(255,255,255,0.07)">
            <div style="display:flex;align-items:center;gap:12px">
                <div style="width:44px;height:44px;background:linear-gradient(135deg,#1b5e20,#43a047);
                            border-radius:14px;display:flex;align-items:center;justify-content:center;
                            font-size:1.4rem;box-shadow:0 4px 16px rgba(76,175,80,0.4)">🌿</div>
                <div>
                    <div style="font-size:1.15rem;font-weight:800;color:#e8f5e9;
                                font-family:'Inter',sans-serif;letter-spacing:-0.3px">AgroScan</div>
                    <div style="font-size:0.68rem;color:#4caf50;font-weight:600;
                                text-transform:uppercase;letter-spacing:1.2px">Plant Disease AI</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='padding:16px 4px 8px'>", unsafe_allow_html=True)

        page = st.session_state.get("page", "scan")

        nav_items = [
            ("scan",    "🔍", "Plant Scanner"),
            ("history", "📋", "Scan History"),
            ("profile", "👤", "My Profile"),
        ]
        for key, icon, label in nav_items:
            active_style = "border-left:3px solid #4caf50 !important;background:rgba(76,175,80,0.15) !important;" if page == key else ""
            # We rely on Streamlit buttons; active state via CSS class trick
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

        # User card at bottom
        user  = st.session_state.user or {}
        name  = user.get("name") or user.get("full_name") or "User"
        email = user.get("email", "")
        initial = name[0].upper()

        st.markdown(f"""
        <div style="position:fixed;bottom:20px;left:0;width:var(--sidebar-width,260px);
                    padding:0 16px">
            <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);
                        border-radius:16px;padding:14px 16px;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="width:38px;height:38px;border-radius:12px;flex-shrink:0;
                                background:linear-gradient(135deg,#2e7d32,#66bb6a);
                                display:flex;align-items:center;justify-content:center;
                                font-size:1rem;font-weight:800;color:white">{initial}</div>
                    <div style="overflow:hidden">
                        <div style="font-weight:700;color:#e8f5e9;font-size:0.88rem;
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}</div>
                        <div style="color:#66a068;font-size:0.72rem;white-space:nowrap;
                                    overflow:hidden;text-overflow:ellipsis">{email}</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)
        if st.button("⏻  Sign Out", use_container_width=True):
            api("get", "/logout")
            for k in ["logged_in", "user", "page", "last_result"]:
                st.session_state.pop(k, None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER  (title + subtitle)
# ══════════════════════════════════════════════════════════════════════════════
def page_header(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div style="padding:8px 0 28px">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px">
            <div style="font-size:1.8rem">{icon}</div>
            <h1 style="font-size:1.9rem;font-weight:800;margin:0;
                       background:linear-gradient(135deg,#c8e6c9,#81c784);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                       font-family:'Inter',sans-serif;letter-spacing:-0.5px">{title}</h1>
        </div>
        <p style="color:#547a56;font-size:0.9rem;margin:0 0 0 52px;font-weight:400">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STATS ROW
# ══════════════════════════════════════════════════════════════════════════════
def render_stats():
    r = api("get", "/api/stats")
    if r is None or not r.ok:
        return
    s = r.json()
    st.markdown(f"""
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:28px">
        {stat_card("🌿", s['total'],    "Total Scans", "#66bb6a")}
        {stat_card("✅", s['healthy'],  "Healthy",     "#4caf50")}
        {stat_card("⚠️", s['diseased'], "Diseased",    "#ef5350")}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PLANT EMOJI MAP
# ══════════════════════════════════════════════════════════════════════════════
PLANT_EMOJI = {
    "Apple":"🍎","Blueberry":"🫐","Cherry":"🍒","Corn":"🌽","Grape":"🍇",
    "Orange":"🍊","Peach":"🍑","Pepper":"🫑","Potato":"🥔","Raspberry":"🍓",
    "Soybean":"🌱","Squash":"🎃","Strawberry":"🍓","Tomato":"🍅",
}

# ══════════════════════════════════════════════════════════════════════════════
# SCAN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_scan():
    page_header("🔍", "Plant Scanner", "Upload or capture a leaf image to detect diseases instantly")
    render_stats()

    # ── Upload + Camera ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                border-radius:20px;padding:24px 24px 8px;margin-bottom:20px">
        <p style="color:#81c784;font-size:0.82rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;margin-bottom:16px">📥 Input Method</p>
    """, unsafe_allow_html=True)

    col_up, col_cam = st.columns([1, 1])
    with col_up:
        uploaded = st.file_uploader("Upload from gallery", type=["jpg","jpeg","png","webp"],
                                    label_visibility="visible")
    with col_cam:
        camera_img = st.camera_input("Capture with camera")

    st.markdown("</div>", unsafe_allow_html=True)

    img_source = camera_img if camera_img else uploaded

    if img_source:
        img_bytes = img_source.getvalue()
        image = Image.open(io.BytesIO(img_bytes))

        col_img, col_result = st.columns([1, 1], gap="large")

        with col_img:
            st.markdown("""
            <p style="color:#81c784;font-size:0.78rem;font-weight:700;
                      text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                🖼️ Selected Image
            </p>""", unsafe_allow_html=True)
            st.image(image, use_container_width=True,
                     caption="Ready for analysis")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            analyse_clicked = st.button("🔍  Analyse Leaf", use_container_width=True,
                                        type="primary", key="analyse_btn")

        with col_result:
            st.markdown("""
            <p style="color:#81c784;font-size:0.78rem;font-weight:700;
                      text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                📊 Analysis Result
            </p>""", unsafe_allow_html=True)

            if analyse_clicked:
                with st.spinner("🧠 Analysing with AI…"):
                    b64 = base64.b64encode(img_bytes).decode()
                    r = api("post", "/predict",
                            json={"image": f"data:image/jpeg;base64,{b64}"})

                if r is None:
                    st.error("Server unreachable.")
                elif r.status_code == 422 or (r.ok and "error" in r.json()):
                    err = r.json().get("error","Invalid image.")
                    st.markdown(f"""
                    <div style="background:rgba(239,83,80,0.1);border:1px solid rgba(239,83,80,0.3);
                                border-radius:16px;padding:24px;text-align:center">
                        <div style="font-size:3rem;margin-bottom:12px">🚫</div>
                        <div style="color:#ef9a9a;font-weight:700;font-size:1rem;margin-bottom:6px">Invalid Image</div>
                        <div style="color:#90a4ae;font-size:0.85rem">{err}</div>
                    </div>""", unsafe_allow_html=True)
                elif r.ok:
                    data = r.json()
                    st.session_state.last_result = data
                    _render_result(data)
            elif st.session_state.last_result:
                _render_result(st.session_state.last_result)
            else:
                st.markdown("""
                <div style="background:rgba(255,255,255,0.03);border:2px dashed rgba(255,255,255,0.1);
                            border-radius:16px;padding:40px 24px;text-align:center">
                    <div style="font-size:2.5rem;margin-bottom:12px">🌿</div>
                    <div style="color:#547a56;font-size:0.9rem;font-weight:500">
                        Click <strong style="color:#81c784">Analyse Leaf</strong> to detect diseases
                    </div>
                </div>""", unsafe_allow_html=True)


def _render_result(data: dict):
    is_healthy = data["status"] == "Healthy"
    emoji = PLANT_EMOJI.get(data["plant"], "🌿")
    bg = "rgba(76,175,80,0.08)" if is_healthy else "rgba(239,83,80,0.08)"
    border = "rgba(76,175,80,0.25)" if is_healthy else "rgba(239,83,80,0.25)"

    # Result card
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border};
                border-radius:18px;padding:20px 22px;margin-bottom:14px">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:14px">
            <div style="font-size:2.8rem;line-height:1">{emoji}</div>
            <div style="flex:1">
                <div style="font-size:0.68rem;color:#90a4ae;text-transform:uppercase;
                            letter-spacing:1.2px;font-weight:700;margin-bottom:3px">
                    Identified Plant
                </div>
                <div style="font-size:1.25rem;font-weight:800;color:#e8f5e9;
                            font-family:'Inter',sans-serif;margin-bottom:6px">
                    {data['plant']}
                </div>
                {badge(is_healthy)}
            </div>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:10px;
                    padding:10px 14px;font-size:0.9rem;color:#b0bec5;font-weight:500">
            {'✨ No disease detected' if is_healthy else f'🦠 {data["disease"]}'}
        </div>
    </div>
    {conf_bar(data['confidence'], is_healthy)}
    """, unsafe_allow_html=True)

    cure = data.get("cure")
    if not is_healthy and cure:
        st.markdown("""<p style="color:#81c784;font-size:0.78rem;font-weight:700;
                              text-transform:uppercase;letter-spacing:1px;
                              margin:16px 0 8px">💊 Treatment Guide</p>""",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.tabs(["🔬 Cause", "💊 Treatment", "🛡️ Prevention"])
        with c1:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border-radius:14px;
                        padding:16px 18px;border-left:3px solid #ef5350">
                <div style="font-size:0.7rem;color:#90a4ae;font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Root Cause</div>
                <p style="color:#cfd8dc;font-size:0.9rem;line-height:1.7;margin:0">{cure['cause']}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            for i, step in enumerate(cure["treatment"], 1):
                st.markdown(f"""
                <div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:10px;
                            background:rgba(255,255,255,0.04);border-radius:12px;padding:12px 14px">
                    <div style="background:linear-gradient(135deg,#2e7d32,#43a047);color:white;
                                border-radius:8px;width:26px;height:26px;min-width:26px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.72rem;font-weight:800;box-shadow:0 2px 8px rgba(76,175,80,0.4)">{i}</div>
                    <div style="color:#cfd8dc;font-size:0.88rem;line-height:1.6;padding-top:2px">{step}</div>
                </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.04);border-radius:14px;
                        padding:16px 18px;border-left:3px solid #4caf50">
                <div style="font-size:0.7rem;color:#90a4ae;font-weight:700;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Prevention Tips</div>
                <p style="color:#cfd8dc;font-size:0.9rem;line-height:1.7;margin:0">{cure['prevention']}</p>
            </div>""", unsafe_allow_html=True)
    elif is_healthy:
        st.markdown("""
        <div style="background:rgba(76,175,80,0.08);border:1px solid rgba(76,175,80,0.2);
                    border-radius:14px;padding:16px 18px;margin-top:12px;
                    display:flex;gap:14px;align-items:flex-start">
            <div style="font-size:1.8rem;flex-shrink:0">🌱</div>
            <div>
                <div style="font-weight:700;color:#66bb6a;margin-bottom:4px">Healthy Leaf</div>
                <div style="color:#81c784;font-size:0.88rem;line-height:1.6">
                    No disease detected. Keep monitoring regularly and maintain good agricultural practices.
                </div>
            </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_history():
    page_header("📋", "Scan History", "All your previous scans — click any entry for full details")

    r = api("get", "/api/history")
    if r is None:
        return
    if not r.ok:
        st.error("Could not load history.")
        return

    scans = r.json()
    if not scans:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03);border:2px dashed rgba(255,255,255,0.1);
                    border-radius:20px;padding:60px 24px;text-align:center">
            <div style="font-size:3rem;margin-bottom:14px">🌿</div>
            <div style="color:#547a56;font-size:1rem;font-weight:600">No scans yet</div>
            <div style="color:#3d5c3e;font-size:0.85rem;margin-top:6px">
                Head over to the Scanner to analyse your first leaf!
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Summary banner ───────────────────────────────────────────────────────
    total    = len(scans)
    healthy  = sum(1 for s in scans if s["status"] == "Healthy")
    diseased = total - healthy
    pct      = round(healthy / total * 100) if total else 0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(27,94,32,0.6),rgba(46,125,50,0.4));
                border:1px solid rgba(76,175,80,0.25);border-radius:20px;
                padding:20px 24px;margin-bottom:24px;
                display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div>
            <div style="font-size:0.72rem;color:#81c784;text-transform:uppercase;
                        letter-spacing:1.2px;font-weight:700;margin-bottom:4px">Your Garden Health</div>
            <div style="font-size:1.4rem;font-weight:800;color:#e8f5e9">{pct}% Healthy Rate</div>
        </div>
        <div style="display:flex;gap:20px">
            <div style="text-align:center">
                <div style="font-size:1.5rem;font-weight:800;color:#66bb6a">{total}</div>
                <div style="font-size:0.7rem;color:#547a56;text-transform:uppercase;letter-spacing:1px">Total</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:1.5rem;font-weight:800;color:#4caf50">{healthy}</div>
                <div style="font-size:0.7rem;color:#547a56;text-transform:uppercase;letter-spacing:1px">Healthy</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:1.5rem;font-weight:800;color:#ef5350">{diseased}</div>
                <div style="font-size:0.7rem;color:#547a56;text-transform:uppercase;letter-spacing:1px">Diseased</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filter ───────────────────────────────────────────────────────────────
    flt = st.radio("", ["🌿 All", "✅ Healthy", "⚠️ Diseased"],
                   horizontal=True, label_visibility="collapsed")
    if "Healthy" in flt:
        scans = [s for s in scans if s["status"] == "Healthy"]
    elif "Diseased" in flt:
        scans = [s for s in scans if s["status"] == "Diseased"]

    st.markdown(f"<p style='color:#547a56;font-size:0.8rem;margin:8px 0 16px'>{len(scans)} result(s)</p>",
                unsafe_allow_html=True)

    # ── Scan cards ───────────────────────────────────────────────────────────
    for s in scans:
        is_h  = s["status"] == "Healthy"
        icon  = "✅" if is_h else "⚠️"
        plant_emoji = PLANT_EMOJI.get(s["plant"], "🌿")
        date_str = s["scanned_at"][:16].replace("T", " ")
        border_c = "rgba(76,175,80,0.35)" if is_h else "rgba(239,83,80,0.35)"
        conf_c   = "#66bb6a" if is_h else "#ef5350"

        with st.expander(f"{plant_emoji}  {s['plant']}  ·  {s['disease']}"):
            # Card header
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        flex-wrap:wrap;gap:10px;margin-bottom:14px">
                <div style="display:flex;align-items:center;gap:12px">
                    <div style="font-size:2.2rem">{plant_emoji}</div>
                    <div>
                        <div style="font-weight:800;color:#e8f5e9;font-size:1.05rem">{s['plant']}</div>
                        <div style="color:#90a4ae;font-size:0.82rem">{s['disease']}</div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:10px">
                    {badge(is_h)}
                    <div style="background:rgba(255,255,255,0.06);border-radius:8px;
                                padding:4px 10px;font-size:0.72rem;color:#78909c">{date_str}</div>
                </div>
            </div>
            {conf_bar(s['confidence'], is_h)}
            """, unsafe_allow_html=True)

            if not is_h:
                rc = api("get", f"/api/cure/{requests.utils.quote(s['disease'])}")
                if rc and rc.ok:
                    cure = rc.json()
                    t1, t2, t3 = st.tabs(["🔬 Cause", "💊 Treatment", "🛡️ Prevention"])
                    with t1:
                        st.markdown(f"<p style='color:#cfd8dc;font-size:0.9rem;line-height:1.7'>{cure.get('cause','—')}</p>",
                                    unsafe_allow_html=True)
                    with t2:
                        for i, step in enumerate(cure.get("treatment", []), 1):
                            st.markdown(f"""
                            <div style='display:flex;gap:10px;margin-bottom:8px;align-items:flex-start;
                                        background:rgba(255,255,255,0.03);border-radius:10px;padding:10px 12px'>
                                <div style='background:#2e7d32;color:white;border-radius:6px;
                                            width:22px;height:22px;min-width:22px;font-size:0.7rem;
                                            font-weight:800;display:flex;align-items:center;
                                            justify-content:center'>{i}</div>
                                <div style='color:#cfd8dc;font-size:0.88rem;line-height:1.6'>{step}</div>
                            </div>""", unsafe_allow_html=True)
                    with t3:
                        st.markdown(f"<p style='color:#cfd8dc;font-size:0.9rem;line-height:1.7'>{cure.get('prevention','—')}</p>",
                                    unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(76,175,80,0.1);border-radius:12px;
                            padding:14px 16px;color:#81c784;font-size:0.88rem">
                    🌱 <strong>Healthy leaf</strong> — No treatment required. Keep monitoring.
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_profile():
    page_header("👤", "My Profile", "Manage your account and view statistics")

    r_user  = api("get", "/api/profile/me")
    r_stats = api("get", "/api/stats")

    user  = r_user.json()  if (r_user  and r_user.ok)  else (st.session_state.user or {})
    stats = r_stats.json() if (r_stats and r_stats.ok) else {"total":0,"healthy":0,"diseased":0}

    name     = user.get("full_name") or user.get("name") or "User"
    email    = user.get("email", "")
    phone    = user.get("phone")    or "Not provided"
    location = user.get("location") or "Not provided"
    joined   = (user.get("created_at") or "")[:10] or "—"
    initial  = name[0].upper()

    # ── Hero banner ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d2e0f 0%,#1b5e20 60%,#2e7d32 100%);
                border:1px solid rgba(76,175,80,0.2);border-radius:24px;padding:32px 28px;
                margin-bottom:24px;position:relative;overflow:hidden">
        <div style="position:absolute;top:-40px;right:-40px;width:180px;height:180px;
                    background:rgba(76,175,80,0.08);border-radius:50%"></div>
        <div style="position:absolute;bottom:-60px;left:-30px;width:220px;height:220px;
                    background:rgba(76,175,80,0.05);border-radius:50%"></div>
        <div style="display:flex;align-items:center;gap:20px;position:relative">
            <div style="width:72px;height:72px;border-radius:22px;flex-shrink:0;
                        background:linear-gradient(135deg,#388e3c,#81c784);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.8rem;font-weight:800;color:white;
                        box-shadow:0 8px 24px rgba(76,175,80,0.5)">{initial}</div>
            <div>
                <div style="font-size:1.5rem;font-weight:800;color:#e8f5e9;
                            font-family:'Inter',sans-serif;margin-bottom:4px">{name}</div>
                <div style="color:#81c784;font-size:0.88rem;margin-bottom:3px">📧 {email}</div>
                <div style="color:#4caf50;font-size:0.75rem;font-weight:600">
                    🗓️ Member since {joined}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:24px">
        {stat_card("🌿", stats['total'],    "Total Scans", "#66bb6a")}
        {stat_card("✅", stats['healthy'],  "Healthy",     "#4caf50")}
        {stat_card("⚠️", stats['diseased'], "Diseased",    "#ef5350")}
    </div>
    """, unsafe_allow_html=True)

    # ── Info grid ────────────────────────────────────────────────────────────
    def info_tile(icon, label, value):
        return f"""
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px;padding:18px 20px">
            <div style="font-size:1.3rem;margin-bottom:8px">{icon}</div>
            <div style="font-size:0.68rem;color:#547a56;text-transform:uppercase;
                        letter-spacing:1.2px;font-weight:700;margin-bottom:4px">{label}</div>
            <div style="font-weight:600;color:#c8e6c9;font-size:0.95rem">{value}</div>
        </div>"""

    c1, c2, c3, c4 = st.columns(4)
    tiles = [
        ("📧","Email",    email),
        ("📱","Phone",    phone),
        ("📍","Location", location),
        ("📅","Joined",   joined),
    ]
    for col, (icon, label, val) in zip([c1,c2,c3,c4], tiles):
        with col:
            st.markdown(info_tile(icon, label, val), unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Edit tabs ────────────────────────────────────────────────────────────
    st.markdown("""
    <p style="color:#81c784;font-size:0.78rem;font-weight:700;
              text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">
        ✏️ Edit Account
    </p>""", unsafe_allow_html=True)

    edit_tab, pass_tab = st.tabs(["👤 Personal Info", "🔒 Change Password"])

    with edit_tab:
        with st.form("edit_profile"):
            ec1, ec2 = st.columns(2)
            with ec1:
                e_name = st.text_input("Full Name", value=name)
            with ec2:
                st.text_input("Email (locked)", value=email, disabled=True)
            ep1, ep2 = st.columns(2)
            with ep1:
                e_phone = st.text_input("Phone", value=user.get("phone",""))
            with ep2:
                e_loc = st.text_input("Location / Farm", value=user.get("location",""))
            save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
        if save_btn:
            if not e_name.strip():
                st.error("Name cannot be empty.")
            else:
                r = api("post", "/api/profile/update", json={
                    "full_name": e_name.strip(),
                    "phone":     e_phone.strip(),
                    "location":  e_loc.strip(),
                })
                if r and r.ok:
                    st.success("✅ Profile updated successfully!")
                    if st.session_state.user:
                        st.session_state.user["name"] = e_name.strip()
                    st.rerun()
                elif r:
                    st.error(r.json().get("error","Update failed."))

    with pass_tab:
        with st.form("change_pw"):
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                old_pw = st.text_input("Current Password", type="password")
            with pc2:
                new_pw = st.text_input("New Password", type="password",
                                       help="Minimum 6 characters")
            with pc3:
                conf_pw = st.text_input("Confirm New", type="password")
            pw_btn = st.form_submit_button("🔒 Update Password", use_container_width=True)
        if pw_btn:
            if not old_pw or not new_pw or not conf_pw:
                st.error("Please fill in all fields.")
            elif len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                r = api("post", "/api/profile/password",
                        json={"old_password": old_pw, "new_password": new_pw})
                if r and r.ok:
                    st.success("🔒 Password changed successfully!")
                elif r:
                    st.error(r.json().get("error","Failed to change password."))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.logged_in:
        page_auth()
        return

    render_sidebar()

    page = st.session_state.get("page", "scan")
    if page == "scan":
        page_scan()
    elif page == "history":
        page_history()
    elif page == "profile":
        page_profile()
    else:
        page_scan()


main()
