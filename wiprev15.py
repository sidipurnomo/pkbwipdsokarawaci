import streamlit as st
import pandas as pd
import time
import requests
import io
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
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz_uF5eFhIEqIpOvFh743QSzaDMItK2Npbdc4qcoGERdHM_R5Da-CvERDg7RbNampxysw/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

# Konfigurasi Notifikasi Email
SENDER_EMAIL = "akunbodong@gmail.com"
SENDER_APP_PASSWORD = "apabae" 

# Konfigurasi Notifikasi WhatsApp (FLOWKIRIM API)
API_URL_FLOWKIRIM = "https://scan.flowkirim.com"
FLOWKIRIM_API_TOKEN = "6945723a2f3ff34569a1c5b963a3f034fab3c9f79bf8fe69aaac9fe25856071a"

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
    st.markdown(f"<h1 class='title-glowing'><img src='{DAIHATSU_LOGO_PNG}' style='height: 40px; margin-right: 15px;'> PKB WIP DSO KARAWACI</h1>", unsafe_allow_html=True)
    st.markdown("""
    <style>
        div[data-testid="stForm"] { max-width: 450px !important; margin: 0 auto !important; padding: 2rem !important; box-shadow: 0px 8px 20px rgba(0,0,0,0.05) !important; }
        @media (max-width: 768px) { div[data-testid="stForm"] { max-width: 90% !important; padding: 1.5rem !important; margin-top: 20px !important; } }
    </style>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center;'>🔐 Login Dashboard</h3>", unsafe_allow_html=True)
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("LOGIN", width="stretch"):
            if username == "dsokarawaci" and password == "adminkarawaci":
                st.session_state['logged_in'] = True
                st.session_state['last_activity'] = time.time() 
                st.rerun()
            else:
                st.error("⚠️ Username atau Password Salah!")

if not st.session_state['logged_in']:
    render_login()
    st.stop()

# ==========================================
# 🚪 SIDEBAR MENU KIRI
# ==========================================
with st.sidebar:
    st.markdown(f"<div style='text-align: center;'><img src='{DAIHATSU_LOGO_PNG}' style='width: 120px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#2e7d32;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)
    menu_pilihan = st.radio(
        "Pilih Halaman:", 
        ["📊 SEMUA WIP", "📱 TAMPILAN MOBILE", "🛠️ ANTREAN GR", "📝 UPDATE GR", "🔨 ANTREAN BR", "📝 UPDATE BR", "✅ RIWAYAT SELESAI", "➕ TAMBAH MOBIL TAMU"], 
        label_visibility="collapsed"
    )
    
    if menu_pilihan != st.session_state['last_menu']:
        st.session_state['last_activity'] = time.time()
        st.session_state['last_menu'] = menu_pilihan

# ==========================================
# 🌐 INTEGRASI CLOUD & FUNGSI BARU
# ==========================================
def hitung_progress(kategori, status):
    if status == "Selesai": return 100
    if status == "Menunggu Part": return 50
    if status == "Quality Control": return 90

    if kategori == "General Repair":
        if status == "Menunggu Pekerjaan": return 10
        if status == "Sedang Dikerjakan": return 60
    elif kategori == "Body Repair":
        br_steps = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan"]
        if status in br_steps:
            return int(((br_steps.index(status) + 1) / len(br_steps)) * 85)
    return 0

@st.cache_data(ttl=15) 
def load_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=15)
        if response.status_code != 200:
            st.error(f"Gagal koneksi ke Cloud. HTTP Code: {response.status_code}")
            return pd.DataFrame()
            
        try:
            data = response.json()
        except ValueError:
            st.error("❌ Gagal membaca data dari Google Sheets. Server mengembalikan bukan format JSON. "
                     "Pastikan Apps Script telah di-deploy dengan akses 'Anyone'.")
            st.error(f"Respons server: {response.text[:200]}")
            return pd.DataFrame()

        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        if 'No PKB' in df.columns and 'No Polisi' in df.columns:
            df['Identifier'] = df.apply(lambda x: str(x['No PKB']).strip() if str(x.get('No PKB', '')).strip() not in ['', '-', 'BELUM ADA', 'nan'] else str(x.get('No Polisi', '')).strip(), axis=1)
            df = df.drop_duplicates(subset=['Identifier'], keep='last').drop(columns=['Identifier']).reset_index(drop=True)
        elif 'No Polisi' in df.columns:
            df = df.drop_duplicates(subset=['No Polisi'], keep='last').reset_index(drop=True)

        kolom_wajib = ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']
        for col in kolom_wajib:
            if col not in df.columns: df[col] = "-"
        
        if 'No PKB' in df.columns and 'Tipe Kendaraan' in df.columns:
            cols = list(df.columns)
            cols.remove('Tipe Kendaraan') 
            cols.insert(cols.index('No PKB') + 1, 'Tipe Kendaraan') 
            df = df[cols] 
            
        if 'Tgl PKB' in df.columns:
            df['Tgl PKB'] = pd.to_datetime(df['Tgl PKB'], errors='coerce')
            df['Tgl PKB'] = df['Tgl PKB'].dt.tz_localize(None)
            now = pd.Timestamp.now().normalize()
            df['Umur PKB (Hari)'] = (now - df['Tgl PKB']).dt.days
            df['Umur PKB (Hari)'] = df['Umur PKB (Hari)'].fillna(0).astype(int)
            df['Tgl PKB'] = df['Tgl PKB'].dt.strftime('%Y-%m-%d').fillna("-")
            
            cols = list(df.columns)
            if 'Umur PKB (Hari)' in cols and 'Tgl PKB' in cols:
                cols.remove('Umur PKB (Hari)')
                cols.insert(cols.index('Tgl PKB') + 1, 'Umur PKB (Hari)')
                df = df[cols]
                
        if 'Kategori' in df.columns and 'Status Pekerjaan' in df.columns:
            df['Progress (%)'] = df.apply(lambda row: hitung_progress(row['Kategori'], row['Status Pekerjaan']), axis=1)

        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal koneksi internet ke database Cloud: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data Cloud: {e}")
        return pd.DataFrame()

def get_merged_data():
    new_df = load_data()
    if 'df_data' in st.session_state and st.session_state['df_data'] is not None:
        old_df = st.session_state['df_data']
        if not new_df.empty and not old_df.empty and 'No Polisi' in old_df.columns:
            old_status_map = dict(zip(old_df['No Polisi'], old_df['Status Pekerjaan'])) if 'Status Pekerjaan' in old_df.columns else {}
            old_ket_map = dict(zip(old_df['No Polisi'], old_df['Keterangan Lanjutan'])) if 'Keterangan Lanjutan' in old_df.columns else {}
            old_foto_map = dict(zip(old_df['No Polisi'], old_df['Foto PKB'])) if 'Foto PKB' in old_df.columns else {}
            
            if 'Status Pekerjaan' in new_df.columns:
                new_df['Status Pekerjaan'] = new_df.apply(lambda row: old_status_map.get(row['No Polisi'], row['Status Pekerjaan']), axis=1)
            if 'Keterangan Lanjutan' in new_df.columns:
                new_df['Keterangan Lanjutan'] = new_df.apply(lambda row: old_ket_map.get(row['No Polisi'], row['Keterangan Lanjutan']), axis=1)
            if 'Foto PKB' in new_df.columns:
                new_df['Foto PKB'] = new_df.apply(lambda row: old_foto_map.get(row['No Polisi'], row['Foto PKB']), axis=1)
            
            new_nopol_list = new_df['No Polisi'].tolist()
            missing_df = old_df[~old_df['No Polisi'].isin(new_nopol_list)].copy()
            
            if not missing_df.empty:
                missing_df['Status Pekerjaan'] = 'Selesai'
                if 'Keterangan Lanjutan' in missing_df.columns:
                    missing_df['Keterangan Lanjutan'] = missing_df['Keterangan Lanjutan'].astype(str) + " [Auto-Selesai: Database ditimpa]"
                else:
                    missing_df['Keterangan Lanjutan'] = "[Auto-Selesai: Database ditimpa]"
                
                missing_df['Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_df = pd.concat([new_df, missing_df], ignore_index=True)
                
                try:
                    df_to_save = new_df.drop(columns=['Umur PKB (Hari)', 'Progress (%)', 'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'], errors='ignore')
                    df_to_save = df_to_save.fillna("-").astype(str)
                    requests.post(APPS_SCRIPT_URL, json=[df_to_save.columns.tolist()] + df_to_save.values.tolist(), timeout=10)
                except:
                    pass

    return new_df

def save_data(df):
    df_to_save = df.drop(columns=['Umur PKB (Hari)', 'Progress (%)', 'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'], errors='ignore')
    df_to_save = df_to_save.fillna("-").
