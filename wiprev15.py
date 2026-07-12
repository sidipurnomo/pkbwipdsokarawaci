import streamlit as st
import pandas as pd
import time
import requests
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# ==========================================
# KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw3_oAXnBuqUHwYAQDdlka4jfJY2bv8JTb--dTOK9giH1X-PIVEpFE0r4vgugs2YsggNQ/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

# Konfigurasi Notifikasi Otomatis
SENDER_EMAIL = "sidi.purnomo@dso.astra.co.id"
SENDER_APP_PASSWORD = "Bu***@07" # Ingat untuk mengganti dengan password asli Anda
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
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# CSS STYLING
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
    
    div[role="radiogroup"] { width: 100% !important; }
    div[role="radiogroup"] > label {
        background-color: #f1f8e9 !important; color: #1b5e20 !important; 
        padding: 12px 15px !important; border-radius: 10px; margin-bottom: 12px;
        border: 1px solid #dcedc8; border-bottom: 5px solid #aed581; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05); cursor: pointer; 
        width: 100% !important; display: block !important; box-sizing: border-box !important;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-3px); border-bottom: 7px solid #7cb342; 
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] {
        width: 100% !important; display: block !important;
    }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: 800 !important; margin: 0 !important; 
        text-align: left !important; white-space: nowrap !important;
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
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEM LOGIN & AUTO LOGOUT
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
        
        # PERBAIKAN: Mengganti use_container_width=True dengan width="stretch"
        if st.form_submit_button("LOGIN KE SISTEM", width="stretch"):
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
# SIDEBAR MENU KIRI
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
        if response.status_code != 200:
            return pd.DataFrame()
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
    except Exception as e:
        st.error(f"Gagal koneksi ke database Cloud: {e}")
        return pd.DataFrame()

def get_merged_data():
    new_df = load_data()
    if 'df_data' in st.session_state and st.session_state['df_data'] is not None:
        old_df = st.session_state['df_data']
        if not new_df.empty and not old_df.empty and 'No Polisi' in old_df.columns and 'Status Pekerjaan' in old_df.columns:
            old_status_map = dict(zip(old_df['No Polisi'], old_df['Status Pekerjaan']))
            if 'Status Pekerjaan' in new_df.columns:
                new_df['Status Pekerjaan'] = new_df.apply(
                    lambda row: old_status_map.get(row['No Polisi'], row['Status Pekerjaan']), 
                    axis=1
                )
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
        else:
            st.error(f"Gagal menyimpan data ke Cloud. Status Code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error sinkronisasi ke Cloud: {e}")
        return False

def upload_foto_cloud(img_file):
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = { "image": (img_file.name, img_file.getvalue(), img_file.type) }
    try:
        res = requests.post(url, files=files, timeout=25)
        data = res.json()
        if res.status_code == 200 and 'data' in data:
            return data['data']['url']
        return None
    except Exception:
        return None

def send_auto_email_wa(nopol, status, catatan, kategori, foto_url=None):
    # Kirim Email
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = "sidi.purnomo@dso.astra.co.id"
        msg['Subject'] = f"Update Status Pekerjaan - No Polisi: {nopol}"
        
        body = f"Berikut update pekerjaan pada kendaraan No Polisi {nopol}.\nStatus: {status}\nCatatan: {catatan}"
        if foto_url and foto_url != "-": body += f"\nFoto Terkini: {foto_url}"
            
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception:
        pass

    # Kirim WA
    try:
        pesan_wa = f"Update pekerjaan kendaraan No Polisi {nopol}.\nStatus: {status}\nCatatan: {catatan}"
        target_numbers = []
        if kategori == "Body Repair": target_numbers.extend(WA_SA_BR)
        elif kategori == "General Repair": target_numbers.extend(WA_SA_GR)
        if status == "Menunggu Part": target_numbers.extend(WA_ADMIN_PART)
            
        headers = {'Authorization': f"Bearer {WA_API_TOKEN}", 'Content-Type': 'application/json'}
        for number in list(set(target_numbers)):
            if number.strip():  
                if foto_url and foto_url != "-":
                    payload = {"to": number.strip(), "media": foto_url, "caption": pesan_wa}
                    requests.post(f"{WA_API_URL.rstrip('/')}/messages/image", headers=headers, json=payload, timeout=5)
                else:
                    payload = {"to": number.strip(), "body": pesan_wa}
                    requests.post(f"{WA_API_URL.rstrip('/')}/messages/text", headers=headers, json=payload, timeout=5)
    except Exception:
        pass

# ==========================================
# DASHBOARD UTAMA
# ==========================================
with st.sidebar:
    st.markdown("---")
    # PERBAIKAN: Mengganti use_container_width=True dengan width="stretch"
    if st.button("🔄 REFRESH DATA", width="stretch"):
        load_data.clear()
        st.session_state['df_data'] = get_merged_data() 
        st.rerun()
    if st.button("LOGOUT", width="stretch"):
        st.session_state['logged_in'] = False
        st.rerun()

st.session_state['df_data'] = get_merged_data()
df = st.session_state['df_data']

def style_umur_pkb(val):
    try:
        if int(val) > 60: return 'color: #ff4b4b; font-weight: bold;'
    except: pass
    return ''

if 'notif_sukses' in st.session_state:
    st.success(st.session_state['notif_sukses'])
    del st.session_state['notif_sukses']

st.markdown(f"<h3 class='main-header' style='text-align: left; display: flex; align-items: center; color: #1b5e20;'><img src='{DAIHATSU_LOGO_PNG}' style='height: 30px; margin-right: 15px;'> Live Service Dashboard</h3>", unsafe_allow_html=True)

df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Total Unit WIP", value=f"{len(df_wip)} Unit")
if not df_wip.empty and 'Kategori' in df_wip.columns:
    m2.metric(label="Antrean GR", value=f"{len(df_wip[df_wip['Kategori'] == 'General Repair'])} Unit")
    m3.metric(label="Antrean BR", value=f"{len(df_wip[df_wip['Kategori'] == 'Body Repair'])} Unit")
else:
    m2.metric(label="Antrean GR", value="0 Unit")
    m3.metric(label="Antrean BR", value="0 Unit")
m4.metric(label="Unit Selesai", value=f"{len(df_selesai)} Unit")
st.markdown("<hr style='border: 1px solid #dcedc8; margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

def execute_form_logic(selected_nopol, list_nopol, kategori_filter):
    if selected_nopol and selected_nopol in list_nopol:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[-1] 
        kategori_asli = data_kendaraan.get('Kategori', 'General Repair')
        
        st.success(f"🎯 **{data_kendaraan.get('Nama Customer', '-')}** | {selected_nopol} | {data_kendaraan.get('Tipe Kendaraan', '-')}")
        
        with st.form(f"form_update_{selected_nopol}"):
            st.markdown("**📌 Status & Keterangan**")
            
            opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
            if kategori_asli == "Body Repair":
                opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
            
            curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
            idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
            
            new_status = st.selectbox("Progress Pekerjaan:", opsi_status, index=idx, key=f"status_{selected_nopol}")
            new_ket = st.text_area("Catatan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')), key=f"ket_{selected_nopol}")
            
            st.markdown("**📸 Foto Kondisi Kendaraan**")
            foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
            
            # PERBAIKAN: Mengganti use_container_width=True dengan width="stretch"
            if foto_saat_ini.startswith("http"): 
                st.image(foto_saat_ini, caption="Foto Terakhir", width="stretch")
            
            uploaded_foto = st.file_uploader("Upload Foto Baru", type=['jpg', 'jpeg', 'png'], key=f"foto_{selected_nopol}")

            # PERBAIKAN: Mengganti use_container_width=True dengan width="stretch"
            if st.form_submit_button("💾 UPDATE DATA", width="stretch"):
                upload_sukses = True
                link_foto = None
                
                if uploaded_foto is not None:
                    with st.spinner("Mengupload foto..."):
                        link_foto = upload_foto_cloud(uploaded_foto)
                        if link_foto: df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = link_foto
                        else: upload_sukses = False 
                
                if upload_sukses:
                    df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                    df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                    df.loc[df['No Polisi'] == selected_nopol, 'Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    st.session_state['df_data'] = df
                    with st.spinner("Menyinkronkan ke Cloud..."):
                        sukses = save_data(df)
                    
                    if sukses:
                        foto_terbaru = link_foto if link_foto else (foto_saat_ini if foto_saat_ini.startswith("http") else None)
                        send_auto_email_wa(selected_nopol, new_status, new_ket, kategori_asli, foto_terbaru)
                        st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} diperbarui!"
                        st.rerun()
                else:
                    st.error("🛑 Gagal menyimpan karena error unggah foto.")

# PERBAIKAN: Mengganti use_container_width=True dengan width="stretch" pada semua dataframe
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        st.dataframe(df_wip.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), width="stretch", hide_index=True)
    elif menu_pilihan == "🛠️ ANTREAN GR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'], width="stretch", hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": 
        list_nopol = df[df['Kategori'] == 'General Repair']['No Polisi'].dropna().unique().tolist()
        execute_form_logic(st.selectbox("Pilih No Polisi", [""] + list_nopol, key="sel_gr"), list_nopol, 'General Repair')
    elif menu_pilihan == "🔨 ANTREAN BR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'], width="stretch", hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": 
        list_nopol = df[df['Kategori'] == 'Body Repair']['No Polisi'].dropna().unique().tolist()
        execute_form_logic(st.selectbox("Pilih No Polisi", [""] + list_nopol, key="sel_br"), list_nopol, 'Body Repair')
    elif menu_pilihan == "✅ RIWAYAT SELESAI": 
        st.dataframe(df_selesai, width="stretch", hide_index=True)
else:
    st.info("Loading data atau database masih kosong.")
