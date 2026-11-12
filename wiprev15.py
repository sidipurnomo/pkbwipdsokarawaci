import streamlit as st
import pandas as pd
import time
import requests
import io
import base64
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==========================================
# 🌟 KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbybnr3sAxBqsyghspXAZlyVOPq83ILSziZountsF2M7UUV_H-uqcn0iJUr5IBmO1v63/exec"

# Konfigurasi Notifikasi Email
SENDER_EMAIL = "akunbodong@gmail.com"
SENDER_APP_PASSWORD = "apabae"

# Konfigurasi Notifikasi WhatsApp (GREEN API)
GREEN_API_HOST = "https://7107.api.greenapi.com"
GREEN_API_ID_INSTANCE = "710722681804"
GREEN_API_TOKEN = "1adfea21b7d0429aa3fb6b88463955fbc5ccde8b52234b0792"

# --- 📌 PETA NOMOR WA BERDASARKAN NAMA SA ---
WA_SA_MAP = {
    "SAHRIM022761": "6287774134574",
    "MAULAN030509": "6281366664391",
    "BERLIA039884": "6283893470438",
    "MUHAMM086163": "628558825962",
}

# Daftar Backup
WA_SA_BR_FALLBACK = ["6287774134574"]
WA_SA_GR_FALLBACK = ["6287774134574"]
WA_ADMIN_PART = ["6289630028860", "6285888874700"]

# Kolom inti dashboard
CORE_COLUMNS = [
    'No PKB', 'Tipe Kendaraan', 'No Polisi', 'Nama Customer', 'Kategori',
    'Status Pekerjaan', 'Nama SA', 'Tgl PKB', 'Tanggal Terakhir Diupdate',
    'Keterangan Lanjutan', 'Foto PKB', 'Status SPK Asuransi',
    'Status Pembayaran OR', 'Kelengkapan Dokumen Asuransi'
]

# Kolom hasil kalkulasi UI (tidak ikut disimpan balik ke sheet)
COMPUTED_COLUMNS = [
    'Umur PKB (Hari)', 'Progress (%)',
    'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'
]

# ==========================================
# 🌟 LINK LOGO & PAGE CONFIG
# ==========================================
DAIHATSU_LOGO_PNG = "https://images.seeklogo.com/logo-png/3/1/daihatsu-logo-png_seeklogo-38135.png"

st.set_page_config(
    page_title="PKB WIP DSO KARAWACI",
    page_icon=DAIHATSU_LOGO_PNG,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 CSS STYLING
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f7fdf7 !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"], [data-testid="stSidebar"] p, [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #2e7d32 !important; }
    }
    div.stButton > button {
        border-radius: 8px; border: 1px solid #4caf50; background-color: transparent;
        color: #2e7d32; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(76, 175, 80, 0.4); background-color: #4caf50;
        color: white; transform: scale(1.02);
    }
    [data-testid="stSidebar"] { font-size: 1.15rem !important; }
    div[role="radiogroup"] > label {
        background-color: #f1f8e9 !important; color: #1b5e20 !important;
        padding: 10px 5px !important; border-radius: 10px; margin-bottom: 12px;
        border: 1px solid #dcedc8; border-bottom: 5px solid #aed581;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05); cursor: pointer; white-space: nowrap !important;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-3px); border-bottom: 7px solid #7cb342;
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: 800 !important; margin: 0 !important; white-space: nowrap !important;
    }
    div[data-testid="metric-container"] {
        background: radial-gradient(circle at top left, #ffffff, #e8f5e9) !important;
        border-radius: 35px !important;
        padding: 20px 10px !important;
        border: 2px solid #aed581 !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.08), inset -3px -3px 10px rgba(0,0,0,0.04) !important;
        text-align: center !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        min-height: 150px !important; width: 100% !important; transition: all 0.3s ease-in-out;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) scale(1.02); box-shadow: 0px 8px 20px rgba(76, 175, 80, 0.3) !important;
    }
    div[data-testid="metric-container"] > div { width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    div[data-testid="metric-container"] label { color: #2e7d32 !important; font-weight: 800 !important; font-size: 15px !important; text-align: center !important; width: 100% !important; margin-bottom: 8px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 900 !important; font-size: 28px !important; text-align: center !important; width: 100% !important; }
    .title-glowing { text-align: center; color: #2e7d32; text-shadow: 2px 2px 4px rgba(76, 175, 80, 0.3); font-family: 'Arial Black', sans-serif; display: flex; justify-content: center; align-items: center; flex-wrap: wrap; }
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; overflow-x: auto !important; -webkit-overflow-scrolling: touch; padding-bottom: 15px; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: 160px !important; flex: 0 0 auto !important; }
        div[data-testid="stForm"] { border-radius: 15px !important; }
        .title-glowing { font-size: 1.5rem !important; }
        .title-glowing img { height: 30px !important; margin-right: 10px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SISTEM LOGIN & AUTO LOGOUT
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'last_activity' not in st.session_state:
    st.session_state['last_activity'] = time.time()
if 'last_menu' not in st.session_state:
    st.session_state['last_menu'] = None

if st.session_state['logged_in']:
    if time.time() - st.session_state['last_activity'] > 1800:
        st.session_state['logged_in'] = False
        st.warning("⏱️ Sesi berakhir. Silakan login kembali.")
        time.sleep(2)
        st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <h1 class='title-glowing'>
            <img src='{DAIHATSU_LOGO_PNG}' style='height: 40px; margin-right: 15px;'>
            PKB WIP DSO KARAWACI
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""
    <style>
        div[data-testid="stForm"] { max-width: 450px !important; margin: 0 auto !important; padding: 2rem !important; box-shadow: 0px 8px 20px rgba(0,0,0,0.05) !important; }
        @media (max-width: 768px) { div
