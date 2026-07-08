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
    .stApp { background-color: #f0f8ff !important; }
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"], [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, 
        [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ff1111 !important; }
    }
    div.stButton > button {
        border-radius: 8px; border: 1px solid #ff4b4b; background-color: transparent;
        color: #ff4b4b; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.6); background-color: #ff4b4b;
        color: white; transform: scale(1.02);
    }
    [data-testid="stSidebar"] { font-size: 1.15rem !important; }
    div[role="radiogroup"] > label {
        background-color: #e3f2fd !important; color: #000000 !important; 
        padding: 10px 5px !important; border-radius: 10px; margin-bottom: 12px;
        border: 1px solid #bbdefb; border-bottom: 5px solid #90caf9; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1); cursor: pointer; white-space: nowrap !important;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-3px); border-bottom: 7px solid #64b5f6; 
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: 800 !important; margin: 0 !important; white-space: nowrap !important;
    }
    div[data-testid="metric-container"] {
        background-color: #fce4ec !important; border-radius: 12px; padding: 15px 20px;
        border: 1px solid #f8bbd0; border-bottom: 6px solid #f48fb1; 
        box-shadow: 0px 4px 0px #f06292, 0px 6px 10px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px); box-shadow: 0px 6px 0px #ec407a;
    }
    .title-glowing {
        text-align: center; color: #ff4b4b; text-shadow: 2px 2px 4px rgba(255, 75, 75, 0.3);
        font-family: 'Arial Black', sans-serif; display: flex; justify-content: center; align-items: center;
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
    st.markdown(f"<h1 class='title-glowing'><img src='{DAIHATSU_LOGO_PNG}' style='height: 50px; margin-right: 20px;'> PKB WIP DSO KARAWACI</h1>", unsafe_allow_html=True)
    
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
    st.markdown(f"<div style='text-align: center;'><img src='{DAIHATSU_LOGO_PNG}' style='width: 140px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>Astra Daihatsu<br>Karawaci</h2>", unsafe_allow_html=True)
    menu_pilihan = st.radio("Pilih Halaman:", ["📊 SEMUA WIP", "🛠️ ANTREAN GR", "📝 UPDATE GR", "🔨 ANTREAN BR", "📝 UPDATE BR", "✅ RIWAYAT SELESAI"], label_visibility="collapsed")
    
    if menu_pilihan != st.session_state['last_menu']:
        st.session_state['last_activity'] = time.time()
        st.session_state['last_menu'] = menu_pilihan

# ==========================================
# 🌐 INTEGRASI DATABASE CLOUD (GOOGLE SHEETS)
# ==========================================
@st.cache_data(ttl=10)
def load_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=15)
        data = response.json()
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Validasi Kolom Kosong (Termasuk 'Tipe Kendaraan')
        kolom_wajib = ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']
        for col in kolom_wajib:
            if col not in df.columns: 
                df[col] = "-"
        
        # Pindahkan 'Tipe Kendaraan' agar berada setelah 'No PKB'
        if 'No PKB' in df.columns and 'Tipe Kendaraan' in df.columns:
            cols = list(df.columns)
            cols.remove('Tipe Kendaraan') 
            idx_no_pkb = cols.index('No PKB') 
            cols.insert(idx_no_pkb + 1, 'Tipe Kendaraan') 
            df = df[cols] 
            
        # Hitung Umur PKB
        if 'Tgl PKB' in df.columns:
            df['Tgl PKB'] = pd.to_datetime(df['Tgl PKB'], errors='coerce')
            df['Tgl PKB'] = df['Tgl PKB'].dt.tz_localize(None)
            now = pd.Timestamp.now().normalize()
            df['Umur PKB (Hari)'] = (now - df['Tgl PKB']).dt.days
            df['Umur PKB (Hari)'] = df['Umur PKB (Hari)'].fillna(0).astype(int)
            df['Tgl PKB'] = df['Tgl PKB'].dt.strftime('%Y-%m-%d').fillna("-")
            
        return df
    except Exception as e:
        st.error(f"Gagal koneksi ke database Cloud: {e}")
        return pd.DataFrame()

def save_data(df):
    """Fungsi untuk menimpa data ke Google Sheets"""
    df_to_save = df.drop(columns=['Umur PKB (Hari)'], errors='ignore')
    df_to_save = df_to_save.fillna("-") 
    df_to_save = df_to_save.astype(str)
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
    """Fungsi upload ke ImgBB dengan format Multipart Form-Data (Paling Stabil)"""
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    
    # Format files ini memaksa ImgBB menerima file sesuai nama, isi biner, dan tipe filenya
    files = {
        "image": (img_file.name, img_file.getvalue(), img_file.type)
    }
    
    try:
        res = requests.post(url, files=files, timeout=25)
        data = res.json()
        if res.status_code == 200 and 'data' in data:
            return data['data']['url']
        else:
            pesan_error = data.get('error', {}).get('message', res.text)
            st.error(f"❌ ImgBB Menolak Upload: {pesan_error}")
            return None
    except Exception as e:
        st.error(f"❌ Gagal upload foto ke Cloud karena koneksi: {e}")
    return None

# ==========================================
# 📊 DASHBOARD & APP LOGIC (STATE PERSISTENCE)
# ==========================================
# Tombol Paksa Sync ulang di paling bawah sidebar
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", use_container_width=True):
        load_data.clear()
        st.session_state['df_data'] = load_data()
        st.rerun()
    if st.button("🚪 LOGOUT SISTEM", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

# Manajemen State agar UI Update Instan
if 'df_data' not in st.session_state or st.session_state['df_data'] is None:
    st.session_state['df_data'] = load_data()

df = st.session_state['df_data']

def style_umur_pkb(val):
    try:
        if int(val) > 60: return 'color: #ff4b4b; font-weight: bold;'
    except: pass
    return ''

if 'notif_sukses' in st.session_state:
    st.success(st.session_state['notif_sukses'])
    del st.session_state['notif_sukses']

st.markdown(f"<h2 style='text-align: left; display: flex; align-items: center;'><img src='{DAIHATSU_LOGO_PNG}' style='height: 35px; margin-right: 15px;'> Live Service Dashboard</h2>", unsafe_allow_html=True)

# Pisahkan Data
df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

# Tampilkan Metrik
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="🔴 Total Unit WIP", value=f"{len(df_wip)} Unit")
if not df_wip.empty and 'Kategori' in df_wip.columns:
    m2.metric(label="🔧 Antrean GR (WIP)", value=f"{len(df_wip[df_wip['Kategori'] == 'General Repair'])} Unit")
    m3.metric(label="🔨 Antrean BR (WIP)", value=f"{len(df_wip[df_wip['Kategori'] == 'Body Repair'])} Unit")
else:
    m2.metric(label="🔧 Antrean GR (WIP)", value="0 Unit")
    m3.metric(label="🔨 Antrean BR (WIP)", value="0 Unit")
m4.metric(label="✅ Selesai", value=f"{len(df_selesai)} Unit")
st.markdown("<br>", unsafe_allow_html=True)

def render_update_form(kategori_filter):
    st.markdown(f"#### 🔎 Pencarian Kendaraan ({kategori_filter})")
    if df.empty: 
        return st.warning("Data database kosong atau gagal dimuat.")
    
    if 'Kategori' not in df.columns or 'No Polisi' not in df.columns:
        return st.error("Kolom 'Kategori' atau 'No Polisi' tidak ditemukan di database.")

    df_kategori = df[df['Kategori'] == kategori_filter]
    list_nopol = df_kategori['No Polisi'].dropna().unique().tolist()
    
    metode_cari = st.radio("Metode:", ["Pilih dari List", "Ketik Manual"], key=f"rad_{kategori_filter}", horizontal=True)
    if metode_cari == "Pilih dari List":
        selected_nopol = st.selectbox("Pilih No Polisi", [""] + list_nopol)
    else:
        selected_nopol = st.text_input("Ketik No Polisi").strip().upper()

    if selected_nopol and selected_nopol in list_nopol:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[0]
        nama_cust = data_kendaraan.get('Nama Customer', '-')
        tipe_kend = data_kendaraan.get('Tipe Kendaraan', '-')
        
        st.success(f"🎯 Data: **{nama_cust}** | **{selected_nopol}** | **{tipe_kend}**")
        
        with st.form(f"form_{kategori_filter}"):
            c1, c2 = st.columns(2)
            with c1:
                opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
                if kategori_filter == "Body Repair":
                    opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
                
                curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
                idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
                new_status = st.selectbox("Progress Baru:", opsi_status, index=idx)
                
                new_ket = st.text_area("Keterangan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
            
            with c2:
                # Membaca link gambar yang sudah ada di memori
                foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
                
                if foto_saat_ini.startswith("http"): 
                    st.image(foto_saat_ini, caption="📸 Foto Terakhir di Server", use_container_width=True)
                    st.markdown(f"🔗 [Buka URL Gambar Penuh]({foto_saat_ini})")
                else:
                    st.warning(f"⚠️ Belum ada foto online. (Data di kolom: '{foto_saat_ini}')")
                
                uploaded_foto = st.file_uploader("Upload Bukti Baru (Simpan ke Cloud)", type=['jpg', 'jpeg', 'png'])

            # Tombol Submit Form
            if st.form_submit_button("💾 UPDATE DATA KE SERVER", use_container_width=True):
                upload_sukses = True
                link_foto = None
                
                if uploaded_foto is not None:
                    with st.spinner("Mengupload foto ke server ImgBB..."):
                        link_foto = upload_foto_cloud(uploaded_foto)
                        if link_foto: 
                            # Simpan link baru ke variabel dataframe sementara
                            df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = link_foto
                        else:
                            upload_sukses = False 
                
                if upload_sukses:
                    # Tulis semua perubahan teks ke variabel dataframe sementara
                    df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                    df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                    df.loc[df['No Polisi'] == selected_nopol, 'Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # TIMPA MEMORI UTAMA DENGAN DATAFRAME YANG SUDAH DIUPDATE (CRITICAL STEP)
                    st.session_state['df_data'] = df
                    
                    # Sinkronisasi / Timpa data ke Google Sheets
                    with st.spinner("Menyinkronkan data dengan Google Sheets..."):
                        sukses = save_data(df)
                        
                    if sukses:
                        st.session_state['notif_sukses'] = f"✅ Data No. Pol {selected_nopol} berhasil diperbarui!"
                        st.rerun()
                else:
                    st.error("🛑 Sinkronisasi Dibatalkan karena gagal mengunggah gambar. Periksa notifikasi error di atas.")

# Logic Menu Render
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        st.dataframe(df_wip.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "🛠️ ANTREAN GR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": 
        render_update_form("General Repair")
    elif menu_pilihan == "🔨 ANTREAN BR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": 
        render_update_form("Body Repair")
    elif menu_pilihan == "✅ RIWAYAT SELESAI": 
        st.dataframe(df_selesai.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_selesai.columns else []), use_container_width=True, hide_index=True)
else:
    st.info("Loading data atau data masih kosong.")
