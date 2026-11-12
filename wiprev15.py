import streamlit as st
import pandas as pd
import time
import re
import requests
import io
import base64
import json
import urllib.parse
from datetime import datetime

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==========================================
# KONFIGURASI CLOUD & API
# ==========================================
APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/AKfycbz1HVlqkDGS64H8R30C-HxcwptGGTKynZctmT4jAJ0C0i8xxee_OQtHfQoKAUohUIk/exec"
)

GREEN_API_HOST = "https://7107.api.greenapi.com"
GREEN_API_ID_INSTANCE = "710722681804"
GREEN_API_TOKEN = "1adfea21b7d0429aa3fb6b88463955fbc5ccde8b52234b0792"

WA_SA_MAP = {
    "SAHRIM022761": "6287774134574",
    "MAULAN030509": "6281366664391",
    "BERLIA039884": "6283893470438",
    "MUHAMM086163": "628558825962",
}

# Daftar kode/nama SA khusus Body Repair (untuk deteksi otomatis jika kolom Kategori kosong)
SA_BODY_REPAIR = ["SAHRIM022761", "SAHRIM"]

WA_SA_BR_FALLBACK = ["6287774134574"]
WA_SA_GR_FALLBACK = ["6287774134574"]
WA_ADMIN_PART = ["6289630028860", "6285888874700"]

STANDARD_COLUMNS = [
    "No PKB", "Tipe Kendaraan", "No Polisi", "Nama Customer", "Kategori",
    "Status Pekerjaan", "Nama SA", "Tgl PKB", "Tanggal Terakhir Diupdate",
    "Keterangan Lanjutan", "Foto PKB", "Status SPK Asuransi",
    "Status Pembayaran OR", "Kelengkapan Dokumen Asuransi"
]

COLUMN_ALIASES = {
    "no pkb": "No PKB",
    "nomor pkb": "No PKB",
    "pkb": "No PKB",
    "no wo": "No PKB",
    "wo": "No PKB",
    "tipe kendaraan": "Tipe Kendaraan",
    "tipe": "Tipe Kendaraan",
    "type": "Tipe Kendaraan",
    "model": "Tipe Kendaraan",
    "kendaraan": "Tipe Kendaraan",
    "no polisi": "No Polisi",
    "nomor polisi": "No Polisi",
    "no pol": "No Polisi",
    "nopol": "No Polisi",
    "plat": "No Polisi",
    "plat nomor": "No Polisi",
    "nama customer": "Nama Customer",
    "customer": "Nama Customer",
    "nama pelanggan": "Nama Customer",
    "pelanggan": "Nama Customer",
    "pemilik": "Nama Customer",
    "kategori": "Kategori",
    "kategori pekerjaan": "Kategori",
    "jenis pekerjaan": "Kategori",
    "jenis service": "Kategori",
    "jenis servis": "Kategori",
    "tipe pekerjaan": "Kategori",
    "tipe service": "Kategori",
    "category": "Kategori",
    "kat": "Kategori",
    "divisi": "Kategori",
    "bengkel": "Kategori",
    "status pekerjaan": "Status Pekerjaan",
    "status": "Status Pekerjaan",
    "progress": "Status Pekerjaan",
    "nama sa": "Nama SA",
    "sa": "Nama SA",
    "service advisor": "Nama SA",
    "tgl pkb": "Tgl PKB",
    "tanggal pkb": "Tgl PKB",
    "tgl masuk": "Tgl PKB",
    "tanggal": "Tgl PKB",
    "tanggal terakhir diupdate": "Tanggal Terakhir Diupdate",
    "last update": "Tanggal Terakhir Diupdate",
    "updated at": "Tanggal Terakhir Diupdate",
    "keterangan lanjutan": "Keterangan Lanjutan",
    "keterangan": "Keterangan Lanjutan",
    "catatan": "Keterangan Lanjutan",
    "keluhan": "Keterangan Lanjutan",
    "foto pkb": "Foto PKB",
    "foto": "Foto PKB",
    "link foto": "Foto PKB",
    "dokumentasi": "Foto PKB",
    "status spk asuransi": "Status SPK Asuransi",
    "status spk": "Status SPK Asuransi",
    "spk": "Status SPK Asuransi",
    "status pembayaran or": "Status Pembayaran OR",
    "pembayaran or": "Status Pembayaran OR",
    "status or": "Status Pembayaran OR",
    "kelengkapan dokumen asuransi": "Kelengkapan Dokumen Asuransi",
    "kelengkapan dokumen": "Kelengkapan Dokumen Asuransi",
    "dokumen asuransi": "Kelengkapan Dokumen Asuransi",
}

DAIHATSU_LOGO_PNG = (
    "https://images.seeklogo.com/logo-png/3/1/"
    "daihatsu-logo-png_seeklogo-38135.png"
)

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
    div.stButton > button {
        border-radius: 8px; border: 1px solid #4caf50;
        background-color: transparent; color: #2e7d32; font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #4caf50; color: white;
    }
    div[role="radiogroup"] > label {
        background-color: #f1f8e9 !important; color: #1b5e20 !important;
        padding: 10px 5px !important; border-radius: 10px; margin-bottom: 8px;
        border: 1px solid #dcedc8; border-bottom: 5px solid #aed581;
    }
    div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none; }
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important; font-weight: 800 !important; margin: 0 !important;
    }
    div[data-testid="metric-container"] {
        background: radial-gradient(circle at top left, #ffffff, #e8f5e9) !important;
        border-radius: 25px !important; padding: 15px 10px !important;
        border: 2px solid #aed581 !important; text-align: center !important;
    }
    .title-glowing {
        text-align: center; color: #2e7d32; font-family: 'Arial Black', sans-serif;
        display: flex; justify-content: center; align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SISTEM LOGIN & AUTO LOGOUT
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "last_activity" not in st.session_state:
    st.session_state["last_activity"] = time.time()
if "last_menu" not in st.session_state:
    st.session_state["last_menu"] = None

if st.session_state["logged_in"]:
    if time.time() - st.session_state["last_activity"] > 1800:
        st.session_state["logged_in"] = False
        st.warning("Sesi berakhir. Silakan login kembali.")
        time.sleep(2)
        st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    header_html = (
        f"<h1 class='title-glowing'>"
        f"<img src='{DAIHATSU_LOGO_PNG}' style='height:40px;margin-right:15px;'>"
        f"PKB WIP DSO KARAWACI</h1>"
    )
    st.markdown(header_html, unsafe_allow_html=True)
    with st.form("login_form"):
        st.markdown("<h3 style='text-align:center;'>Login Dashboard</h3>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("LOGIN", width="stretch"):
            if username == "dsokarawaci" and password == "adminkarawaci":
                st.session_state["logged_in"] = True
                st.session_state["last_activity"] = time.time()
                st.rerun()
            else:
                st.error("Username atau Password Salah!")

if not st.session_state["logged_in"]:
    render_login()
    st.stop()

# ==========================================
# SIDEBAR MENU KIRI
# ==========================================
with st.sidebar:
    logo_html = f"<div style='text-align:center;'><img src='{DAIHATSU_LOGO_PNG}' style='width:120px;'></div>"
    st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#2e7d32;'>Astra Daihatsu<br>Karawaci</h3>", unsafe_allow_html=True)

    menu_pilihan = st.radio(
        "Pilih Halaman:",
        [
            "📊 SEMUA WIP",
            "📱 TAMPILAN MOBILE",
            "🛠️ ANTREAN GR",
            "📝 UPDATE GR",
            "🔨 ANTREAN BR",
            "📝 UPDATE BR",
            "✅ RIWAYAT SELESAI",
            "➕ TAMBAH MOBIL TAMU"
        ],
        label_visibility="collapsed"
    )

    if menu_pilihan != st.session_state["last_menu"]:
        st.session_state["last_activity"] = time.time()
        st.session_state["last_menu"] = menu_pilihan

    st.markdown("---")
    if st.button("🔄 REFRESH DATA DARI CLOUD", width="stretch"):
        load_data.clear()
        st.rerun()
    if st.button("LOGOUT", width="stretch"):
        st.session_state["logged_in"] = False
        st.rerun()

# ==========================================
# FUNGSI CLOUD & PARSING SPREADSHEET
# ==========================================
def normalize_kategori(row):
    """Menstandarkan nilai Kategori menjadi 'Body Repair' atau 'General Repair'."""
    raw_kat = str(row.get("Kategori", "-")).strip().upper()
    sa = str(row.get("Nama SA", "-")).strip().upper()
    pkb = str(row.get("No PKB", "-")).strip().upper()

    if raw_kat not in ["", "-", "NONE", "NAN", "NULL"]:
        if (
            "BODY" in raw_kat
            or raw_kat in ["BR", "BP", "B/R", "B&P"]
            or re.search(r"\b(BR|BP)\b", raw_kat)
        ):
            return "Body Repair"
        if (
            "GENERAL" in raw_kat
            or raw_kat in ["GR", "PM", "G/R"]
            or re.search(r"\b(GR|PM)\b", raw_kat)
        ):
            return "General Repair"

    if any(sa_br in sa for sa_br in SA_BODY_REPAIR):
        return "Body Repair"

    if re.search(r"[-_/]BR[-_/]|^BR\d", pkb):
        return "Body Repair"
    if re.search(r"[-_/]GR[-_/]|^GR\d", pkb):
        return "General Repair"

    return "General Repair"

def hitung_progress(kategori, status):
    st_up = str(status).strip().lower()
    kat_up = str(kategori).strip().lower()
    if st_up in ["selesai", "done", "closed"]:
        return 100
    if st_up == "menunggu part":
        return 50
    if st_up == "quality control":
        return 90
    if kat_up in ["general repair", "gr"]:
        if st_up == "menunggu pekerjaan":
            return 10
        if st_up == "sedang dikerjakan":
            return 60
    elif kat_up in ["body repair", "br"]:
        br_steps = [
            "antrian pekerjaan", "bongkar", "ketok / las", "dempul",
            "epoxy", "pengecatan / oven", "poles", "perakitan / pemasangan"
        ]
        if st_up in br_steps:
            return int(((br_steps.index(st_up) + 1) / len(br_steps)) * 85)
    return 0

def post_to_apps_script(payload, timeout=30):
    try:
        headers = {"Content-Type": "text/plain;charset=utf-8"}
        action_name = payload.get("action", "")
        target_url = (
            f"{APPS_SCRIPT_URL}?action={urllib.parse.quote(str(action_name))}"
            if action_name else APPS_SCRIPT_URL
        )
        res = requests.post(
            target_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
    except requests.exceptions.RequestException as e:
        return False, f"Error koneksi: {e}", None

    if "<!DOCTYPE html>" in res.text or "<html" in res.text.lower():
        return False, "Akses ditolak (HTML). Deploy ulang Apps Script dengan akses 'Anyone'.", None

    try:
        res_json = res.json()
    except ValueError:
        return False, f"Respons bukan JSON valid: {res.text[:150]}", None

    if res.status_code == 200 and (res_json.get("success") is True or res_json.get("status") == "success"):
        return True, "OK", res_json
    err_msg = res_json.get("error") or res_json.get("message") or str(res_json)
    return False, err_msg, res_json

def clean_header_key(col_name):
    return re.sub(r"[\s._\-/]+", " ", str(col_name).strip().lower()).strip()

def normalize_columns(df):
    rename_map = {}
    used_targets = set()
    for col in df.columns:
        key = clean_header_key(col)
        if key in COLUMN_ALIASES:
            target = COLUMN_ALIASES[key]
            if target not in used_targets:
                rename_map[col] = target
                used_targets.add(target)
    return df.rename(columns=rename_map) if rename_map else df

def parse_raw_payload_to_df(data):
    """Mengubah berbagai struktur JSON dari Apps Script menjadi DataFrame."""
    if not data:
        return pd.DataFrame(), "Respons JSON kosong."

    if isinstance(data, dict):
        if data.get("status") == "error" or ("error" in data and not any(isinstance(v, list) for v in data.values())):
            return pd.DataFrame(), f"Error dari Apps Script: {data.get('error', data)}"
        extracted_list = None
        for key in ["data", "values", "records", "rows", "result", "items"]:
            if key in data and isinstance(data[key], list):
                extracted_list = data[key]
                break
        if extracted_list is None:
            for val in data.values():
                if isinstance(val, list):
                    extracted_list = val
                    break
        data = extracted_list if extracted_list is not None else [data]

    if not isinstance(data, list) or len(data) == 0:
        return pd.DataFrame(), "Data array kosong."

    if isinstance(data[0], list):
        header_idx = 0
        best_score = -1
        for i in range(min(5, len(data))):
            row_keys = [clean_header_key(cell) for cell in data[i]]
            score = sum(1 for k in row_keys if k in COLUMN_ALIASES)
            if score > best_score:
                best_score = score
                header_idx = i

        raw_headers = data[header_idx]
        seen = {}
        clean_headers = []
        for idx, h in enumerate(raw_headers):
            name = str(h).strip() if str(h).strip() else f"Kolom_{idx+1}"
            if name in seen:
                seen[name] += 1
                name = f"{name}_{seen[name]}"
            else:
                seen[name] = 1
            clean_headers.append(name)

        rows = data[header_idx + 1:]
        if not rows:
            return pd.DataFrame(columns=clean_headers), "Header ditemukan, namun belum ada baris data di bawahnya."
        padded_rows = [
            r[:len(clean_headers)] + [""] * max(0, len(clean_headers) - len(r))
            for r in rows
        ]
        return pd.DataFrame(padded_rows, columns=clean_headers), "OK (Format 2D Array)"

    if isinstance(data[0], dict):
        return pd.DataFrame(data), "OK (Format Object List)"

    return pd.DataFrame(), f"Format data tidak dikenali: {type(data[0])}"

@st.cache_data(ttl=15)
def load_data():
    empty_df = pd.DataFrame(columns=STANDARD_COLUMNS)
    diag = {"status": "Belum terhubung", "raw_cols": [], "raw_count": 0, "raw_kat_sample": []}
    try:
        res = requests.get(f"{APPS_SCRIPT_URL}?action=get_data", timeout=15, allow_redirects=True)
        if res.status_code != 200:
            diag["status"] = f"HTTP Error {res.status_code}"
            st.error(f"Gagal koneksi Cloud. HTTP: {res.status_code}")
            return empty_df, diag

        if "<!DOCTYPE html>" in res.text or "<html" in res.text.lower():
            diag["status"] = "Akses Ditolak (HTML Login Google)"
            st.error("Akses GET ditolak (HTML). Pastikan Apps Script diset ke 'Anyone'.")
            return empty_df, diag

        try:
            raw_json = res.json()
        except ValueError:
            diag["status"] = f"Bukan JSON: {res.text[:120]}"
            st.error("Respons GET dari Apps Script bukan JSON valid.")
            return empty_df, diag

        df_raw, parse_msg = parse_raw_payload_to_df(raw_json)
        diag["status"] = parse_msg
        diag["raw_cols"] = list(df_raw.columns) if not df_raw.empty else []
        diag["raw_count"] = len(df_raw)

        if df_raw.empty:
            return empty_df, diag

        df = normalize_columns(df_raw.copy())
        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = "-"

        # Hapus kolom aksi WA/Email lama jika terbawa dari sheet
        legacy_action_cols = ["Aksi WA Part 1", "Aksi WA Part 2", "Aksi Email Part", "Aksi WA Part"]
        df = df.drop(columns=legacy_action_cols, errors="ignore")

        for col in df.columns:
            df[col] = df[col].apply(
                lambda v: "-" if v is None or str(v).strip() in ["", "None", "nan", "NaN", "null"] else str(v).strip()
            )

        diag["raw_kat_sample"] = df["Kategori"].unique().tolist()[:10]

        df["No Polisi"] = df["No Polisi"].str.upper()
        df["Nama SA"] = df["Nama SA"].str.upper()

        check_cols = ["No PKB", "No Polisi", "Nama Customer", "Tipe Kendaraan", "Nama SA"]
        mask_has_data = df[check_cols].apply(lambda r: any(val != "-" for val in r), axis=1)
        df = df[mask_has_data].reset_index(drop=True)

        if df.empty:
            diag["status"] = "Semua baris kosong setelah pembersihan."
            return empty_df, diag

        df["Kategori"] = df.apply(normalize_kategori, axis=1)

        def make_identifier(row):
            pkb = str(row.get("No PKB", "-")).strip().upper()
            nopol = str(row.get("No Polisi", "-")).strip().upper()
            if pkb not in ["", "-", "BELUM ADA", "0"]:
                return f"PKB_{pkb}"
            if nopol not in ["", "-"]:
                return f"NOPOL_{nopol}"
            return f"ROW_{row.name}"

        df["Identifier"] = df.apply(make_identifier, axis=1)
        df = df.drop_duplicates(subset=["Identifier"], keep="last").drop(columns=["Identifier"]).reset_index(drop=True)

        extra_cols = [c for c in df.columns if c not in STANDARD_COLUMNS]
        df = df[STANDARD_COLUMNS + extra_cols]

        parsed_tgl = pd.to_datetime(df["Tgl PKB"], errors="coerce").dt.tz_localize(None)
        now = pd.Timestamp.now().normalize()
        df["Umur PKB (Hari)"] = (now - parsed_tgl).dt.days.fillna(0).astype(int)
        df["Tgl PKB"] = parsed_tgl.dt.strftime("%Y-%m-%d").fillna(df["Tgl PKB"])

        cols = list(df.columns)
        cols.remove("Umur PKB (Hari)")
        cols.insert(cols.index("Tgl PKB") + 1, "Umur PKB (Hari)")
        df = df[cols]

        df["Progress (%)"] = df.apply(
            lambda r: hitung_progress(r["Kategori"], r["Status Pekerjaan"]), axis=1
        )
        return df, diag
    except Exception as e:
        diag["status"] = f"Exception: {e}"
        st.error(f"Kesalahan saat memuat data Cloud: {e}")
        return empty_df, diag

def prepare_df_for_sheet(df):
    computed = [
        "Umur PKB (Hari)", "Progress (%)",
        "Aksi WA Part 1", "Aksi WA Part 2", "Aksi Email Part", "Aksi WA Part"
    ]
    df_clean = df.drop(columns=computed, errors="ignore").copy()
    for col in STANDARD_COLUMNS:
        if col not in df_clean.columns:
            df_clean[col] = "-"
    extra = [c for c in df_clean.columns if c not in STANDARD_COLUMNS]
    return df_clean[STANDARD_COLUMNS + extra].fillna("-").astype(str)

def save_data(df):
    df_to_save = prepare_df_for_sheet(df)
    payload = {
        "action": "save_data",
        "data": [df_to_save.columns.tolist()] + df_to_save.values.tolist()
    }
    sukses, msg, _ = post_to_apps_script(payload, timeout=30)
    if sukses:
        load_data.clear()
        return True
    st.error(f"Gagal menyimpan ke Google Sheets: {msg}")
    return False

def add_row_to_sheet(row_dict, fallback_df):
    clean_row = {col: str(row_dict.get(col, "-")) for col in STANDARD_COLUMNS}
    sukses, _, _ = post_to_apps_script({"action": "add_row", "row": clean_row}, timeout=25)
    if sukses:
        load_data.clear()
        return True
    return save_data(fallback_df)

def update_row_in_sheet(nopol, updates, fallback_df, no_pkb="-"):
    payload = {
        "action": "update_row",
        "nopol": str(nopol).strip().upper(),
        "no_pkb": str(no_pkb).strip().upper(),
        "updates": {k: str(v) for k, v in updates.items()}
    }
    sukses, _, _ = post_to_apps_script(payload, timeout=25)
    if sukses:
        load_data.clear()
        return True
    return save_data(fallback_df)

def compress_image(img_file, max_dim=1600, max_kb=1024):
    if not PIL_AVAILABLE:
        return img_file.getvalue(), img_file.name, img_file.type or "image/jpeg"
    try:
        img = Image.open(img_file)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        resample = getattr(Image, "Resampling", Image).LANCZOS
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), resample)
        buf = io.BytesIO()
        q = 85
        img.save(buf, format="JPEG", quality=q, optimize=True)
        while buf.tell() > max_kb * 1024 and q > 30:
            q -= 10
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q, optimize=True)
        buf.seek(0)
        new_name = img_file.name.rsplit(".", 1)[0] + "_compressed.jpg"
        return buf.getvalue(), new_name, "image/jpeg"
    except Exception:
        return img_file.getvalue(), img_file.name, img_file.type or "image/jpeg"

def upload_foto_cloud(img_file):
    img_bytes, img_name, img_type = compress_image(img_file)
    b64_str = base64.b64encode(img_bytes).decode("utf-8")

    candidate_actions = ["upload_image", "upload_foto", "upload", "upload_file", "uploadImage"]
    last_msg = "Action tidak dikenali"

    for act in candidate_actions:
        payload = {
            "action": act,
            "filename": img_name,
            "fileName": img_name,
            "mimeType": img_type,
            "data": b64_str,
            "base64": b64_str,
            "fileData": b64_str
        }
        sukses, msg, data = post_to_apps_script(payload, timeout=60)
        if sukses and isinstance(data, dict):
            file_url = (
                data.get("url")
                or data.get("fileUrl")
                or data.get("link")
                or data.get("webViewLink")
            )
            if not file_url and data.get("fileId"):
                file_url = f"https://drive.google.com/uc?export=view&id={data.get('fileId')}"
            if file_url:
                return file_url

        last_msg = msg
        if "tidak dikenali" not in str(msg).lower() and "unknown action" not in str(msg).lower():
            break

    st.error(
        f"Upload GDrive Gagal: {last_msg}. "
        "Pastikan fungsi doPost(e) di Google Apps Script sudah mendukung action 'upload_image' dan sudah di-Deploy versi terbaru."
    )
    return None

# ==========================================
# NOTIFIKASI WHATSAPP OTOMATIS KE SA MASING-MASING (GREEN API)
# ==========================================
def resolve_sa_wa(nama_sa, kategori):
    """Mencari nomor WhatsApp SA berdasarkan kode lengkap maupun potongan nama SA."""
    sa_clean = str(nama_sa).strip().upper()
    if sa_clean and sa_clean != "-":
        if sa_clean in WA_SA_MAP:
            return [WA_SA_MAP[sa_clean]]
        for kode_sa, no_wa in WA_SA_MAP.items():
            prefix = re.sub(r"\d+", "", kode_sa)
            if kode_sa in sa_clean or sa_clean in kode_sa or (prefix and prefix in sa_clean):
                return [no_wa]

    if kategori == "Body Repair":
        return list(WA_SA_BR_FALLBACK)
    return list(WA_SA_GR_FALLBACK)

def send_auto_wa(nopol, status, catatan, kategori, nama_sa, foto_urls, spk="-", status_or="-", dok="-", no_pkb="-"):
    target_wa = resolve_sa_wa(nama_sa, kategori)
    if status == "Menunggu Part":
        target_wa.extend(WA_ADMIN_PART)

    target_wa = list(dict.fromkeys([num.strip() for num in target_wa if str(num).strip()]))
    wa_errors = []

    if not target_wa:
        wa_errors.append(f"Tidak ada nomor WA tujuan untuk SA '{nama_sa}'.")
        return wa_errors

    pesan = (
        f"*UPDATE PROGRESS KENDARAAN*\n\n"
        f"No PKB: {no_pkb}\n"
        f"No Polisi: {nopol}\n"
        f"SA: {nama_sa}\n"
        f"Kategori: {kategori}\n"
        f"Status: *{status}*\n"
        f"Catatan: {catatan}"
    )
    if spk != "-" or status_or != "-" or dok != "-":
        pesan += f"\n\n*Data Asuransi:*\nSPK: {spk}\nBayar OR: {status_or}\nDokumen: {dok}"

    headers = {"Content-Type": "application/json"}
    base_url = f"{GREEN_API_HOST.rstrip('/')}/waInstance{GREEN_API_ID_INSTANCE}"
    url_text = f"{base_url}/sendMessage/{GREEN_API_TOKEN}"
    url_file = f"{base_url}/sendFileByUrl/{GREEN_API_TOKEN}"

    valid_urls = [u.strip() for u in (foto_urls or []) if str(u).strip().startswith("http")]

    try:
        for clean_num in target_wa:
            chat_id = f"{clean_num}@c.us"
            if valid_urls:
                for i, url in enumerate(valid_urls):
                    cap = pesan if i == 0 else f"Foto Progress ({i+1}) - {nopol} [{status}]"
                    body_file = {
                        "chatId": chat_id,
                        "urlFile": url,
                        "fileName": f"Progress_{nopol.replace(' ', '_')}_{i+1}.jpg",
                        "caption": cap
                    }
                    r = requests.post(url_file, headers=headers, json=body_file, timeout=15)
                    if str(r.status_code) != "200":
                        wa_errors.append(f"Gagal kirim foto ke {clean_num}: HTTP {r.status_code}")
            else:
                body_txt = {"chatId": chat_id, "message": pesan}
                r = requests.post(url_text, headers=headers, json=body_txt, timeout=10)
                if str(r.status_code) != "200":
                    wa_errors.append(f"Gagal kirim pesan ke {clean_num}: HTTP {r.status_code}")
    except Exception as e:
        wa_errors.append(f"Error Green API: {e}")

    return wa_errors

# ==========================================
# DASHBOARD UTAMA
# ==========================================
df, diag_info = load_data()
st.session_state["df_data"] = df

def style_umur_pkb(val):
    try:
        if int(val) > 60:
            return "color: #ff4b4b; font-weight: bold;"
    except Exception:
        pass
    return ""

def get_col_configs(target_df):
    cfg = {}
    if "Foto PKB" in target_df.columns:
        cfg["Foto PKB"] = st.column_config.TextColumn("Foto Progress")
    if "Progress (%)" in target_df.columns:
        cfg["Progress (%)"] = st.column_config.ProgressColumn(
            "Progress", format="%d%%", min_value=0, max_value=100
        )
    return cfg

if "notif_sukses" in st.session_state:
    st.success(st.session_state["notif_sukses"])
    del st.session_state["notif_sukses"]

if "wa_errors" in st.session_state:
    st.error("Gagal mengirim WhatsApp:\n" + "\n".join(st.session_state["wa_errors"]))
    del st.session_state["wa_errors"]

dash_title = (
    f"<h3 style='display:flex;align-items:center;color:#1b5e20;'>"
    f"<img src='{DAIHATSU_LOGO_PNG}' style='height:30px;margin-right:15px;'>"
    f"Live Service Dashboard</h3>"
)
st.markdown(dash_title, unsafe_allow_html=True)

if not df.empty:
    status_series = df["Status Pekerjaan"].astype(str).str.strip().str.lower()
    is_done = status_series.isin(["selesai", "done", "closed"])
    df_wip = df[~is_done].copy()
    df_selesai = df[is_done].copy()
else:
    df_wip = df.copy()
    df_selesai = pd.DataFrame(columns=STANDARD_COLUMNS)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Unit WIP", f"{len(df_wip)} Unit")
if not df_wip.empty:
    gr_count = int((df_wip["Kategori"] == "General Repair").sum())
    br_count = int((df_wip["Kategori"] == "Body Repair").sum())
else:
    gr_count, br_count = 0, 0
m2.metric("Antrean GR", f"{gr_count} Unit")
m3.metric("Antrean BR", f"{br_count} Unit")
m4.metric("Unit Selesai", f"{len(df_selesai)} Unit")

st.markdown("<hr style='border:1px solid #dcedc8;margin:10px 0 20px 0;'>", unsafe_allow_html=True)

def execute_form_logic(selected_nopol):
    global df
    if selected_nopol and not df.empty and selected_nopol in df["No Polisi"].values:
        row = df[df["No Polisi"] == selected_nopol].iloc[-1]
        kat_asli = row.get("Kategori", "General Repair")
        nama_sa = str(row.get("Nama SA", "-"))
        no_pkb = str(row.get("No PKB", "-"))
        target_wa_preview = ", ".join(resolve_sa_wa(nama_sa, kat_asli))

        st.success(
            f"**{row.get('Nama Customer', '-')}** | {selected_nopol} | "
            f"Kategori: **{kat_asli}** | SA: **{nama_sa}** (WA Otomatis: `{target_wa_preview}`) | {row.get('Tipe Kendaraan', '-')}"
        )

        if kat_asli == "Body Repair":
            st.warning("⚠️ Pekerjaan **Body Repair** wajib melampirkan foto progress terbaru setiap kali melakukan update.")

        with st.form(f"form_update_{selected_nopol}", clear_on_submit=True):
            opsi_status = ["Menunggu Pekerjaan", "Sedang Dikerjakan", "Menunggu Part", "Quality Control", "Selesai"]
            if kat_asli == "Body Repair":
                opsi_status = [
                    "Antrian Pekerjaan", "Bongkar", "Ketok / Las", "Dempul",
                    "Epoxy", "Pengecatan / Oven", "Poles", "Perakitan / Pemasangan",
                    "Menunggu Part", "Quality Control", "Selesai"
                ]

            curr_status = str(row.get("Status Pekerjaan", ""))
            idx = opsi_status.index(curr_status) if curr_status in opsi_status else 0

            new_status = st.selectbox("Progress Pekerjaan:", opsi_status, index=idx)
            new_ket = st.text_area("Catatan Tambahan:", value=str(row.get("Keterangan Lanjutan", "-")))

            st.markdown("---")
            curr_spk = str(row.get("Status SPK Asuransi", "-"))
            is_asuransi = st.checkbox("Pelanggan Asuransi", value=(curr_spk not in ["-", ""]))

            if is_asuransi:
                c1, c2, c3 = st.columns(3)
                with c1:
                    opsi_spk = ["-", "Menunggu SPK", "SPK Turun", "Revisi SPK"]
                    new_spk = st.selectbox("Status SPK:", opsi_spk, index=opsi_spk.index(curr_spk) if curr_spk in opsi_spk else 0)
                with c2:
                    curr_or = str(row.get("Status Pembayaran OR", "-"))
                    opsi_or = ["-", "Belum Bayar OR", "Sudah Bayar OR"]
                    new_or = st.selectbox("Pembayaran OR:", opsi_or, index=opsi_or.index(curr_or) if curr_or in opsi_or else 0)
                with c3:
                    curr_dok = str(row.get("Kelengkapan Dokumen Asuransi", "-"))
                    opsi_dok = ["-", "Dokumen Belum Lengkap", "Dokumen Lengkap"]
                    new_dok = st.selectbox("Dokumen Klaim:", opsi_dok, index=opsi_dok.index(curr_dok) if curr_dok in opsi_dok else 0)
            else:
                new_spk, new_or, new_dok = "-", "-", "-"

            st.markdown("---")
            foto_lama = str(row.get("Foto PKB", "-")).strip()
            urls_lama = [u.strip() for u in foto_lama.split(",") if u.strip().startswith("http")] if foto_lama != "-" else []
            if urls_lama:
                st.caption("Foto Progress Sebelumnya:")
                cols = st.columns(min(len(urls_lama), 4))
                for i, u in enumerate(urls_lama):
                    cols[i % 4].image(u, caption=f"Foto {i+1}")

            label_upload = (
                "Upload Foto Progress Terbaru (WAJIB untuk Body Repair) *"
                if kat_asli == "Body Repair"
                else "Upload Foto Progress (Opsional)"
            )
            uploaded = st.file_uploader(
                label_upload, type=["jpg", "jpeg", "png"],
                accept_multiple_files=True, key=f"up_{selected_nopol}"
            )

            if st.form_submit_button("💾 SIMPAN UPDATE & KIRIM WA KE SA", width="stretch"):
                if kat_asli == "Body Repair" and not uploaded:
                    st.error("❌ Pekerjaan Body Repair WAJIB mengunggah foto progress sebelum menyimpan update!")
                else:
                    ok_up = True
                    new_links = []
                    if uploaded:
                        with st.spinner("Mengupload foto progress ke Google Drive..."):
                            for f in uploaded:
                                link = upload_foto_cloud(f)
                                if link:
                                    new_links.append(link)
                                else:
                                    ok_up = False
                                    break
                    if ok_up:
                        semua_foto = list(dict.fromkeys(urls_lama + new_links))
                        foto_final = ", ".join(semua_foto) if semua_foto else "-"
                        updates = {
                            "Kategori": kat_asli,
                            "Status Pekerjaan": new_status,
                            "Keterangan Lanjutan": new_ket,
                            "Status SPK Asuransi": new_spk,
                            "Status Pembayaran OR": new_or,
                            "Kelengkapan Dokumen Asuransi": new_dok,
                            "Tanggal Terakhir Diupdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Foto PKB": foto_final
                        }
                        for k, v in updates.items():
                            df.loc[df["No Polisi"] == selected_nopol, k] = v

                        with st.spinner("Memperbarui database Google Sheets..."):
                            sukses = update_row_in_sheet(selected_nopol, updates, df, no_pkb=no_pkb)

                        if sukses:
                            kirim_urls = new_links if new_links else urls_lama
                            wa_err = send_auto_wa(
                                selected_nopol, new_status, new_ket, kat_asli,
                                nama_sa, kirim_urls, new_spk, new_or, new_dok, no_pkb=no_pkb
                            )
                            if wa_err:
                                st.session_state["wa_errors"] = wa_err
                                st.session_state["notif_sukses"] = f"Database {selected_nopol} diperbarui, namun notifikasi WA ke SA gagal."
                            else:
                                st.session_state["notif_sukses"] = (
                                    f"Database {selected_nopol} otomatis diperbarui & progress terkirim ke WA SA ({nama_sa})!"
                                )
                            st.rerun()
    elif selected_nopol:
        st.error("Kendaraan tidak ditemukan di Database.")

def render_update_form(kategori_filter):
    st.markdown(f"#### Pencarian Kendaraan WIP ({kategori_filter})")
    if df_wip.empty:
        st.warning("Tidak ada data WIP aktif.")
        return
    df_kat = df_wip[df_wip["Kategori"] == kategori_filter]
    if df_kat.empty:
        st.info(f"Belum ada kendaraan aktif pada kategori {kategori_filter}.")
        return
    list_nopol = [n for n in df_kat["No Polisi"].dropna().unique().tolist() if n != "-"]
    metode = st.radio("Metode:", ["Pilih dari List", "Ketik Manual"], key=f"rad_{kategori_filter}", horizontal=True)
    if metode == "Pilih dari List":
        sel = st.selectbox("Pilih No Polisi", [""] + list_nopol)
    else:
        sel = st.text_input("Ketik No Polisi").strip().upper()
    execute_form_logic(sel)

# ==========================================
# RENDER HALAMAN SESUAI MENU
# ==========================================
if menu_pilihan == "📊 SEMUA WIP":
    st.markdown("#### Database WIP Aktif (Real-Time Google Sheets)")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        cari = st.text_input("Cari No Polisi / Customer / No PKB:").strip().upper()
    with f2:
        f_kat = st.selectbox("Filter Kategori:", ["Semua", "General Repair", "Body Repair"])
    with f3:
        sa_opts = ["Semua"] + sorted([
            s for s in df_wip["Nama SA"].dropna().unique().tolist()
            if str(s).strip() not in ["", "-"]
        ]) if not df_wip.empty else ["Semua"]
        f_sa = st.selectbox("Filter SA:", sa_opts)

    df_disp = df_wip.copy()
    if not df_disp.empty:
        if cari:
            mask = (
                df_disp["No Polisi"].astype(str).str.upper().str.contains(cari, na=False) |
                df_disp["Nama Customer"].astype(str).str.upper().str.contains(cari, na=False) |
                df_disp["No PKB"].astype(str).str.upper().str.contains(cari, na=False)
            )
            df_disp = df_disp[mask]
        if f_kat != "Semua":
            df_disp = df_disp[df_disp["Kategori"] == f_kat]
        if f_sa != "Semua":
            df_disp = df_disp[df_disp["Nama SA"] == f_sa]

    st.dataframe(
        df_disp.style.map(style_umur_pkb, subset=["Umur PKB (Hari)"] if "Umur PKB (Hari)" in df_disp.columns else []),
        width="stretch",
        hide_index=True,
        column_config=get_col_configs(df_disp)
    )

    with st.expander("🔍 Diagnostik Koneksi & Struktur Data Google Sheets", expanded=df.empty):
        st.write(f"**Status Pembacaan:** {diag_info.get('status')}")
        st.write(f"**Total Baris Terbaca:** {len(df)} baris (Mentah: {diag_info.get('raw_count')} baris)")
        st.write(f"**Kolom Asli di Sheet:** `{diag_info.get('raw_cols')}`")
        st.write(f"**Nilai Mentah Kolom Kategori di Sheet:** `{diag_info.get('raw_kat_sample')}`")
        st.write(f"**Hasil Normalisasi WIP:** General Repair = `{gr_count}` unit | Body Repair = `{br_count}` unit")
        if df.empty:
            st.warning(
                "Jika kolom asli di sheet terlihat kosong atau salah nama sheet, pastikan fungsi `doGet(e)` "
                "di Google Apps Script membaca sheet yang benar dan Web App sudah di-Deploy dengan akses **Anyone**."
            )

elif menu_pilihan == "📱 TAMPILAN MOBILE":
    st.markdown("#### Menu Update Mobile (WIP)")
    if df_wip.empty:
        st.warning("Tidak ada data WIP aktif.")
    else:
        list_nopol = [n for n in df_wip["No Polisi"].dropna().unique().tolist() if n != "-"]
        t1, t2 = st.tabs(["Pilih dari List", "Cari Manual"])
        with t1:
            n_list = st.selectbox("Cari No Polisi", [""] + list_nopol, key="mob_list")
        with t2:
            n_man = st.text_input("Ketik No Polisi", key="mob_man").strip().upper()
        execute_form_logic(n_list if n_list else n_man)

elif menu_pilihan == "🛠️ ANTREAN GR":
    st.markdown("#### Daftar Antrean General Repair (GR)")
    df_gr = df_wip[df_wip["Kategori"] == "General Repair"] if not df_wip.empty else pd.DataFrame(columns=STANDARD_COLUMNS)
    st.dataframe(
        df_gr.style.map(style_umur_pkb, subset=["Umur PKB (Hari)"] if "Umur PKB (Hari)" in df_gr.columns else []),
        width="stretch", hide_index=True, column_config=get_col_configs(df_gr)
    )

elif menu_pilihan == "📝 UPDATE GR":
    render_update_form("General Repair")

elif menu_pilihan == "🔨 ANTREAN BR":
    st.markdown("#### Daftar Antrean Body Repair (BR)")
    df_br = df_wip[df_wip["Kategori"] == "Body Repair"] if not df_wip.empty else pd.DataFrame(columns=STANDARD_COLUMNS)
    st.dataframe(
        df_br.style.map(style_umur_pkb, subset=["Umur PKB (Hari)"] if "Umur PKB (Hari)" in df_br.columns else []),
        width="stretch", hide_index=True, column_config=get_col_configs(df_br)
    )

elif menu_pilihan == "📝 UPDATE BR":
    render_update_form("Body Repair")

elif menu_pilihan == "✅ RIWAYAT SELESAI":
    st.markdown("#### Riwayat Kendaraan Selesai")
    st.dataframe(
        df_selesai.style.map(style_umur_pkb, subset=["Umur PKB (Hari)"] if "Umur PKB (Hari)" in df_selesai.columns else []),
        width="stretch", hide_index=True, column_config=get_col_configs(df_selesai)
    )

elif menu_pilihan == "➕ TAMBAH MOBIL TAMU":
    st.markdown("#### Input Kendaraan Tamu / Manual")
    with st.form("form_input_tamu", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nopol_baru = st.text_input("No Polisi *").strip().upper()
            nama_cust_baru = st.text_input("Nama Customer", value="TAMU / NON-PKB").strip().upper()
            tipe_baru = st.text_input("Tipe Kendaraan *").strip()
            warna_baru = st.text_input("Warna Kendaraan").strip()
        with c2:
            nama_sa_baru = st.text_input("Nama SA *").strip().upper()
            kategori_baru = st.selectbox("Kategori Pekerjaan", ["General Repair", "Body Repair"])
            catatan_baru = st.text_area("Keterangan Awal / Keluhan").strip()
            foto_barus = st.file_uploader(
                "Upload Foto Kendaraan (Wajib untuk Body Repair)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )

        if st.form_submit_button("💾 SIMPAN DATA KENDARAAN", width="stretch"):
            if not nopol_baru or not tipe_baru or not nama_sa_baru:
                st.error("No Polisi, Tipe Kendaraan, dan Nama SA wajib diisi!")
            elif kategori_baru == "Body Repair" and not foto_barus:
                st.error("❌ Pekerjaan Body Repair WAJIB melampirkan foto awal/progress!")
            else:
                link_fotos = []
                ok_up = True
                if foto_barus:
                    with st.spinner("Mengupload foto..."):
                        for f in foto_barus:
                            link = upload_foto_cloud(f)
                            if link:
                                link_fotos.append(link)
                            else:
                                ok_up = False
                                break
                if ok_up:
                    gab_tipe = f"{tipe_baru} ({warna_baru})" if warna_baru else tipe_baru
                    status_awal = "Menunggu Pekerjaan" if kategori_baru == "General Repair" else "Antrian Pekerjaan"
                    new_data = {
                        "No PKB": "BELUM ADA",
                        "Tipe Kendaraan": gab_tipe,
                        "No Polisi": nopol_baru,
                        "Nama Customer": nama_cust_baru or "TAMU / NON-PKB",
                        "Kategori": kategori_baru,
                        "Status Pekerjaan": status_awal,
                        "Nama SA": nama_sa_baru,
                        "Tgl PKB": datetime.now().strftime("%Y-%m-%d"),
                        "Tanggal Terakhir Diupdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Keterangan Lanjutan": catatan_baru or "-",
                        "Foto PKB": ", ".join(link_fotos) if link_fotos else "-",
                        "Status SPK Asuransi": "-",
                        "Status Pembayaran OR": "-",
                        "Kelengkapan Dokumen Asuransi": "-"
                    }
                    df_new = pd.DataFrame([new_data])
                    df_upd = pd.concat([df, df_new], ignore_index=True) if not df.empty else df_new
                    with st.spinner("Menambahkan data ke Google Sheets..."):
                        if add_row_to_sheet(new_data, df_upd):
                            wa_err = send_auto_wa(
                                nopol_baru, status_awal, catatan_baru or "Unit Tamu Masuk",
                                kategori_baru, nama_sa_baru, link_fotos, no_pkb="BELUM ADA"
                            )
                            if wa_err:
                                st.session_state["wa_errors"] = wa_err
                            st.session_state["notif_sukses"] = (
                                f"Kendaraan Tamu {nopol_baru} tersimpan ke database & notifikasi dikirim ke SA {nama_sa_baru}!"
                            )
                            st.rerun()

    st.markdown("---")
    st.markdown("#### Riwayat Kendaraan Tamu (Input Manual)")
    df_tamu = df[df["No PKB"] == "BELUM ADA"].copy() if not df.empty else pd.DataFrame(columns=STANDARD_COLUMNS)
    kolom_tampil = [
        "No Polisi", "Nama Customer", "Tipe Kendaraan", "Nama SA",
        "Kategori", "Status Pekerjaan", "Keterangan Lanjutan",
        "Tgl PKB", "Tanggal Terakhir Diupdate"
    ]
    st.dataframe(df_tamu[[c for c in kolom_tampil if c in df_tamu.columns]], width="stretch", hide_index=True)
