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
# 🎨 CSS STYLING (HIJAU MUDA & MOBILE RESPONSIVE)
# ==========================================
st.markdown("""
<style>
    /* Background utama aplikasi */
    .stApp { background-color: #f7fdf7 !important; }
    
    /* Warna tulisan di sidebar */
    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"], [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, 
        [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #2e7d32 !important; }
    }
    
    /* Styling Tombol (Warna Hijau) */
    div.stButton > button {
        border-radius: 8px; border: 1px solid #4caf50; background-color: transparent;
        color: #2e7d32; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(76, 175, 80, 0.4); background-color: #4caf50;
        color: white; transform: scale(1.02);
    }
    
    [data-testid="stSidebar"] { font-size: 1.15rem !important; }
    
    /* Styling Radio Button / Menu Pilihan */
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
    
    /* Styling Metrik / Bubble Info (Hijau Muda Nyaman) */
    div[data-testid="metric-container"] {
        background-color: #e8f5e9 !important; border-radius: 12px; padding: 15px 15px;
        border: 1px solid #c8e6c9; border-bottom: 6px solid #81c784; 
        box-shadow: 0px 4px 0px #4caf50, 0px 6px 10px rgba(0,0,0,0.1);
    }
    div[data-testid="metric-container"] label { color: #2e7d32 !important; font-weight: bold; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1b5e20 !important; }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px); box-shadow: 0px 6px 0px #388e3c;
    }
    
    /* Header Glowing Hijau */
    .title-glowing {
        text-align: center; color: #2e7d32; text-shadow: 2px 2px 4px rgba(76, 175, 80, 0.3);
        font-family: 'Arial Black', sans-serif; display: flex; justify-content: center; align-items: center;
        flex-wrap: wrap; /* Agar aman di HP */
    }
    
    /* 📱 OVERRIDE KHUSUS TAMPILAN HORIZONTAL DI HP */
    @media (max-width: 768px) {
        /* Memaksa baris metrik menjadi horizontal scrollable */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch; /* Smooth scroll on iOS */
            padding-bottom: 15px; /* Spasi untuk scrollbar */
        }
        /* Mengunci lebar minimum agar bubble tidak gepeng */
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            min-width: 140px !important; 
            flex: 0 0 auto !important; 
        }
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
    st.markdown("<h3 style='text-align:center; color:#2e7d32;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)
    menu_pilihan = st.radio(
        "Pilih Halaman:", 
        ["📊 SEMUA WIP", "📱 TAMPILAN MOBILE", "🛠️ ANTREAN GR", "📝 UPDATE GR", "🔨 ANTREAN BR", "📝 UPDATE BR", "✅ RIWAYAT SELESAI"], 
        label_visibility="collapsed"
    )
    
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
    df_to_save = df.drop(columns=['Umur PKB (Hari)', 'Aksi WA Part', 'Aksi Email Part'], errors='ignore')
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
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = { "image": (img_file.name, img_file.getvalue(), img_file.type) }
    
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
        st.error(f"❌ Gagal upload foto ke Cloud: {e}")
    return None

# ==========================================
# 📊 DASHBOARD & APP LOGIC
# ==========================================
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", use_container_width=True):
        load_data.clear()
        st.session_state['df_data'] = load_data()
        st.rerun()
    if st.button("🚪 LOGOUT SISTEM", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()

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

st.markdown(f"<h3 style='text-align: left; display: flex; align-items: center; color: #1b5e20;'><img src='{DAIHATSU_LOGO_PNG}' style='height: 30px; margin-right: 15px;'> Live Service Dashboard</h3>", unsafe_allow_html=True)

df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

# Tampilkan Metrik Horizontal
m1, m2, m3, m4 = st.columns(4)
m1.metric(label="Total Unit WIP", value=f"{len(df_wip)} Unit")
if not df_wip.empty and 'Kategori' in df_wip.columns:
    m2.metric(label="Antrean GR", value=f"{len(df_wip[df_wip['Kategori'] == 'General Repair'])} Unit")
    m3.metric(label="Antrean BR", value=f"{len(df_wip[df_wip['Kategori'] == 'Body Repair'])} Unit")
else:
    m2.metric(label="Antrean GR", value="0 Unit")
    m3.metric(label="Antrean BR", value="0 Unit")
m4.metric(label="Unit Selesai", value=f"{len(df_selesai)} Unit")
st.markdown("<br>", unsafe_allow_html=True)

# Fungsi Render Form General / BR
def render_update_form(kategori_filter):
    st.markdown(f"#### 🔎 Pencarian Kendaraan ({kategori_filter})")
    if df.empty: return st.warning("Database kosong.")
    
    df_kategori = df[df['Kategori'] == kategori_filter]
    list_nopol = df_kategori['No Polisi'].dropna().unique().tolist()
    
    metode_cari = st.radio("Metode:", ["Pilih dari List", "Ketik Manual"], key=f"rad_{kategori_filter}", horizontal=True)
    if metode_cari == "Pilih dari List":
        selected_nopol = st.selectbox("Pilih No Polisi", [""] + list_nopol)
    else:
        selected_nopol = st.text_input("Ketik No Polisi").strip().upper()

    execute_form_logic(selected_nopol, list_nopol, kategori_filter)

# Fungsi Render Khusus Tampilan Handphone (Pencarian Tab & Ringkas)
def render_mobile_form():
    st.markdown("#### 📱 Menu Update Mobile")
    if df.empty: return st.warning("Database kosong.")
    
    list_nopol = df['No Polisi'].dropna().unique().tolist()
    
    tab1, tab2 = st.tabs(["📝 Pilih dari List", "⌨️ Cari Manual"])
    with tab1:
        nopol_list = st.selectbox("Cari No Polisi Kendaraan", [""] + list_nopol, key="mob_list")
    with tab2:
        nopol_man = st.text_input("Ketik No Polisi", key="mob_man").strip().upper()
        
    selected_nopol = nopol_list if nopol_list else nopol_man
    execute_form_logic(selected_nopol, list_nopol, None)

# Logika Form Inti (Dipakai di Desktop & Mobile)
def execute_form_logic(selected_nopol, list_nopol, kategori_filter):
    if selected_nopol and selected_nopol in list_nopol:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[0]
        kategori_asli = data_kendaraan.get('Kategori', 'General Repair')
        
        st.success(f"🎯 **{data_kendaraan.get('Nama Customer', '-')}** | {selected_nopol} | {data_kendaraan.get('Tipe Kendaraan', '-')}")
        
        with st.form(f"form_update_{selected_nopol}"):
            st.markdown("**📌 Status & Keterangan**")
            
            opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
            if kategori_asli == "Body Repair":
                opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
            
            curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
            idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
            
            new_status = st.selectbox("Progress Pekerjaan:", opsi_status, index=idx)
            new_ket = st.text_area("Catatan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
            
            st.markdown("**📸 Foto Kondisi Kendaraan**")
            foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
            if foto_saat_ini.startswith("http"): 
                st.image(foto_saat_ini, caption="Foto Terakhir", use_container_width=True)
            
            uploaded_foto = st.file_uploader("Upload Foto Baru (Simpan ke Cloud)", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("💾 UPDATE DATA", use_container_width=True):
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
                        st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} berhasil diperbarui!"
                        st.rerun()
                else:
                    st.error("🛑 Gagal menyimpan karena error unggah foto.")

# Logic Menu Render & Tabel Kolom Aksi
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        # Tambahkan Link Email & WA khusus 'Menunggu Part'
        df_display = df_wip.copy()
        if 'Status Pekerjaan' in df_display.columns:
            # Pesan template dari tim Admin Service ke Admin Part
            nomor_wa_part = "+6289630028860" # GANTI DENGAN NOMOR ADMIN PART ASLI
            email_part = "deny.hermawan@dso.astra.co.id;hendri.yogasaputra@dso.astra.co.id" # GANTI DENGAN EMAIL ASLI
            
            df_display['Aksi WA Part'] = df_display.apply(
                lambda row: f"https://wa.me/{nomor_wa_part}?text=Halo%20Admin%20Part,%20saya%20Admin%20Service.%20Mohon%20info%20ketersediaan/estimasi%20part%20untuk%20kendaraan%20WIP%20No%20Polisi:%20{row['No Polisi']}" if row['Status Pekerjaan'] == 'Menunggu Part' else None, axis=1
            )
            df_display['Aksi Email Part'] = df_display.apply(
                lambda row: f"mailto:{email_part}?subject=Follow%20Up%20Part%20WIP%20-%20{row['No Polisi']}&body=Halo%20Tim%20Part,%0A%0AMohon%20bantuannya%20untuk%20update%20status%20part%20kendaraan%20dengan%20No%20Polisi:%20{row['No Polisi']}.%0A%0ATerima%20kasih." if row['Status Pekerjaan'] == 'Menunggu Part' else None, axis=1
            )
            
        st.dataframe(
            df_display.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_display.columns else []), 
            use_container_width=True, hide_index=True,
            column_config={
                "Aksi WA Part": st.column_config.LinkColumn("Hubungi via WA", display_text="💬 Chat Admin Part"),
                "Aksi Email Part": st.column_config.LinkColumn("Hubungi via Email", display_text="📧 Email Admin Part")
            }
        )
    elif menu_pilihan == "📱 TAMPILAN MOBILE":
        render_mobile_form()
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
    st.info("Loading data atau database masih kosong.")
