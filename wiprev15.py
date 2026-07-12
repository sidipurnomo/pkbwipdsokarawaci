import streamlit as st
import pandas as pd
import time
import requests
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw3_oAXnBuqUHwYAQDdlka4jfJY2bv8JTb--dTOK9giH1X-PIVEpFE0r4vgugs2YsggNQ/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

# Konfigurasi Notifikasi Otomatis
SENDER_EMAIL = "sidi.purnomo@dso.astra.co.id"
SENDER_APP_PASSWORD = "Bu***@07" 
WA_API_URL = "https://gate.whapi.cloud/"
WA_API_TOKEN = "CIgRwaeFa1cvnYaWH1RtBL6taXQi3vcq"

# Konfigurasi Nomor WA Target
WA_SA_BR = ["6281399211266", "6285600199590"]
WA_SA_GR = ["6281366664391", "6283893470438", "628558825962", "6287774134574"]
WA_ADMIN_PART = ["6289630028860", "6285888874700"]

# ==========================================
# LINK LOGO & PAGE CONFIG
# ==========================================
DAIHATSU_LOGO_PNG = "https://images.seeklogo.com/logo-png/3/1/daihatsu-logo-png_seeklogo-38135.png"

st.set_page_config(
    page_title="PKB WIP DSO KARAWACI",
    page_icon=DAIHATSU_LOGO_PNG,
    layout="wide"
)

# ==========================================
# CSS STYLING
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f7fdf7 !important; }
    div.stButton > button {
        border-radius: 8px; border: 1px solid #4caf50; background-color: transparent;
        color: #2e7d32; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(76, 175, 80, 0.4); background-color: #4caf50;
        color: white; transform: scale(1.02);
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
    .title-glowing { text-align: center; color: #2e7d32; text-shadow: 2px 2px 4px rgba(76, 175, 80, 0.3); font-family: 'Arial Black', sans-serif; display: flex; justify-content: center; align-items: center; flex-wrap: wrap; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEM LOGIN & AUTO LOGOUT
# ==========================================
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
if 'last_activity' not in st.session_state: 
    st.session_state['last_activity'] = time.time()

if st.session_state['logged_in']:
    if time.time() - st.session_state['last_activity'] > 1800:
        st.session_state['logged_in'] = False
        st.warning("⏱️ Sesi berakhir. Silakan login kembali.")
        time.sleep(3) 
        st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='title-glowing'><img src='{DAIHATSU_LOGO_PNG}' style='height: 40px; margin-right: 15px;'> PKB WIP DSO KARAWACI</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center;'>🔐 Login Dashboard</h3>", unsafe_allow_html=True)
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button("LOGIN KE SISTEM", use_container_width=True):
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
# INTEGRASI CLOUD & FUNGSI 
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
        if response.status_code != 200: return pd.DataFrame()
        data = response.json()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(data)
        if 'No Polisi' in df.columns:
            df = df.drop_duplicates(subset=['No Polisi'], keep='last').reset_index(drop=True)
        kolom_wajib = ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']
        for col in kolom_wajib:
            if col not in df.columns: df[col] = "-"
        if 'Tgl PKB' in df.columns:
            df['Tgl PKB'] = pd.to_datetime(df['Tgl PKB'], errors='coerce')
            df['Tgl PKB'] = df['Tgl PKB'].dt.tz_localize(None)
            now = pd.Timestamp.now().normalize()
            df['Umur PKB (Hari)'] = (now - df['Tgl PKB']).dt.days
            df['Umur PKB (Hari)'] = df['Umur PKB (Hari)'].fillna(0).astype(int)
            df['Tgl PKB'] = df['Tgl PKB'].dt.strftime('%Y-%m-%d').fillna("-")
        if 'Kategori' in df.columns and 'Status Pekerjaan' in df.columns:
            df['Progress (%)'] = df.apply(lambda row: hitung_progress(row['Kategori'], row['Status Pekerjaan']), axis=1)
        return df
    except: return pd.DataFrame()

def get_merged_data():
    new_df = load_data()
    if 'df_data' in st.session_state and st.session_state['df_data'] is not None:
        old_df = st.session_state['df_data']
        if not new_df.empty and not old_df.empty and 'No Polisi' in old_df.columns:
            old_status_map = dict(zip(old_df['No Polisi'], old_df['Status Pekerjaan']))
            new_df['Status Pekerjaan'] = new_df.apply(lambda row: old_status_map.get(row['No Polisi'], row['Status Pekerjaan']), axis=1)
    return new_df

def save_data(df):
    df_to_save = df.drop(columns=['Umur PKB (Hari)', 'Progress (%)', 'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'], errors='ignore')
    df_to_save = df_to_save.fillna("-").astype(str)
    data_list = [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    try:
        response = requests.post(APPS_SCRIPT_URL, json=data_list, timeout=20)
        if response.status_code == 200:
            load_data.clear()
            return True
        return False
    except: return False

def upload_foto_cloud(img_file):
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = { "image": img_file.getvalue() }
    try:
        res = requests.post(url, files=files, timeout=25)
        data = res.json()
        return data['data']['url'] if res.status_code == 200 and 'data' in data else None
    except: return None

def send_auto_email_wa(nopol, status, catatan, kategori, foto_url=None):
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = SENDER_EMAIL, "sidi.purnomo@dso.astra.co.id", f"Update Status Pekerjaan - No Polisi: {nopol}"
        body = f"Update pekerjaan No Polisi {nopol}.\nStatus: {status}\nCatatan: {catatan}"
        if foto_url: body += f"\nFoto: {foto_url}"
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls(); server.login(SENDER_EMAIL, SENDER_APP_PASSWORD); server.send_message(msg); server.quit()
    except: pass

    try:
        pesan_wa = f"Update pekerjaan No Polisi {nopol}.\nStatus: {status}\nCatatan: {catatan}"
        target = (WA_SA_BR if kategori == "Body Repair" else WA_SA_GR) + (WA_ADMIN_PART if status == "Menunggu Part" else [])
        headers = {'Authorization': f"Bearer {WA_API_TOKEN}", 'Content-Type': 'application/json'}
        for number in list(set(target)):
            if number.strip():
                payload = {"to": number.strip(), "media": foto_url, "caption": pesan_wa} if foto_url else {"to": number.strip(), "body": pesan_wa}
                endpoint = "/messages/image" if foto_url else "/messages/text"
                requests.post(f"{WA_API_URL.rstrip('/')}{endpoint}", headers=headers, json=payload, timeout=5)
    except: pass

# ==========================================
# DASHBOARD UTAMA
# ==========================================
st.session_state['df_data'] = get_merged_data()
df = st.session_state['df_data']

# HEADER & NAVIGASI
col_h1, col_h2, col_h3 = st.columns([4, 1, 1])
with col_h1:
    st.markdown(f"<h3 style='color: #1b5e20;'><img src='{DAIHATSU_LOGO_PNG}' style='height: 30px; margin-right: 15px;'> Live Service Dashboard</h3>", unsafe_allow_html=True)
with col_h2:
    if st.button("🔄 REFRESH", use_container_width=True):
        load_data.clear()
        st.rerun()
with col_h3:
    if st.button("LOGOUT", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

menu_pilihan = st.selectbox(
    "Pilih Halaman:", 
    ["📊 SEMUA WIP", "🛠️ ANTREAN GR", "📝 UPDATE GR", "🔨 ANTREAN BR", "📝 UPDATE BR", "✅ RIWAYAT SELESAI", "➕ TAMBAH MOBIL TAMU"]
)

# METRICS
df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Unit WIP", f"{len(df_wip)} Unit")
m2.metric("Antrean GR", f"{len(df_wip[df_wip['Kategori'] == 'General Repair'])} Unit")
m3.metric("Antrean BR", f"{len(df_wip[df_wip['Kategori'] == 'Body Repair'])} Unit")
m4.metric("Unit Selesai", f"{len(df_selesai)} Unit")
st.markdown("<hr>", unsafe_allow_html=True)

def execute_form_logic(selected_nopol, list_nopol, kategori_filter):
    if selected_nopol and selected_nopol in list_nopol:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[-1] 
        kategori_asli = data_kendaraan.get('Kategori', 'General Repair')
        st.success(f"🎯 **{data_kendaraan.get('Nama Customer', '-')}** | {selected_nopol}")
        
        with st.form(f"form_update_{selected_nopol}"):
            opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
            if kategori_asli == "Body Repair":
                opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
            
            curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
            idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
            
            new_status = st.selectbox("Progress Pekerjaan:", opsi_status, index=idx)
            new_ket = st.text_area("Catatan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
            
            foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
            if foto_saat_ini.startswith("http"): st.image(foto_saat_ini, caption="Foto Terakhir", use_column_width=True)
            
            uploaded_foto = st.file_uploader("Upload Foto Baru", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("💾 UPDATE DATA", use_container_width=True):
                link_foto = upload_foto_cloud(uploaded_foto) if uploaded_foto else None
                df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                if link_foto: df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = link_foto
                
                st.session_state['df_data'] = df
                if save_data(df):
                    send_auto_email_wa(selected_nopol, new_status, new_ket, kategori_asli, link_foto or (foto_saat_ini if foto_saat_ini.startswith("http") else None))
                    st.success("✅ Data berhasil diperbarui!")
                    st.rerun()

# RENDER TABLE
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": st.dataframe(df_wip, use_container_width=True, hide_index=True)
    elif menu_pilihan == "🛠️ ANTREAN GR": st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'], use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": execute_form_logic(st.selectbox("Pilih No Polisi", [""] + df[df['Kategori'] == 'General Repair']['No Polisi'].unique().tolist()), df['No Polisi'].tolist(), 'General Repair')
    elif menu_pilihan == "🔨 ANTREAN BR": st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'], use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": execute_form_logic(st.selectbox("Pilih No Polisi", [""] + df[df['Kategori'] == 'Body Repair']['No Polisi'].unique().tolist()), df['No Polisi'].tolist(), 'Body Repair')
    elif menu_pilihan == "✅ RIWAYAT SELESAI": st.dataframe(df_selesai, use_container_width=True, hide_index=True)
else:
    st.info("Loading data atau database masih kosong.")
