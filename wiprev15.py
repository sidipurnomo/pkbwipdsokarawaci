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
# 🌟 KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbw3_oAXnBuqUHwYAQDdlka4jfJY2bv8JTb--dTOK9giH1X-PIVEpFE0r4vgugs2YsggNQ/exec"
IMGBB_API_KEY = "569f395028cc808c2a05e9fd24882084"

SENDER_EMAIL = "emailkamu@gmail.com"
SENDER_APP_PASSWORD = "password_aplikasi_gmail_kamu"
WA_API_URL = "https://gate.whapi.cloud/"
WA_API_TOKEN = "CIgRwaeFa1cvnYaWH1RtBL6taXQi3vcq"

DAIHATSU_LOGO_PNG = "https://images.seeklogo.com/logo-png/3/1/daihatsu-logo-png_seeklogo-38135.png"

st.set_page_config(
    page_title="PKB WIP DSO KARAWACI", 
    page_icon=DAIHATSU_LOGO_PNG, 
    layout="wide", 
    initial_sidebar_state="expanded"
)
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
# 🎨 CSS STYLING (HIJAU MUDA, BUBBLE SIMETRIS & MOBILE RESPONSIVE)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f7fdf7 !important; }
    div.stButton > button { border-radius: 8px; border: 1px solid #4caf50; background-color: transparent; color: #2e7d32; font-weight: bold; }
    div.stButton > button:hover { background-color: #4caf50; color: white; }
    .title-glowing { text-align: center; color: #2e7d32; font-family: 'Arial Black', sans-serif; }
</style>
""", unsafe_allow_html=True)
# ==========================================
# 🔐 SISTEM LOGIN & AUTO LOGOUT
# ==========================================
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

def render_login():
    st.markdown("<h1 class='title-glowing'>PKB WIP DSO KARAWACI</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔑 Password", type="password")
        if st.form_submit_button("LOGIN KE SISTEM", width='stretch'):
            if username == "dsokarawaci" and password == "adminkarawaci":
                st.session_state['logged_in'] = True
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
@st.cache_data(ttl=60) 
def load_data():
    try:
        response = requests.get(APPS_SCRIPT_URL, timeout=10)
        return pd.DataFrame(response.json()) if response.status_code == 200 else pd.DataFrame()
    except:
        return pd.DataFrame()

def save_data(df):
    df_to_save = df.fillna("-").astype(str)
    data_list = [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    try:
        response = requests.post(APPS_SCRIPT_URL, json=data_list, timeout=20)
        return response.status_code == 200
    except:
        return False

def upload_foto_cloud(img_file):
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    try:
        res = requests.post(url, files={"image": (img_file.name, img_file.getvalue(), img_file.type)}, timeout=25)
        return res.json()['data']['url'] if res.status_code == 200 else None
    except:
        return None

# ==========================================
# LOGIKA DASHBOARD
# ==========================================
df = load_data()
menu_pilihan = st.sidebar.radio("Pilih Halaman:", ["📊 SEMUA WIP", "📝 UPDATE GR", "📝 UPDATE BR", "➕ TAMBAH MOBIL"])

if st.sidebar.button("🔄 REFRESH DATA", width='stretch'):
    st.rerun()

st.header(f"{menu_pilihan}")

if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP":
        st.dataframe(df, width='stretch', hide_index=True)
        
    elif menu_pilihan in ["📝 UPDATE GR", "📝 UPDATE BR"]:
        kategori = "General Repair" if "GR" in menu_pilihan else "Body Repair"
        list_nopol = df[df['Kategori'] == kategori]['No Polisi'].dropna().unique().tolist()
        
        selected = st.selectbox("Pilih No Polisi", [""] + list_nopol)
        if selected:
            data = df[df['No Polisi'] == selected].iloc[-1]
            with st.form(f"form_{selected}"):
                new_status = st.selectbox("Status", ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Selesai"], index=0)
                new_ket = st.text_area("Catatan", value=data.get('Keterangan Lanjutan', ''))
                uploaded_foto = st.file_uploader("Upload Foto", type=['jpg', 'png'])
                
                if st.form_submit_button("💾 SIMPAN DATA", width='stretch'):
                    df.loc[df['No Polisi'] == selected, 'Status Pekerjaan'] = new_status
                    df.loc[df['No Polisi'] == selected, 'Keterangan Lanjutan'] = new_ket
                    
                    if uploaded_foto:
                        link = upload_foto_cloud(uploaded_foto)
                        if link: df.loc[df['No Polisi'] == selected, 'Foto PKB'] = link
                    
                    if save_data(df):
                        st.success("Berhasil diperbarui!")
                        time.sleep(1)
                        st.rerun()

    elif menu_pilihan == "➕ TAMBAH MOBIL":
        with st.form("form_tambah"):
            nopol = st.text_input("No Polisi").upper()
            tipe = st.text_input("Tipe Kendaraan")
            if st.form_submit_button("TAMBAH", width='stretch'):
                new_row = pd.DataFrame([{'No Polisi': nopol, 'Tipe Kendaraan': tipe, 'Status Pekerjaan': 'Menunggu Pekerjaan'}])
                df_updated = pd.concat([df, new_row], ignore_index=True)
                if save_data(df_updated):
                    st.success("Berhasil ditambah!")
                    st.rerun()
else:
    st.info("Data kosong atau gagal memuat.")
def send_auto_email_wa(nopol, status, catatan):
    # --- LOGIKA OTOMATIS EMAIL (Latar Belakang) ---
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = "deny.hermawan@dso.astra.co.id, hendri.yogasaputra@dso.astra.co.id"
        msg['Subject'] = f"Update Status Pekerjaan Otomatis - No Polisi: {nopol}"
        
        body = f"Terdapat update pada kendaraan No Polisi {nopol}.\nStatus Terkini: {status}\nCatatan: {catatan}\n\nSalam, Admin Service."
        msg.attach(MIMEText(body, 'plain'))
        
        # Uncomment baris di bawah ini setelah memasukkan kredensial SENDER_EMAIL yang valid
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        # server.send_message(msg)
        # server.quit()
    except Exception as e:
        print(f"Gagal mengirim email background: {e}")

    # --- LOGIKA OTOMATIS WHATSAPP (Latar Belakang) ---
    # Membutuhkan penyedia layanan API pihak ke-3 (contoh: Fonnte)
    try:
        target_numbers = "089630028860,085888874700"
        pesan_wa = f"Terdapat update pada kendaraan No Polisi {nopol}.\nStatus Terkini: {status}\nCatatan: {catatan}"
        
        # Uncomment baris di bawah ini setelah mendapatkan Token Fonnte/WA API lainnya
        # headers = {'Authorization': WA_API_TOKEN}
        # data = {'target': target_numbers, 'message': pesan_wa}
        # requests.post(WA_API_URL, headers=headers, data=data)
    except Exception as e:
        print(f"Gagal mengirim WA background: {e}")

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

st.markdown(f"<h3 style='text-align: left; display: flex; align-items: center; color: #1b5e20;'><img src='{DAIHATSU_LOGO_PNG}' style='height: 30px; margin-right: 15px;'> Live Service Dashboard</h3>", unsafe_allow_html=True)

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
            
            st.markdown("**📸 Foto Kondisi Kendaraan**")
            foto_saat_ini = str(data_kendaraan.get('Foto PKB', '-')).strip()
            if foto_saat_ini.startswith("http"): 
                st.image(foto_saat_ini, caption="Foto Terakhir", use_container_width=True)
            
            uploaded_foto = st.file_uploader("Upload Foto Baru (Simpan ke Cloud)", type=['jpg', 'jpeg', 'png'])

            if st.form_submit_button("💾 UPDATE DATA", use_container_width=True):
                # FITUR BARU: Wajib foto jika kategori Body Repair
                if kategori_asli == "Body Repair" and uploaded_foto is None:
                    st.error("🛑 GAGAL UPDATE: Kategori Body Repair DIWAJIBKAN mengunggah foto kondisi kendaraan saat update status!")
                else:
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
                            # FITUR BARU: Trigger otomatis notifikasi background tanpa klik
                            send_auto_email_wa(selected_nopol, new_status, new_ket)
                            st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} berhasil diperbarui! Email/WA terkirim otomatis."
                            st.rerun()
                    else:
                        st.error("🛑 Gagal menyimpan karena error unggah foto.")

if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        df_display = df_wip.copy()
        
        # Pengaturan untuk merender Dashboard dengan Progress Bar Visual
        column_configs = {
            "Aksi WA Part 1": st.column_config.LinkColumn("Hubungi WA 1", display_text="💬 Chat Part 1"),
            "Aksi WA Part 2": st.column_config.LinkColumn("Hubungi WA 2", display_text="💬 Chat Part 2"),
            "Aksi Email Part": st.column_config.LinkColumn("Hubungi via Email", display_text="📧 Email Admin Part")
        }
        
        # Tambahkan konfigurasi bar hanya jika kolom ada
        if 'Progress (%)' in df_display.columns:
            column_configs["Progress (%)"] = st.column_config.ProgressColumn(
                "Persentase Selesai",
                help="Bar Progress Status Pekerjaan",
                format="%d%%",
                min_value=0,
                max_value=100
            )

        st.dataframe(
            df_display.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_display.columns else []), 
            use_container_width=True, hide_index=True,
            column_config=column_configs
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
                foto_baru = st.file_uploader("Upload Foto Kendaraan", type=['jpg', 'jpeg', 'png'])
            
            st.markdown("*Wajib diisi")
            
            if st.form_submit_button("💾 SIMPAN DATA KENDARAAN", use_container_width=True):
                if not nopol_baru or not tipe_baru:
                    st.error("⚠️ No Polisi dan Tipe Kendaraan wajib diisi!")
                else:
                    link_foto = "-"
                    upload_sukses = True
                    
                    if foto_baru is not None:
                        with st.spinner("Mengupload foto..."):
                            link = upload_foto_cloud(foto_baru)
                            if link: link_foto = link
                            else: upload_sukses = False
                    
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
else:
    st.info("Loading data atau database masih kosong.")
