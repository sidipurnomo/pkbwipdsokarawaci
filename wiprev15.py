import streamlit as st
import pandas as pd
import time
import requests
import io
import base64
import json
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
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbybnr3sAxBqsyghspXAZlyVOPq83ILSziZountsF2M7UUV_H-uqcn0iJUr5IBmO1v63/exec"

# Konfigurasi Notifikasi Email
SENDER_EMAIL = "akunbodong@gmail.com"
SENDER_APP_PASSWORD = "apabae"

# Konfigurasi Notifikasi WhatsApp (GREEN API)
GREEN_API_HOST = "https://7107.api.greenapi.com"
GREEN_API_ID_INSTANCE = "710722681804"
GREEN_API_TOKEN = "1adfea21b7d0429aa3fb6b88463955fbc5ccde8b52234b0792"

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

STANDARD_COLUMNS = [
    'No PKB', 'Tipe Kendaraan', 'No Polisi', 'Nama Customer', 'Kategori',
    'Status Pekerjaan', 'Nama SA', 'Tgl PKB', 'Tanggal Terakhir Diupdate',
    'Keterangan Lanjutan', 'Foto PKB', 'Status SPK Asuransi',
    'Status Pembayaran OR', 'Kelengkapan Dokumen Asuransi'
]

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
        time.sleep(2)
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

    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", width="stretch"):
        load_data.clear()
        if 'df_data' in st.session_state:
            del st.session_state['df_data']
        st.rerun()
    if st.button("LOGOUT", width="stretch"):
        st.session_state['logged_in'] = False
        st.rerun()

# ==========================================
# 🌐 NORMALISASI & INTEGRASI CLOUD
# ==========================================
def normalisasi_kategori(val):
    """Menyeragamkan variasi teks kategori di Sheets (GR / General Repair, BR / Body Repair)."""
    s = str(val).strip().upper()
    if s in ["", "-", "NAN", "NONE"]:
        return "-"
    if s in ["GR", "G.R", "GENERAL REPAIR", "GENERAL", "SERVICE", "SERVIS"] or "GENERAL" in s or s.startswith("GR"):
        return "General Repair"
    if s in ["BR", "B.R", "BODY REPAIR", "BODY", "BODY & PAINT", "BP"] or "BODY" in s or s.startswith("BR"):
        return "Body Repair"
    return str(val).strip()

def normalisasi_status(status_val, kategori_norm):
    """Menyeragamkan status pekerjaan dan memberi default jika kosong."""
    s = str(status_val).strip()
    s_up = s.upper()
    default_status = "Antrian Pekerjaan" if kategori_norm == "Body Repair" else "Menunggu Pekerjaan"

    if s_up in ["", "-", "NAN", "NONE", "BELUM DIKERJAKAN", "ANTRI", "ANTRIAN"]:
        return default_status
    if s_up == "SELESAI":
        return "Selesai"

    semua_status = [
        "Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai",
        "Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul",
        "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan"
    ]
    for st_valid in semua_status:
        if s_up == st_valid.upper():
            return st_valid
    return s

def hitung_progress(kategori, status):
    if status == "Selesai":
        return 100
    if status == "Menunggu Part":
        return 50
    if status == "Quality Control":
        return 90

    if kategori == "General Repair":
        if status == "Menunggu Pekerjaan":
            return 10
        if status == "Sedang Dikerjakan":
            return 60
    elif kategori == "Body Repair":
        br_steps = [
            "Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul",
            "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan"
        ]
        if status in br_steps:
            return int(((br_steps.index(status) + 1) / len(br_steps)) * 85)
    return 0

def post_to_apps_script(payload, timeout=30):
    try:
        headers = {"Content-Type": "text/plain;charset=utf-8"}
        response = requests.post(
            APPS_SCRIPT_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
    except requests.exceptions.RequestException as e:
        return False, f"Error koneksi ke Google Apps Script: {e}", None

    if "<!DOCTYPE html>" in response.text or "<html" in response.text.lower():
        return False, (
            "Akses ke Google Apps Script DITOLAK (respons HTML). "
            "Pastikan Web App sudah di-Deploy ulang dengan 'Who has access' = 'Anyone'."
        ), None

    try:
        res_json = response.json()
    except ValueError:
        return False, f"Respons Apps Script bukan JSON valid: {response.text[:200]}", None

    if response.status_code == 200 and (res_json.get("success") is True or res_json.get("status") == "success"):
        return True, "OK", res_json
    else:
        err_msg = res_json.get("error") or res_json.get("message") or str(res_json)
        return False, f"Apps Script menolak permintaan: {err_msg}", res_json

@st.cache_data(ttl=15)
def load_data():
    empty_df = pd.DataFrame(columns=STANDARD_COLUMNS)
    try:
        response = requests.get(f"{APPS_SCRIPT_URL}?action=get_data", timeout=15, allow_redirects=True)
        if response.status_code != 200:
            st.error(f"Gagal koneksi ke Cloud. HTTP Code: {response.status_code}")
            return empty_df

        if "<!DOCTYPE html>" in response.text or "<html" in response.text.lower():
            st.error("❌ Akses GET ke Google Apps Script ditolak (HTML). Pastikan 'Who has access' diatur ke 'Anyone'.")
            return empty_df

        try:
            data = response.json()
        except ValueError:
            st.error("❌ Respons GET tidak valid (bukan JSON). Pastikan fungsi doGet(e) di Code.gs sudah benar.")
            return empty_df

        if not data:
            return empty_df

        if isinstance(data, dict):
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])
            elif data.get('status') == 'error':
                st.error(f"❌ Error dari Spreadsheet: {data.get('error', 'Unknown error')}")
                return empty_df
            else:
                df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        if df.empty:
            return empty_df

        # Bersihkan spasi nama kolom
        df.columns = [str(c).strip() for c in df.columns]

        # Antisipasi jika nama kolom kategori di sheet berbeda (misal 'Kategori Pekerjaan' / 'Jenis Pekerjaan')
        if 'Kategori' not in df.columns:
            for alt_col in ['Kategori Pekerjaan', 'Jenis Pekerjaan', 'Tipe Pekerjaan', 'Divisi', 'Workshop']:
                if alt_col in df.columns:
                    df['Kategori'] = df[alt_col]
                    break

        if 'No Polisi' in df.columns:
            df['No Polisi'] = df['No Polisi'].astype(str).str.strip().str.upper()
            df = df[df['No Polisi'].notna() & (~df['No Polisi'].isin(['', '-', 'NAN', 'NONE']))]
        if 'No PKB' in df.columns:
            df['No PKB'] = df['No PKB'].astype(str).str.strip()

        if df.empty:
            return empty_df

        if 'No PKB' in df.columns and 'No Polisi' in df.columns:
            df['Identifier'] = df.apply(
                lambda x: str(x['No PKB']).strip()
                if str(x.get('No PKB', '')).strip() not in ['', '-', 'BELUM ADA', 'nan', 'None']
                else str(x.get('No Polisi', '')).strip(),
                axis=1
            )
            df = df.drop_duplicates(subset=['Identifier'], keep='last').drop(columns=['Identifier']).reset_index(drop=True)
        elif 'No Polisi' in df.columns:
            df = df.drop_duplicates(subset=['No Polisi'], keep='last').reset_index(drop=True)

        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = "-"

        # Normalisasi Kategori & Status Pekerjaan agar GR dan BR selalu terbaca di masing-masing dashboard
        df['Kategori'] = df['Kategori'].apply(normalisasi_kategori)
        df['Status Pekerjaan'] = df.apply(
            lambda row: normalisasi_status(row['Status Pekerjaan'], row['Kategori']), axis=1
        )

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

        df['Progress (%)'] = df.apply(
            lambda row: hitung_progress(row['Kategori'], row['Status Pekerjaan']), axis=1
        )

        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal koneksi internet ke database Cloud: {e}")
        return empty_df
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data Cloud: {e}")
        return empty_df

def prepare_df_for_sheet(df):
    df_clean = df.drop(
        columns=['Umur PKB (Hari)', 'Progress (%)', 'Aksi WA Part 1', 'Aksi WA Part 2', 'Aksi Email Part', 'Aksi WA Part'],
        errors='ignore'
    ).copy()
    for col in STANDARD_COLUMNS:
        if col not in df_clean.columns:
            df_clean[col] = "-"
    df_clean = df_clean[STANDARD_COLUMNS]
    return df_clean.fillna("-").astype(str)

def save_data(df):
    df_to_save = prepare_df_for_sheet(df)
    payload_save = {
        "action": "save_data",
        "data": [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    }
    sukses, msg, _ = post_to_apps_script(payload_save, timeout=30)
    if sukses:
        load_data.clear()
        return True
    else:
        st.error(f"❌ Gagal menyimpan ke Google Sheets: {msg}")
        return False

def add_row_to_sheet(row_dict, full_df_fallback):
    clean_row = {col: str(row_dict.get(col, "-")) for col in STANDARD_COLUMNS}
    payload = {
        "action": "add_row",
        "row": clean_row
    }
    sukses, msg, _ = post_to_apps_script(payload, timeout=25)
    if sukses:
        load_data.clear()
        return True
    return save_data(full_df_fallback)

def update_row_in_sheet(nopol, updated_fields, full_df_fallback):
    payload = {
        "action": "update_row",
        "nopol": str(nopol).strip().upper(),
        "updates": {k: str(v) for k, v in updated_fields.items()}
    }
    sukses, msg, _ = post_to_apps_script(payload, timeout=25)
    if sukses:
        load_data.clear()
        return True
    return save_data(full_df_fallback)

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
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    payload = {
        "action": "upload_image",
        "filename": img_name,
        "mimeType": img_type,
        "data": img_base64
    }

    sukses, msg, data = post_to_apps_script(payload, timeout=60)
    if sukses and data and data.get('url'):
        return data.get('url')
    else:
        st.error(f"❌ Upload GDrive Gagal: {msg}")
        return None

# ==========================================
# 🚀 PENGIRIMAN WA GREEN API & EMAIL
# ==========================================
def send_auto_email_wa(nopol, status, catatan, kategori, nama_sa, list_foto_urls, spk_status, or_status, dok_status):
    target_wa = []
    wa_error_messages = []

    if status == "Menunggu Part":
        target_wa.extend(WA_ADMIN_PART)
    else:
        sa_upper = str(nama_sa).strip().upper()
        if sa_upper in WA_SA_MAP:
            target_wa.append(WA_SA_MAP[sa_upper])
        else:
            if kategori == "Body Repair":
                target_wa.extend(WA_SA_BR_FALLBACK)
            elif kategori == "General Repair":
                target_wa.extend(WA_SA_GR_FALLBACK)

    target_wa = list(set(target_wa))

    if not target_wa:
        wa_error_messages.append(f"Tidak ada nomor WA tujuan untuk SA '{nama_sa}' (Kategori: {kategori}).")
        return wa_error_messages

    pesan_wa = (
        f"*UPDATE STATUS KENDARAAN*\n\n"
        f"🚘 *No Polisi:* {nopol}\n"
        f"👤 *SA:* {nama_sa}\n"
        f"🛠️ *Kategori:* {kategori}\n"
        f"📊 *Status Terkini:* {status}\n"
        f"📝 *Catatan:* {catatan}"
    )

    if spk_status != "-" or or_status != "-" or dok_status != "-":
        pesan_wa += f"\n\n🛡️ *Data Asuransi:*\n📄 SPK: {spk_status}\n💰 Bayar OR: {or_status}\n📁 Dokumen: {dok_status}"

    headers = {'Content-Type': 'application/json'}
    base_url = f"{GREEN_API_HOST.rstrip('/')}/waInstance{GREEN_API_ID_INSTANCE}"
    url_send_text = f"{base_url}/sendMessage/{GREEN_API_TOKEN}"
    url_send_file = f"{base_url}/sendFileByUrl/{GREEN_API_TOKEN}"

    try:
        for number in target_wa:
            if not number.strip():
                continue
            chat_id = f"{number.strip()}@c.us"

            if list_foto_urls:
                for i, url in enumerate(list_foto_urls):
                    if not url.startswith("http"):
                        continue
                    caption = pesan_wa if i == 0 else f"Lanjutan Foto ({i+1}) - {nopol}"
                    payload = {
                        "chatId": chat_id,
                        "urlFile": url.strip(),
                        "fileName": f"Update_Kendaraan_{i+1}.jpg",
                        "caption": caption
                    }
                    res = requests.post(url_send_file, headers=headers, json=payload, timeout=15)
                    if str(res.status_code) != "200":
                        wa_error_messages.append(f"Gagal kirim gambar ke {number}. Kode HTTP: {res.status_code}. Info: {res.text}")
            else:
                payload = {
                    "chatId": chat_id,
                    "message": pesan_wa
                }
                res = requests.post(url_send_text, headers=headers, json=payload, timeout=10)
                if str(res.status_code) != "200":
                    wa_error_messages.append(f"Gagal kirim teks ke {number}. Kode HTTP: {res.status_code}. Info: {res.text}")

    except Exception as e:
        wa_error_messages.append(f"Error Koneksi Server Green API: {str(e)}")

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = "deny.hermawan@dso.astra.co.id, hendri.yogasaputra@dso.astra.co.id"
        msg['Subject'] = f"Update Status ({kategori}) - No Polisi: {nopol} [{status}]"

        body = f"Terdapat update pada kendaraan No Polisi: {nopol}\nNama SA: {nama_sa}\nKategori Pekerjaan: {kategori}\nStatus Terkini: {status}\nCatatan: {catatan}\n"
        if spk_status != "-" or or_status != "-" or dok_status != "-":
            body += f"\n--- Info Asuransi ---\nStatus SPK: {spk_status}\nPembayaran OR: {or_status}\nKelengkapan Dokumen: {dok_status}\n"
        if list_foto_urls:
            body += "\nLink Foto Terkini:\n" + "\n".join(list_foto_urls)
        body += "\n\nSalam, Admin Service DSO Karawaci."
        msg.attach(MIMEText(body, 'plain'))
    except Exception as e:
        print(f"Gagal menyiapkan email background: {e}")

    return wa_error_messages

# ==========================================
# 📊 DASHBOARD & APP LOGIC
# ==========================================
df = load_data()
st.session_state['df_data'] = df

def style_umur_pkb(val):
    try:
        if int(val) > 60:
            return 'color: #ff4b4b; font-weight: bold;'
    except Exception:
        pass
    return ''

def get_table_column_configs(target_df):
    column_configs = {
        "Aksi WA Part 1": st.column_config.LinkColumn("Hubungi WA 1", display_text="💬 Chat Part 1"),
        "Aksi WA Part 2": st.column_config.LinkColumn("Hubungi WA 2", display_text="💬 Chat Part 2"),
        "Aksi Email Part": st.column_config.LinkColumn("Hubungi via Email", display_text="📧 Email Admin Part")
    }
    if 'Progress (%)' in target_df.columns:
        column_configs["Progress (%)"] = st.column_config.ProgressColumn(
            "Persentase Selesai",
            help="Bar Progress Status Pekerjaan",
            format="%d%%",
            min_value=0,
            max_value=100
        )
    return column_configs

if 'notif_sukses' in st.session_state:
    st.success(st.session_state['notif_sukses'])
    del st.session_state['notif_sukses']

if 'wa_errors' in st.session_state:
    st.error("⚠️ **GAGAL MENGIRIM WHATSAPP (GREEN API):**\n\n" + "\n".join(st.session_state['wa_errors']))
    del st.session_state['wa_errors']

st.markdown(f"<h3 style='text-align: left
