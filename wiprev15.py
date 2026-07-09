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
# 🌟 KONTAK PIC PART (Sesuaikan dengan data asli)
# ==========================================
PIC_PART_WA = "6281234567890" # Gunakan format 62...
PIC_PART_EMAIL = "admin.part@astra.co.id"

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
# 🎨 CSS STYLING (Diperbarui untuk Mobile & Warna yang Nyaman)
# ==========================================
st.markdown("""
<style>
    /* Menyesuaikan warna background secara dinamis berdasarkan tema Streamlit */
    .stApp { transition: background-color 0.3s ease; }
    
    /* Styling tombol */
    div.stButton > button {
        border-radius: 8px; border: 1px solid #ff4b4b; background-color: transparent;
        color: #ff4b4b; font-weight: bold; transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0px 0px 15px rgba(255, 75, 75, 0.6); background-color: #ff4b4b;
        color: white; transform: scale(1.02);
    }
    
    /* Perbaikan Radio Button agar warna teks menyesuaikan mode terang/gelap */
    div[role="radiogroup"] > label {
        padding: 10px 5px !important; border-radius: 10px; margin-bottom: 8px;
        border: 1px solid var(--primary-color);
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1); cursor: pointer;
    }
    div[role="radiogroup"] > label:hover {
        transform: translateY(-2px); border-color: #ff4b4b;
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: bold !important; margin: 0 !important; white-space: nowrap !important;
    }
    
    /* Container Metrik */
    div[data-testid="metric-container"] {
        border-radius: 12px; padding: 15px 20px;
        border: 1px solid rgba(255, 75, 75, 0.3); border-bottom: 5px solid #ff4b4b; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    
    /* Header Horizontal Responsif */
    .header-container {
        display: flex; align-items: center; justify-content: flex-start;
        flex-wrap: wrap; gap: 15px; margin-bottom: 20px;
    }
    .header-container img { height: 45px; }
    .header-container h2 { margin: 0; color: #ff4b4b; font-family: 'Arial Black', sans-serif; }
    
    @media (max-width: 768px) {
        .header-container { justify-content: center; text-align: center; flex-direction: row; }
        .header-container h2 { font-size: 20px; }
        .header-container img { height: 35px; }
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
        <div class="header-container" style="justify-content: center;">
            <img src='{DAIHATSU_LOGO_PNG}'>
            <h2>PKB WIP DSO KARAWACI</h2>
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
    st.markdown(f"<div style='text-align: center;'><img src='{DAIHATSU_LOGO_PNG}' style='width: 140px; margin-bottom:10px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; margin-top:0;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)
    
    # Menambahkan Menu "📱 UPDATE MOBILE"
    menu_pilihan = st.radio("Pilih Halaman:", [
        "📊 SEMUA WIP", 
        "📱 UPDATE MOBILE", 
        "🛠️ ANTREAN GR", 
        "📝 UPDATE GR", 
        "🔨 ANTREAN BR", 
        "📝 UPDATE BR", 
        "✅ RIWAYAT SELESAI"
    ], label_visibility="collapsed")
    
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
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
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
# 📊 DASHBOARD & APP LOGIC
# ==========================================
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA", use_container_width=True):
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

# Header Horizontal
st.markdown(f"""
    <div class="header-container">
        <img src='{DAIHATSU_LOGO_PNG}'>
        <h2>Live Service Dashboard</h2>
    </div>
""", unsafe_allow_html=True)

df_wip = df[df['Status Pekerjaan'] != 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else df
df_selesai = df[df['Status Pekerjaan'] == 'Selesai'] if not df.empty and 'Status Pekerjaan' in df.columns else pd.DataFrame()

m1, m2, m3, m4 = st.columns(4)
m1.metric(label="🔴 Total Unit WIP", value=f"{len(df_wip)} Unit")
if not df_wip.empty and 'Kategori' in df_wip.columns:
    m2.metric(label="🔧 Antrean GR", value=f"{len(df_wip[df_wip['Kategori'] == 'General Repair'])} Unit")
    m3.metric(label="🔨 Antrean BR", value=f"{len(df_wip[df_wip['Kategori'] == 'Body Repair'])} Unit")
else:
    m2.metric(label="🔧 Antrean GR", value="0 Unit")
    m3.metric(label="🔨 Antrean BR", value="0 Unit")
m4.metric(label="✅ Selesai", value=f"{len(df_selesai)} Unit")
st.markdown("<br>", unsafe_allow_html=True)

def render_update_form(kategori_filter=None, mode_mobile=False):
    if mode_mobile:
        st.markdown("#### 📱 Update Cepat (Mobile View)")
    else:
        st.markdown(f"#### 🔎 Pencarian Kendaraan ({kategori_filter})")
        
    if df.empty: 
        return st.warning("Data database kosong atau gagal dimuat.")
    if 'No Polisi' not in df.columns:
        return st.error("Kolom 'No Polisi' tidak ditemukan di database.")

    # Filter khusus kategori jika tidak di mode mobile
    if not mode_mobile and kategori_filter:
        df_filter = df[df['Kategori'] == kategori_filter]
    else:
        df_filter = df

    list_nopol = df_filter['No Polisi'].dropna().unique().tolist()
    
    if mode_mobile:
        selected_nopol = st.text_input("🔍 Ketik No Polisi (Tanpa Spasi)").strip().upper()
    else:
        metode_cari = st.radio("Metode Pencarian:", ["Pilih dari List", "Ketik Manual"], horizontal=True)
        if metode_cari == "Pilih dari List":
            selected_nopol = st.selectbox("Pilih No Polisi", [""] + list_nopol)
        else:
            selected_nopol = st.text_input("Ketik No Polisi").strip().upper()

    if selected_nopol:
        if selected_nopol in list_nopol:
            data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[0]
            nama_cust = data_kendaraan.get('Nama Customer', '-')
            tipe_kend = data_kendaraan.get('Tipe Kendaraan', '-')
            kategori = data_kendaraan.get('Kategori', 'Umum')
            
            st.success(f"🎯 **{nama_cust}** | **{selected_nopol}** | **{tipe_kend}**")
            
            with st.form(f"form_update_{selected_nopol}"):
                # Opsi Status Dinamis
                opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
                if kategori == "Body Repair":
                    opsi_status = ["Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul", "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan", "Menunggu Part", "Quality Control", "Selesai"]
                
                curr_status = str(data_kendaraan.get('Status Pekerjaan', ''))
                idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0
                
                new_status = st.selectbox("Progress Baru:", opsi_status, index=idx)
                
                if not mode_mobile:
                    new_ket = st.text_area("Keterangan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
                else:
                    new_ket = st.text_input("Keterangan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
                
                # Tampilkan Foto Terakhir
                foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
                if foto_saat_ini.startswith("http"): 
                    st.image(foto_saat_ini, caption="📸 Foto Terakhir", width=250)
                
                uploaded_foto = st.file_uploader("Upload Bukti Baru", type=['jpg', 'jpeg', 'png'])

                if st.form_submit_button("💾 UPDATE DATA", use_container_width=True):
                    upload_sukses = True
                    link_foto = None
                    
                    if uploaded_foto is not None:
                        with st.spinner("Mengupload foto..."):
                            link_foto = upload_foto_cloud(uploaded_foto)
                            if link_foto: 
                                df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = link_foto
                            else:
                                upload_sukses = False 
                    
                    if upload_sukses:
                        df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                        df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                        df.loc[df['No Polisi'] == selected_nopol, 'Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.session_state['df_data'] = df
                        
                        with st.spinner("Menyinkronkan data..."):
                            sukses = save_data(df)
                            
                        if sukses:
                            st.session_state['notif_sukses'] = f"✅ No. Pol {selected_nopol} berhasil diupdate!"
                            st.rerun()
                    else:
                        st.error("🛑 Gagal mengunggah gambar. Update dibatalkan.")
        else:
            st.warning(f"⚠️ Kendaraan dengan Nopol {selected_nopol} tidak ditemukan.")

# Logic Menu Render
if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        # Modifikasi tampilan dataframe khusus WIP untuk menambahkan Tautan Hubungi PIC
        df_display = df_wip.copy()
        
        # Fungsi pembuat Link WhatsApp & Email
        def gen_wa(row):
            if row.get('Status Pekerjaan') == 'Menunggu Part':
                return f"https://wa.me/{PIC_PART_WA}?text=Halo%20PIC%20Part,%20mohon%20info%20ketersediaan%20part%20untuk%20No%20Polisi%20{row['No Polisi']}"
            return None

        def gen_email(row):
            if row.get('Status Pekerjaan') == 'Menunggu Part':
                return f"mailto:{PIC_PART_EMAIL}?subject=Follow%20Up%20Part%20Kendaraan%20{row['No Polisi']}&body=Halo%20Tim%20Part,%0A%0AMohon%20informasi%20mengenai%20status%20part%20untuk%20kendaraan%20dengan%20No%20Polisi:%20{row['No Polisi']}.%0A%0ATerima%20kasih."
            return None

        df_display['Hubungi WA'] = df_display.apply(gen_wa, axis=1)
        df_display['Hubungi Email'] = df_display.apply(gen_email, axis=1)
        
        # Konfigurasi kolom
        col_config = {
            "Hubungi WA": st.column_config.LinkColumn("Chat WA", display_text="📲 WA PIC"),
            "Hubungi Email": st.column_config.LinkColumn("Kirim Email", display_text="📧 Email PIC")
        }
        
        st.dataframe(
            df_display.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_display.columns else []),
            column_config=col_config,
            use_container_width=True, hide_index=True
        )
        
    elif menu_pilihan == "📱 UPDATE MOBILE":
        render_update_form(mode_mobile=True)
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
