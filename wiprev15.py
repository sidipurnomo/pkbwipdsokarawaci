import streamlit as st
import pandas as pd
import time
import requests
import json
from datetime import datetime

# ==========================================
# 🌟 KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz_uF5eFhIEqIpOvFh743QSzaDMItK2Npbdc4qcoGERdHM_R5Da-CvERDg7RbNampxysw/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

# Nomor WA Admin Part / Email Admin Part (Silakan sesuaikan)
NO_WA_ADMIN_PART = "6281234567890" 
EMAIL_ADMIN_PART = "admin.part@karawaci.daihatsu.co.id"

# ==========================================
# 🌟 LINK LOGO SUPER JERNIH (VECTOR/PNG)
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
    /* Penyesuaian Latar Belakang & Warna Teks Adaptif */
    .stApp { background-color: var(--background-color); }
    
    /* Tombol Kustom */
    div.stButton > button {
        border-radius: 8px; border: 1px solid #ff4b4b; background-color: transparent;
        color: #ff4b4b; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.4); background-color: #ff4b4b;
        color: white; transform: scale(1.02);
    }
    
    /* Styling Radio Button Menu */
    div[role="radiogroup"] > label {
        background-color: var(--secondary-background-color) !important; 
        padding: 10px 5px !important; border-radius: 10px; margin-bottom: 12px;
        border: 1px solid #bbdefb; border-bottom: 4px solid #90caf9; 
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1); cursor: pointer; white-space: nowrap !important;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-2px); border-bottom: 6px solid #64b5f6; 
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: bold !important; margin: 0 !important;
    }

    /* Kustomisasi Metrik agar Horizontal di Layar HP */
    .metric-container {
        display: flex; flex-direction: row; flex-wrap: nowrap;
        justify-content: space-between; gap: 8px; 
        margin-bottom: 20px; width: 100%; overflow-x: auto;
        padding-bottom: 5px;
    }
    .metric-card {
        flex: 1; min-width: 70px; background-color: #fce4ec; border-radius: 10px; 
        padding: 12px 5px; text-align: center; border: 1px solid #f8bbd0;
        border-bottom: 5px solid #f48fb1; box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .metric-title { font-size: 11px; font-weight: 700; color: #424242; margin-bottom: 5px; line-height: 1.2;}
    .metric-value { font-size: 16px; font-weight: 900; color: #d81b60; }
    
    /* Header Horizontal Paksa untuk HP */
    .header-horizontal {
        display: flex; align-items: center; justify-content: flex-start;
        flex-wrap: nowrap;
    }
    
    /* Glow Title */
    .title-glowing {
        color: #ff4b4b; text-shadow: 1px 1px 3px rgba(255, 75, 75, 0.2);
        font-family: 'Arial Black', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔐 SISTEM LOGIN & AUTO LOGOUT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'last_activity' not in st.session_state: st.session_state['last_activity'] = time.time()
if 'last_menu' not in st.session_state: st.session_state['last_menu'] = None

if st.session_state['logged_in']:
    if time.time() - st.session_state['last_activity'] > 1800:
        st.session_state['logged_in'] = False
        st.warning("⏱️ Sesi berakhir. Silakan login kembali.")
        time.sleep(3) 
        st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='header-horizontal' style='justify-content: center; margin-bottom: 20px;'>
            <img src='{DAIHATSU_LOGO_PNG}' style='height: 40px; margin-right: 15px;'>
            <h2 class='title-glowing' style='margin: 0; font-size: 24px;'>PKB WIP DSO KARAWACI</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Username")
            password = st.text_input("🔑 Password", type="password")
            if st.form_submit_button("🚀 LOGIN KE SISTEM", use_container_width=True):
                if username == "dsokarawaci" and password == "adminkarawaci":
                    st.session_state['logged_in'] = True
                    st.session_state['last_activity'] = time.time() 
                    st.rerun()
                else:
                    st.error("⚠️ Akses Ditolak!")

if not st.session_state['logged_in']:
    render_login()
    st.stop()

# ==========================================
# 🚪 SIDEBAR MENU KIRI
# ==========================================
with st.sidebar:
    st.markdown(f"<div style='text-align: center;'><img src='{DAIHATSU_LOGO_PNG}' style='width: 120px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-weight:bold; margin-bottom: 20px;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)
    
    menu_pilihan = st.radio("Pilih Halaman:", [
        "📊 SEMUA WIP", 
        "🛠️ ANTREAN GR", 
        "📝 UPDATE GR", 
        "🔨 ANTREAN BR", 
        "📝 UPDATE BR",
        "📱 TAMPILAN HP", # Menu Baru
        "✅ RIWAYAT SELESAI"
    ], label_visibility="collapsed")
    
    if menu_pilihan != st.session_state['last_menu']:
        st.session_state['last_activity'] = time.time()
        st.session_state['last_menu'] = menu_pilihan

# ==========================================
# 🌐 INTEGRASI DATABASE CLOUD
# ==========================================
@st.cache_data(ttl=10)
def load_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=15)
        data = response.json()
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        kolom_wajib = ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']
        for col in kolom_wajib:
            if col not in df.columns: 
                df[col] = "-"
        
        if 'No PKB' in df.columns and 'Tipe Kendaraan' in df.columns:
            cols = list(df.columns)
            cols.remove('Tipe Kendaraan') 
            idx_no_pkb = cols.index('No PKB') 
            cols.insert(idx_no_pkb + 1, 'Tipe Kendaraan') 
            df = df[cols] 
            
        if 'Tgl PKB' in df.columns:
            df['Tgl PKB'] = pd.to_datetime(df['Tgl PKB'], errors='coerce').dt.tz_localize(None)
            now = pd.Timestamp.now().normalize()
            df['Umur PKB (Hari)'] = (now - df['Tgl PKB']).dt.days.fillna(0).astype(int)
            df['Tgl PKB'] = df['Tgl PKB'].dt.strftime('%Y-%m-%d').fillna("-")
