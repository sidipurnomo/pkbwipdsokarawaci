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
# 🌟 KONFIGURASI HALAMAN (Harus paling atas)
# ==========================================
DAIHATSU_LOGO_PNG = "https://images.seeklogo.com/logo-png/3/1/daihatsu-logo-png_seeklogo-38135.png"
st.set_page_config(
    page_title="PKB WIP DSO KARAWACI", 
    page_icon=DAIHATSU_LOGO_PNG, 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ==========================================
# 🌟 KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbz_uF5eFhIEqIpOvFh743QSzaDMItK2Npbdc4qcoGERdHM_R5Da-CvERDg7RbNampxysw/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

# Konfigurasi Notifikasi Otomatis
SENDER_EMAIL = "sidi.purnomo@dso.astra.co.id"
SENDER_APP_PASSWORD = "Bulan@07" # App Password / Password Email
WA_API_URL = "https://gate.whapi.cloud/" # Base URL Whapi Cloud
WA_API_TOKEN = "CIgRwaeFa1cvnYaWH1RtBL6taXQi3vcq"

WA_SA_BR = ["6281399211266", "6285600199590"] 
WA_SA_GR = ["6281366664391", "6283893470438", "628558825962", "6287774134574"] 
WA_ADMIN_PART = ["6289630028860", "6285888874700"] 

# ==========================================
# 🎨 CSS STYLING
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
        border-radius: 35px !important; padding: 20px 10px !important;
        border: 2px solid #aed581 !important; text-align: center !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.08) !important;
    }
    div[data-testid="metric-container"] label { color: #2e7d32 !important; font-weight: 800 !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1b5e20 !important; font-weight: 900 !important; }
    .title-glowing { text-align: center; color: #2e7d32; text-shadow: 2px 2px 4px rgba(76, 175, 80, 0.3); font-family: 'Arial Black', sans-serif; }
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
        time.sleep(2) 
        st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 class='title-glowing'><img src='{DAIHATSU_LOGO_PNG}' style='height: 40px; margin-right: 15px;'> PKB WIP DSO KARAWACI</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<h3 style='text-align: center;'>🔐 Login Dashboard</h3>", unsafe_allow_html=True)
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
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
# 🚪 SIDEBAR MENU KIRI
# ==========================================
with st.sidebar:
    st.markdown(f"<div style='text-align: center;'><img src='{DAIHATSU_LOGO_PNG}' style='width: 120px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#2e7d32;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)
    menu_pilihan = st.radio(
        "Pilih Halaman:", 
        ["📊 SEMUA WIP", "📱 TAMPILAN MOBILE", "🛠️ ANTREAN GR", "📝 UPDATE GR", "🔨 ANTREAN BR", "📝 UPDATE BR", "✅ RIWAYAT SELESAI", "➕ TAMBAH MOBIL TAMU", "📥 UPLOAD DATA BARU"], 
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

@st.cache_data(ttl=20) 
def load_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=20)
        # Proteksi jika Google Apps Script merespon error HTML bukan JSON
        if response.status_code != 200:
            st.error(f"⚠️ Gagal menarik data dari Google Cloud (Status: {response.status_code})")
            return pd.DataFrame()
        
        data = response.json()
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        if 'No Polisi' in df.columns:
            df = df.drop_duplicates(subset=['No Polisi'], keep='last').reset_index(drop=True)

        kolom_wajib = ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']
        for col in kolom_wajib:
            if col not in df.columns: df[col] = "-"
        
        # Penataan Posisi Kolom
        if 'No PKB' in df.columns and 'Tipe Kendaraan' in df.columns:
            cols = list(df.columns)
            cols.remove('Tipe Kendaraan') 
            cols.insert(cols.index('No PKB') + 1, 'Tipe Kendaraan') 
            df = df[cols] 
            
        # Kalkulasi Umur PKB
        if 'Tgl PKB' in df.columns:
            df['Tgl PKB'] = pd.to_datetime(df['Tgl PKB'], errors='coerce').dt.tz_localize(None)
            now = pd.Timestamp.now().normalize()
            df['Umur PKB (Hari)'] = (now - df['Tgl PKB']).dt.days.fillna(0).astype(int)
            df['Tgl PKB'] = df['Tgl PKB'].dt.strftime('%Y-%m-%d').fillna("-")
            
            cols = list(df.columns)
            if 'Umur PKB (Hari)' in cols and 'Tgl PKB' in cols:
                cols.remove('Umur PKB (Hari)')
                cols.insert(cols.index('Tgl PKB') + 1, 'Umur PKB (Hari)')
                df = df[cols]
                
        # Kalkulasi Progress
        if 'Kategori' in df.columns and 'Status Pekerjaan' in df.columns:
            df['Progress (%)'] = df.apply(lambda row: hitung_progress(row['Kategori'], row['Status Pekerjaan']), axis=1)

        return df
    except requests.exceptions.JSONDecodeError:
        st.error("⚠️ Koneksi ke Google Apps Script bermasalah (JSON Decode Error). Cek URL Apps Script.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Error koneksi database: {e}")
        return pd.DataFrame()

def save_data(df):
    df_to_save = df.drop(columns=['Umur PKB (Hari)', 'Progress (%)', 'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'], errors='ignore')
    # Proteksi Format: Pastikan seluruh tipe data adalah string agar JSON Serialize di Requests tidak gagal (NaN / NaT issue)
    df_to_save = df_to_save.fillna("-").astype(str) 
    data_list = [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    
    try:
        response = requests.post(APPS_SCRIPT_URL, json=data_list, timeout=25)
        if response.status_code == 200:
            load_data.clear() # Bersihkan cache streamlit
            return True
        else:
            st.error(f"⚠️ Gagal menyimpan ke Cloud. Status Code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Koneksi internet terputus saat menyimpan ke Cloud: {e}")
        return False
    except Exception as e:
        st.error(f"⚠️ Error tak terduga saat sinkronisasi Cloud: {e}")
        return False

def upload_foto_cloud(img_file):
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    files = { "image": (img_file.name, img_file.getvalue(), img_file.type) }
    try:
        res = requests.post(url, files=files, timeout=30)
        data = res.json()
        if res.status_code == 200 and 'data' in data:
            return data['data']['url']
        else:
            st.error(f"❌ ImgBB Menolak Upload: {data.get('error', {}).get('message', res.text)}")
            return None
    except Exception as e:
        st.error(f"❌ Koneksi terputus saat upload foto: {e}")
    return None

def send_auto_email_wa(nopol, status, catatan, kategori, foto_url=None):
    latest_foto = None
    all_fotos = []
    if foto_url and foto_url != "-":
        all_fotos = [f.strip() for f in foto_url.split("|") if f.strip().startswith("http")]
        if all_fotos:
            latest_foto = all_fotos[-1] 

    # --- EMAIL SENDER ---
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = "sidi.purnomo@dso.astra.co.id"
        msg['Subject'] = f"Update Status Pekerjaan Otomatis - No Polisi: {nopol}"
        
        body = f"Selamat siang sahabat,\n\nBerikut update pekerjaan pada kendaraan No Polisi {nopol}.\nStatus Terkini: {status}\nCatatan: {catatan}"
        if all_fotos: body += "\n\nLampiran Foto (Riwayat Terkini):\n" + "\n".join(all_fotos)
        body += "\n\nSalam,\nAdmin Service."
        
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"❌ Gagal mengirim email: {e}")

    # --- WA WHAPI CLOUD ---
    try:
        pesan_wa = f"Selamat Siang Sahabat, Berikut update pekerjaan pada kendaraan {nopol}.\nStatus Terkini: {status}\nCatatan: {catatan}"
        if len(all_fotos) > 1: pesan_wa += f"\n*(Terdapat {len(all_fotos)} riwayat foto di sistem)*"

        target_numbers = WA_SA_BR if kategori == "Body Repair" else WA_SA_GR
        if status == "Menunggu Part": target_numbers.extend(WA_ADMIN_PART)
        target_numbers = list(set(target_numbers))
        
        headers = {'Authorization': f"Bearer {WA_API_TOKEN}", 'Content-Type': 'application/json'}
        for number in target_numbers:
            if number.strip():  
                payload = {"to": number.strip(), "caption": pesan_wa, "media": latest_foto} if latest_foto else {"to": number.strip(), "body": pesan_wa}
                endpoint = f"{WA_API_URL.rstrip('/')}/messages/image" if latest_foto else f"{WA_API_URL.rstrip('/')}/messages/text"
                requests.post(endpoint, headers=headers, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Gagal mengirim WA: {e}")

# ==========================================
# 📊 DASHBOARD & APP LOGIC
# ==========================================
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", use_container_width=True):
        load_data.clear()
        st.session_state['df_data'] = get_merged_data() 
        st.rerun()
    if st.button("LOGOUT", use_container_width=True):
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

def render_mobile_form():
    st.markdown("#### 📱 Menu Update Mobile")
    if df.empty: return st.warning("Database kosong.")
    
    list_nopol = df['No Polisi'].dropna().unique().tolist()
    
    tab1, tab2 = st.tabs(["📝 Pilih dari List", "⌨️ Cari Manual"])
    with tab1: nopol_list = st.selectbox("Cari No Polisi Kendaraan", [""] + list_nopol, key="mob_list")
    with tab2: nopol_man = st.text_input("Ketik No Polisi", key="mob_man").strip().upper()
        
    selected_nopol = nopol_list if nopol_list else nopol_man
    execute_form_logic(selected_nopol, list_nopol, None)

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
            
            new_status = st.selectbox("Progress Pekerjaan:", opsi_status, index=idx)
            new_ket = st.text_area("Catatan Tambahan:", value=str(data_kendaraan.get('Keterangan Lanjutan', '-')))
            
            st.markdown("**📸 Foto Kondisi Kendaraan (Riwayat Folder)**")
            foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
            
            # FITUR MENAMPILKAN MULTIPLE FOTO LAMA (FOLDER)
            if foto_saat_ini != "-" and "http" in foto_saat_ini:
                st.caption("Album Foto Tersimpan:")
                list_foto_lama = [f.strip() for f in foto_saat_ini.split("|") if f.strip().startswith("http")]
                kolom_foto = st.columns(min(len(list_foto_lama), 4) if len(list_foto_lama) > 0 else 1)
                for i, url_f in enumerate(list_foto_lama):
                    kolom_foto[i % 4].image(url_f, caption=f"Foto {i+1}", use_container_width=True)
            else:
                st.caption("Belum ada foto yang tersimpan.")
            
            st.markdown("---")
            uploaded_fotos = st.file_uploader("Upload Foto Baru (Bisa lebih dari 1 file)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

            if st.form_submit_button("💾 UPDATE DATA", use_container_width=True):
                if kategori_asli == "Body Repair" and not uploaded_fotos and (foto_saat_ini == "-" or foto_saat_ini == ""):
                    st.error("🛑 GAGAL UPDATE: Kategori Body Repair DIWAJIBKAN mengunggah minimal 1 foto kendaraan!")
                else:
                    upload_sukses = True
                    new_links_array = []
                    
                    if uploaded_fotos:
                        with st.spinner("Mengupload semua foto ke Cloud (ImgBB)..."):
                            for foto in uploaded_fotos:
                                link_terupload = upload_foto_cloud(foto)
                                if link_terupload:
                                    new_links_array.append(link_terupload)
                                else:
                                    upload_sukses = False 
                    
                    if upload_sukses:
                        kumpulan_foto_final = foto_saat_ini
                        if new_links_array:
                            string_foto_baru = " | ".join(new_links_array)
                            if kumpulan_foto_final != "-" and kumpulan_foto_final != "":
                                kumpulan_foto_final = kumpulan_foto_final + " | " + string_foto_baru
                            else:
                                kumpulan_foto_final = string_foto_baru
                                
                        df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                        df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                        df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = kumpulan_foto_final
                        df.loc[df['No Polisi'] == selected_nopol, 'Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.session_state['df_data'] = df
                        with st.spinner("Menyinkronkan ke Database Cloud..."):
                            sukses = save_data(df)
                        
                        if sukses:
                            send_auto_email_wa(selected_nopol, new_status, new_ket, kategori_asli, kumpulan_foto_final)
                            st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} berhasil diperbarui beserta folder foto! Email/WA terkirim otomatis."
                            st.rerun()
                    else:
                        st.error("🛑 Gagal menyimpan karena terjadi error koneksi saat unggah foto.")

if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        df_display = df_wip.copy()
        column_configs = {
            "Aksi WA Part 1": st.column_config.LinkColumn("Hubungi WA 1", display_text="💬 Chat Part 1"),
            "Aksi WA Part 2": st.column_config.LinkColumn("Hubungi WA 2", display_text="💬 Chat Part 2"),
            "Aksi Email Part": st.column_config.LinkColumn("Hubungi via Email", display_text="📧 Email Admin Part")
        }
        if 'Progress (%)' in df_display.columns:
            column_configs["Progress (%)"] = st.column_config.ProgressColumn("Persentase Selesai", help="Bar Progress Status Pekerjaan", format="%d%%", min_value=0, max_value=100)

        st.dataframe(df_display.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_display.columns else []), use_container_width=True, hide_index=True, column_config=column_configs)
    
    elif menu_pilihan == "📱 TAMPILAN MOBILE": render_mobile_form()
    elif menu_pilihan == "🛠️ ANTREAN GR": st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": render_update_form("General Repair")
    elif menu_pilihan == "🔨 ANTREAN BR": st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), use_container_width=True, hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": render_update_form("Body Repair")
    elif menu_pilihan == "✅ RIWAYAT SELESAI": st.dataframe(df_selesai.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_selesai.columns else []), use_container_width=True, hide_index=True)
        
    elif menu_pilihan == "➕ TAMBAH MOBIL TAMU":
        st.markdown("#### 🚗 Input Kendaraan Tamu / Manual")
        st.info("Fitur ini digunakan untuk memasukkan kendaraan yang belum terdaftar PKB (Non-PKB).")
        
        with st.form("form_input_tamu"):
            c1, c2 = st.columns(2)
            with c1:
                nopol_baru = st.text_input("No Polisi *").strip().upper()
                tipe_baru = st.text_input("Tipe Kendaraan *").strip()
                kategori_baru = st.selectbox("Kategori Pekerjaan", ["General Repair", "Body Repair"])
            with c2:
                warna_baru = st.text_input("Warna Kendaraan").strip()
                foto_baru = st.file_uploader("Upload Foto Kendaraan", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            
            st.markdown("*Wajib diisi")
            if st.form_submit_button("💾 SIMPAN DATA KENDARAAN", use_container_width=True):
                if not nopol_baru or not tipe_baru:
                    st.error("⚠️ No Polisi dan Tipe Kendaraan wajib diisi!")
                else:
                    link_foto = "-"
                    upload_sukses = True
                    
                    if foto_baru:
                        with st.spinner("Mengupload foto..."):
                            kumpulan_link = []
                            for fb in foto_baru:
                                link = upload_foto_cloud(fb)
                                if link: kumpulan_link.append(link)
                                else: upload_sukses = False
                            
                            if kumpulan_link: link_foto = " | ".join(kumpulan_link)
                    
                    if upload_sukses:
                        new_data = {col: "-" for col in df.columns}
                        gabungan_tipe = f"{tipe_baru} ({warna_baru})" if warna_baru else tipe_baru
                        
                        new_data['No Polisi'] = nopol_baru
                        new_data['Tipe Kendaraan'] = gabungan_tipe
                        new_data['Kategori'] = kategori_baru
                        new_data['Status Pekerjaan'] = "Menunggu Pekerjaan" if kategori_baru == "General Repair" else "Antrian Pekerjaan"
                        new_data['Tgl PKB'] = datetime.now().strftime("%Y-%m-%d")
                        new_data['Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_data['Nama Customer'] = "TAMU / NON-PKB"
                        new_data['No PKB'] = "BELUM ADA"
                        new_data['Foto PKB'] = link_foto
                        
                        df_new_row = pd.DataFrame([new_data])
                        df_updated = pd.concat([df, df_new_row], ignore_index=True)
                        
                        st.session_state['df_data'] = df_updated
                        with st.spinner("Menyinkronkan ke Cloud..."):
                            sukses = save_data(df_updated)
                        
                        if sukses:
                            st.session_state['notif_sukses'] = f"✅ Kendaraan Tamu {nopol_baru} berhasil didaftarkan!"
                            st.rerun()
                    else:
                        st.error("🛑 Gagal menyimpan karena error unggah foto.")
                        
    elif menu_pilihan == "📥 UPLOAD DATA BARU":
        st.markdown("#### 📥 Timpa Database dengan File Baru")
        st.info("PENTING: Gunakan fitur ini untuk mengunggah / update data mentah PKB.\n\n1. **Status Pekerjaan** dan **Foto Lama** akan *dipertahankan* utuh.\n2. Jika ada data lama yang *hilang* (tidak ada di file baru), otomatis akan dipindahkan menjadi **'Selesai'**.")
        
        uploaded_db = st.file_uploader("Upload Excel/CSV Database", type=["xlsx", "csv"])
        if uploaded_db is not None:
            if st.button("🔄 PROSES & TIMPA DATABASE SEKARANG", use_container_width=True):
                with st.spinner("Memproses pergantian dan pencocokan data..."):
                    try:
                        df_baru = pd.read_csv(uploaded_db) if uploaded_db.name.endswith('.csv') else pd.read_excel(uploaded_db)
                            
                        if 'No Polisi' not in df_baru.columns:
                            st.error("❌ Gagal! File yang diupload tidak memiliki kolom 'No Polisi'.")
                        else:
                            df_lama = df.copy()
                            final_rows = []
                            nopol_baru_list = [str(x).strip().upper() for x in df_baru['No Polisi'].dropna().unique()]
                            
                            # 1. Masukkan data baru tapi ambil Status & Foto dari data lama
                            for _, row in df_baru.iterrows():
                                nopol = str(row['No Polisi']).strip().upper()
                                match_lama = df_lama[df_lama['No Polisi'] == nopol]
                                
                                if not match_lama.empty:
                                    data_lama = match_lama.iloc[-1]
                                    row['Status Pekerjaan'] = data_lama.get('Status Pekerjaan', 'Menunggu Pekerjaan')
                                    row['Foto PKB'] = data_lama.get('Foto PKB', '-')
                                    row['Keterangan Lanjutan'] = data_lama.get('Keterangan Lanjutan', '-')
                                else:
                                    row['Status Pekerjaan'] = "Antrian Pekerjaan" if row.get('Kategori', '') == "Body Repair" else "Menunggu Pekerjaan"
                                    row['Foto PKB'] = "-"
                                    
                                final_rows.append(row.to_dict())
                                
                            # 2. Cari mobil lama yang hilang di data baru (Ubah ke Selesai)
                            for _, row_lama in df_lama.iterrows():
                                nopol_lama = str(row_lama['No Polisi']).strip().upper()
                                if nopol_lama not in nopol_baru_list:
                                    row_lama['Status Pekerjaan'] = "Selesai"
                                    final_rows.append(row_lama.to_dict())
                                    
                            df_final = pd.DataFrame(final_rows)
                            
                            for col in ['Nama SA', 'Tipe Kendaraan', 'Tanggal Terakhir Diupdate', 'Keterangan Lanjutan', 'Foto PKB']:
                                if col not in df_final.columns: df_final[col] = "-"
                                    
                            st.session_state['df_data'] = df_final
                            if save_data(df_final):
                                st.success("✅ Database berhasil ditimpa! Data lama yang hilang otomatis masuk ke status 'Selesai'.")
                                time.sleep(3)
                                st.rerun()
                                
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan saat membaca file: {e}")

else:
    st.info("⏳ Memuat data dari Cloud... Jika tidak muncul, pastikan link Google Apps Script sudah benar dan Aktif (Anyone).")
