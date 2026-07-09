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
            
        return df
    except Exception as e:
        st.error(f"Gagal koneksi ke database: {e}")
        return pd.DataFrame()

def save_data(df):
    df_to_save = df.drop(columns=['Umur PKB (Hari)', 'Aksi Admin Part'], errors='ignore').fillna("-").astype(str)
    data_list = [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    try:
        response = requests.post(APPS_SCRIPT_URL, json=data_list, timeout=20)
        if response.status_code == 200:
            load_data.clear()
            return True
        st.error("Gagal menyimpan data ke Cloud.")
        return False
    except Exception as e:
        st.error(f"Error sinkronisasi: {e}")
        return False

def upload_foto_cloud(img_file):
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = {"image": (img_file.name, img_file.getvalue(), img_file.type)}
    try:
        res = requests.post(url, files=files, timeout=25)
        data = res.json()
        if res.status_code == 200 and 'data' in data: return data['data']['url']
        st.error(f"❌ ImgBB Gagal: {data.get('error', {}).get('message', res.text)}")
    except Exception as e:
        st.error(f"❌ Koneksi upload gagal: {e}")
    return None

# ==========================================
# 📊 LOGIC & STATE PERSISTENCE
# ==========================================
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA", use_container_width=True):
        load_data.clear()
        st.session_state['df_data'] = load_data()
        st.rerun()
    if st.button("🚪 LOGOUT", use_container_width=True):
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

# Header Horizontal
st.markdown(f"""
    <div class='header-horizontal' style='margin-bottom: 15px;'>
        <img src='{DAIHATSU_LOGO_PNG}' style='height: 28px; margin-right: 12px;'>
        <h2 style='margin: 0; font-size: 22px; font-weight: bold;'>Live Service Dashboard</h2>
    </div>
""", unsafe_allow_html=True)

# Pisahkan Data
df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

# Tampilkan Metrik Secara Horizontal Menggunakan HTML/CSS Custom
wip_count = len(df_wip)
gr_count = len(df_wip[df_wip['Kategori'] == 'General Repair']) if 'Kategori' in df_wip.columns else 0
br_count = len(df_wip[df_wip['Kategori'] == 'Body Repair']) if 'Kategori' in df_wip.columns else 0
selesai_count = len(df_selesai)

st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-title">🔴 Total WIP</div>
            <div class="metric-value">{wip_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">🔧 Antrean GR</div>
            <div class="metric-value">{gr_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">🔨 Antrean BR</div>
            <div class="metric-value">{br_count}</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">✅ Selesai</div>
            <div class="metric-value">{selesai_count}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

def render_update_form(kategori_filter):
    kategori_label = kategori_filter if kategori_filter else "Semua Kategori"
    st.markdown(f"#### 🔎 Pencarian Kendaraan ({kategori_label})")
    
    if df.empty: return st.warning("Data database kosong atau gagal dimuat.")
    if 'No Polisi' not in df.columns: return st.error("Kolom 'No Polisi' tidak ditemukan.")

    # Filter Kategori jika diperlukan
    df_filter = df[df['Kategori'] == kategori_filter] if kategori_filter else df
    list_nopol = df_filter['No Polisi'].dropna().unique().tolist()
    
    metode_cari = st.radio("Metode Pencarian:", ["Pilih dari List", "Ketik Manual"], horizontal=True)
    if metode_cari == "Pilih dari List":
        selected_nopol = st.selectbox("Pilih No Polisi", [""] + list_nopol)
    else:
        selected_nopol = st.text_input("Ketik No Polisi (Tanpa Spasi)").strip().upper()

    if selected_nopol and selected_nopol in list_nopol:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[0]
        nama_cust = data_kendaraan.get('Nama Customer', '-')
        tipe_kend = data_kendaraan.get('Tipe Kendaraan', '-')
        kat_kend = data_kendaraan.get('Kategori', 'General Repair')
        
        st.success(f"🎯 Data: **{nama_cust}** | **{selected_nopol}** | **{tipe_kend}**")
        
        with st.form("form_update_data"):
            c1, c2 = st.columns(2)
            with c1:
                if kat_kend == "Body Repair":
                    opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
                else:
                    opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
                
                curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
                idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
                new_status = st.selectbox("Progress Baru:", opsi_status, index=idx)
                new_ket = st.text_area("Keterangan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
            
            with c2:
                foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
                if foto_saat_ini.startswith("http"): 
                    st.image(foto_saat_ini, caption="📸 Foto Terakhir di Server", use_container_width=True)
                else:
                    st.warning("⚠️ Belum ada foto online.")
                
                uploaded_foto = st.file_uploader("Upload Bukti Baru (Cloud)", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("💾 UPDATE DATA KE SERVER", use_container_width=True):
                upload_sukses = True
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
                    
                    with st.spinner("Menyinkronkan data dengan Google Sheets..."):
                        if save_data(df):
                            st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} berhasil diperbarui!"
                            st.rerun()
                else:
                    st.error("🛑 Sinkronisasi dibatalkan. Gagal mengunggah foto.")

# Logic Menu Render
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        # Tambahkan logika Link Notifikasi ke Admin Part khusus yang statusnya "Menunggu Part"
        if 'Status Pekerjaan' in df_wip.columns and 'No Polisi' in df_wip.columns:
            # Menggunakan WA Link. Jika ingin Email ubah ke: mailto:{EMAIL_ADMIN_PART}?subject=Info Part {x['No Polisi']}
            df_wip['Aksi Admin Part'] = df_wip.apply(
                lambda x: f"https://wa.me/{NO_WA_ADMIN_PART}?text=Halo%20Admin%20Part,%20mohon%20info%20ketersediaan%20part%20untuk%20kendaraan%20dengan%20No%20Polisi:%20{x['No Polisi']}" if x['Status Pekerjaan'] == 'Menunggu Part' else "-", 
                axis=1
            )
        
        st.dataframe(
            df_wip.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []),
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Aksi Admin Part": st.column_config.LinkColumn("Hubungi Admin (Klik)", display_text="Chat Admin Part")
            }
        )
    elif menu_pilihan == "🛠️ ANTREAN GR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": 
        render_update_form("General Repair")
    elif menu_pilihan == "🔨 ANTREAN BR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": 
        render_update_form("Body Repair")
    elif menu_pilihan == "📱 TAMPILAN HP":
        # Render form tanpa filter (Gabungan GR & BR, ideal untuk mekanik/SA di HP)
        render_update_form(None)
    elif menu_pilihan == "✅ RIWAYAT SELESAI": 
        st.dataframe(df_selesai.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_selesai.columns else []), use_container_width=True, hide_index=True)
else:
    st.info("Loading data atau data masih kosong.")
