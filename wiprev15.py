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

# Konfigurasi Notifikasi WhatsApp (API Starsender)
WA_API_URL = "https://api.starsender.online/api/send/" 
WA_API_TOKEN = "2a38570f-52d8-49f3-af5f-d5ab08b4af0c"

# --- 📌 PETA NOMOR WA BERDASARKAN NAMA SA ---
# [PENTING] Silakan isi dan sesuaikan NAMA SA beserta Nomor WA-nya di sini.
# Pastikan ejaan nama sesuai dengan yang ada di Google Sheets (huruf besar/kecil otomatis disesuaikan)
WA_SA_MAP = {
    "SAHRIM022761": ["6281399211266", "6287774134574", "6281287200880"],
    "MAULAN030509": "6281366664391",
    "BERLIA039884": "6283893470438",
    "MUHAMM086163": "628558825962",
}

# Daftar Backup jika nama SA tidak ditemukan & Admin Part
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
        data = response.json()
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
    except Exception as e:
        st.error(f"Gagal koneksi ke database Cloud: {e}")
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
    df_to_save = df_to_save.fillna("-").astype(str)
    data_list = [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    
    try:
        response = requests.post(APPS_SCRIPT_URL, json=data_list, timeout=30)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error koneksi ke Google Sheets: {e}")
        return False

    if response.status_code == 200:
        load_data.clear()
        return True
    else:
        st.error(f"❌ Gagal menyimpan data ke Cloud. Status Code: {response.status_code} | Respons: {response.text[:200]}")
        return False

def compress_image(img_file, max_dimension=1600, max_size_kb=1024):
    if not PIL_AVAILABLE:
        return img_file.getvalue(), img_file.name, img_file.type or "image/jpeg"
    try:
        img = Image.open(img_file)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS

        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), resample)

        buffer = io.BytesIO()
        quality = 85
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        while buffer.tell() > max_size_kb * 1024 and quality > 30:
            quality -= 10
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)

        buffer.seek(0)
        new_name = img_file.name.rsplit('.', 1)[0] + "_compressed.jpg"
        return buffer.getvalue(), new_name, "image/jpeg"
    except Exception as e:
        print(f"Kompresi foto gagal, upload file asli: {e}")
        return img_file.getvalue(), img_file.name, img_file.type or "image/jpeg"

def upload_foto_cloud(img_file):
    img_bytes, img_name, img_type = compress_image(img_file)
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMGBB_API_KEY}
    files = {"image": (img_name, img_bytes, img_type)}

    try:
        res = requests.post(url, data=payload, files=files, timeout=30)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Gagal terhubung ke server ImgBB: {e}")
        return None

    try:
        data = res.json()
    except ValueError:
        st.error(f"❌ ImgBB memberi respons tidak valid (Status {res.status_code}).")
        return None

    if res.status_code == 200 and data.get('success') and 'data' in data:
        return data['data']['url']
    else:
        err_msg = data.get('error', {}).get('message', 'Penyebab tidak diketahui')
        st.error(f"❌ ImgBB Menolak Upload (Status {res.status_code}): {err_msg}")
        return None

# Fungsi pengiriman pesan WA + Foto (Support Multiple URL)
def send_auto_email_wa(nopol, status, catatan, kategori, nama_sa, list_foto_urls):
    target_wa = []
    
    # 1. Aturan Pengecualian: Jika Menunggu Part HANYA terkirim ke Admin Part
    if status == "Menunggu Part":
        target_wa.extend(WA_ADMIN_PART)
    else:
        # 2. Pisahkan pengiriman otomatis berdasarkan Nama SA
        sa_upper = str(nama_sa).strip().upper()
        # Jika nama SA ditemukan di Map, kirim ke nomor tersebut
        if sa_upper in WA_SA_MAP:
            target_wa.append(WA_SA_MAP[sa_upper])
        else:
            # Fallback jika nama SA tidak ada di map
            if kategori == "Body Repair":
                target_wa.extend(WA_SA_BR_FALLBACK)
            elif kategori == "General Repair":
                target_wa.extend(WA_SA_GR_FALLBACK)
                
    # Hapus duplikat nomor WA
    target_wa = list(set(target_wa))
    
    # --- KIRIM WHATSAPP MULTIPLE FOTO ---
    try:
        pesan_wa = f"*UPDATE STATUS KENDARAAN*\n\n🚘 *No Polisi:* {nopol}\n👤 *SA:* {nama_sa}\n🛠️ *Kategori:* {kategori}\n📊 *Status Terkini:* {status}\n📝 *Catatan:* {catatan}"
        headers = {'Authorization': f"Bearer {WA_API_TOKEN}", 'Content-Type': 'application/json'}
        
        for number in target_wa:
            if not number.strip(): continue
            
            if list_foto_urls:
                # Foto pertama sekaligus kirim caption komplit
                for i, url in enumerate(list_foto_urls):
                    if not url.startswith("http"): continue
                    caption = pesan_wa if i == 0 else f"Lanjutan Foto ({i+1}) - {nopol}"
                    payload = {"to": number.strip(), "media": url.strip(), "caption": caption}
                    requests.post(f"{WA_API_URL.rstrip('/')}/messages/image", headers=headers, json=payload, timeout=5)
            else:
                # Jika tidak ada foto sama sekali, kirim pesan text murni
                payload = {"to": number.strip(), "body": pesan_wa}
                requests.post(f"{WA_API_URL.rstrip('/')}/messages/text", headers=headers, json=payload, timeout=5)
    except Exception as e:
        print(f"Gagal mengirim WA background: {e}")

    # --- KIRIM EMAIL ---
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = "deny.hermawan@dso.astra.co.id, hendri.yogasaputra@dso.astra.co.id"
        msg['Subject'] = f"Update Status ({kategori}) - No Polisi: {nopol} [{status}]"
        
        body = f"Terdapat update pada kendaraan No Polisi: {nopol}\nNama SA: {nama_sa}\nKategori Pekerjaan: {kategori}\nStatus Terkini: {status}\nCatatan: {catatan}\n"
        if list_foto_urls:
            body += "\nLink Foto Terkini:\n" + "\n".join(list_foto_urls)
        body += "\n\nSalam, Admin Service DSO Karawaci."
        
        msg.attach(MIMEText(body, 'plain'))
        # Uncomment untuk mengaktifkan SMTP email
        # server = smtplib.SMTP('smtp.gmail.com', 587)
        # server.starttls()
        # server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        # server.send_message(msg)
        # server.quit()
    except Exception as e:
        print(f"Gagal mengirim email background: {e}")

# ==========================================
# 📊 DASHBOARD & APP LOGIC
# ==========================================
with st.sidebar:
    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", width="stretch"):
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
    st.markdown(f"#### 🔎 Pencarian Kendaraan WIP ({kategori_filter})")
    if df_wip.empty: return st.warning("Tidak ada data WIP saat ini.")
    
    df_kategori = df_wip[df_wip['Kategori'] == kategori_filter]
    list_nopol = df_kategori['No Polisi'].dropna().unique().tolist()
    
    metode_cari = st.radio("Metode:", ["Pilih dari List", "Ketik Manual"], key=f"rad_{kategori_filter}", horizontal=True)
    if metode_cari == "Pilih dari List":
        selected_nopol = st.selectbox("Pilih No Polisi", [""] + list_nopol)
    else:
        selected_nopol = st.text_input("Ketik No Polisi").strip().upper()

    execute_form_logic(selected_nopol, list_nopol, kategori_filter)

def render_mobile_form():
    st.markdown("#### 📱 Menu Update Mobile (WIP)")
    if df_wip.empty: return st.warning("Tidak ada data WIP saat ini.")
    
    list_nopol = df_wip['No Polisi'].dropna().unique().tolist()
    
    tab1, tab2 = st.tabs(["📝 Pilih dari List", "⌨️ Cari Manual"])
    with tab1: nopol_list = st.selectbox("Cari No Polisi Kendaraan", [""] + list_nopol, key="mob_list")
    with tab2: nopol_man = st.text_input("Ketik No Polisi", key="mob_man").strip().upper()
        
    selected_nopol = nopol_list if nopol_list else nopol_man
    execute_form_logic(selected_nopol, list_nopol, None)

def execute_form_logic(selected_nopol, list_nopol, kategori_filter):
    if selected_nopol and selected_nopol in df['No Polisi'].values:
        data_kendaraan = df[df['No Polisi'] == selected_nopol].iloc[-1] 
        kategori_asli = data_kendaraan.get('Kategori', 'General Repair')
        nama_sa = str(data_kendaraan.get('Nama SA', '-'))
        
        st.success(f"🎯 **{data_kendaraan.get('Nama Customer', '-')}** | {selected_nopol} | SA: {nama_sa} | {data_kendaraan.get('Tipe Kendaraan', '-')}")
        
        with st.form(f"form_update_{selected_nopol}", clear_on_submit=True):
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
            
            # Tampilkan multiple foto yang lama jika ada (dipisah koma)
            if foto_saat_ini != "-":
                list_foto_lama = [f.strip() for f in foto_saat_ini.split(',') if f.strip().startswith("http")]
                if list_foto_lama:
                    cols = st.columns(min(len(list_foto_lama), 4))
                    for i, f_url in enumerate(list_foto_lama):
                        cols[i % 4].image(f_url, caption=f"Foto Terakhir {i+1}")
            
            # Mendukung multiple upload file sekarang
            uploaded_fotos = st.file_uploader("Upload Foto Baru (Bisa Lebih Dari Satu)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key=f"upload_{selected_nopol}")

            if st.form_submit_button("💾 UPDATE DATA", width="stretch"):
                if kategori_asli == "Body Repair" and not uploaded_fotos and new_status != curr_status:
                    st.error("🛑 GAGAL UPDATE: Kategori Body Repair DIWAJIBKAN mengunggah foto saat update status!")
                else:
                    upload_sukses = True
                    link_fotos = []
                    
                    if uploaded_fotos:
                        with st.spinner("Mengupload foto..."):
                            for foto in uploaded_fotos:
                                link = upload_foto_cloud(foto)
                                if link:
                                    link_fotos.append(link)
                                else:
                                    upload_sukses = False
                                    break
                    
                    if upload_sukses:
                        # Jika ada foto baru, simpan ke database pisahkan koma
                        if link_fotos:
                            df.loc[df['No Polisi'] == selected_nopol, 'Foto PKB'] = ", ".join(link_fotos)
                            
                        df.loc[df['No Polisi'] == selected_nopol, 'Status Pekerjaan'] = new_status
                        df.loc[df['No Polisi'] == selected_nopol, 'Keterangan Lanjutan'] = new_ket
                        df.loc[df['No Polisi'] == selected_nopol, 'Tanggal Terakhir Diupdate'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.session_state['df_data'] = df
                        with st.spinner("Menyinkronkan ke Cloud..."):
                            sukses = save_data(df)
                            
                        if sukses:
                            # Tentukan List URL untuk dikirim via WA
                            foto_terkirim_urls = link_fotos if link_fotos else ([f.strip() for f in foto_saat_ini.split(',') if f.strip().startswith("http")] if foto_saat_ini != "-" else [])
                            
                            send_auto_email_wa(selected_nopol, new_status, new_ket, kategori_asli, nama_sa, foto_terkirim_urls)
                            target_notif = "Admin Part" if new_status == "Menunggu Part" else f"SA {nama_sa}"
                            st.session_state['notif_sukses'] = f"✅ Data {selected_nopol} berhasil diperbarui! Email/WA terkirim otomatis ke {target_notif}."
                            st.rerun()
                    else:
                        st.error("🛑 Gagal menyimpan karena ada error saat unggah foto.")
    elif selected_nopol:
        st.error("❌ Kendaraan tidak ditemukan di Database.")

if not df.empty:
    if menu_pilihan == "📊 SEMUA WIP": 
        df_display = df_wip.copy()
        
        column_configs = {
            "Aksi WA Part 1": st.column_config.LinkColumn("Hubungi WA 1", display_text="💬 Chat Part 1"),
            "Aksi WA Part 2": st.column_config.LinkColumn("Hubungi WA 2", display_text="💬 Chat Part 2"),
            "Aksi Email Part": st.column_config.LinkColumn("Hubungi via Email", display_text="📧 Email Admin Part")
        }
        
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
            width="stretch", hide_index=True,
            column_config=column_configs
        )
    elif menu_pilihan == "📱 TAMPILAN MOBILE":
        render_mobile_form()
    elif menu_pilihan == "🛠️ ANTREAN GR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'General Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), width="stretch", hide_index=True)
    elif menu_pilihan == "📝 UPDATE GR": 
        render_update_form("General Repair")
    elif menu_pilihan == "🔨 ANTREAN BR": 
        st.dataframe(df_wip[df_wip['Kategori'] == 'Body Repair'].style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_wip.columns else []), width="stretch", hide_index=True)
    elif menu_pilihan == "📝 UPDATE BR": 
        render_update_form("Body Repair")
    elif menu_pilihan == "✅ RIWAYAT SELESAI": 
        st.dataframe(df_selesai.style.map(style_umur_pkb, subset=['Umur PKB (Hari)'] if 'Umur PKB (Hari)' in df_selesai.columns else []), width="stretch", hide_index=True)
        
    elif menu_pilihan == "➕ TAMBAH MOBIL TAMU":
        st.markdown("#### 🚗 Input Kendaraan Tamu / Manual")
        st.info("Fitur ini digunakan untuk memasukkan kendaraan yang belum terdaftar PKB (Non-PKB).")
        
        with st.form("form_input_tamu", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nopol_baru = st.text_input("No Polisi *").strip().upper()
                tipe_baru = st.text_input("Tipe Kendaraan *").strip()
                kategori_baru = st.selectbox("Kategori Pekerjaan", ["General Repair", "Body Repair"])
                nama_sa_baru = st.text_input("Nama SA *").strip()
            with c2:
                warna_baru = st.text_input("Warna Kendaraan").strip()
                foto_barus = st.file_uploader("Upload Foto Kendaraan (Bisa Multiple)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
            
            st.markdown("*Wajib diisi")
            
            if st.form_submit_button("💾 SIMPAN DATA KENDARAAN", width="stretch"):
                if not nopol_baru or not tipe_baru or not nama_sa_baru:
                    st.error("⚠️ No Polisi, Tipe Kendaraan, dan Nama SA wajib diisi!")
                else:
                    link_fotos = []
                    upload_sukses = True
                    
                    if foto_barus:
                        with st.spinner("Mengupload foto..."):
                            for foto in foto_barus:
                                link = upload_foto_cloud(foto)
                                if link: 
                                    link_fotos.append(link)
                                else: 
                                    upload_sukses = False
                                    break
                    
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
                        new_data['Nama SA'] = nama_sa_baru.upper()
                        new_data['No PKB'] = "BELUM ADA"
                        new_data['Foto PKB'] = ", ".join(link_fotos) if link_fotos else "-"
                        
                        df_new_row = pd.DataFrame([new_data])
                        df_updated = pd.concat([df, df_new_row], ignore_index=True)
                        
                        st.session_state['df_data'] = df_updated
                        with st.spinner("Menyinkronkan ke Cloud..."):
                            sukses = save_data(df_updated)
                        
                        if sukses:
                            st.session_state['notif_sukses'] = f"✅ Kendaraan Tamu {nopol_baru} berhasil didaftarkan!"
                            st.rerun()
                    else:
                        st.error("🛑 Gagal menyimpan karena ada error saat unggah foto.")
else:
    st.info("Loading data atau database masih kosong.")
