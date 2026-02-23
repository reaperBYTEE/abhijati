import streamlit as st
import pandas as pd
import qrcode
import requests
import base64
import time
from io import BytesIO

# --- 1. SETTING PAGE & TAMPILAN ANTI-GHOIB ---
st.set_page_config(page_title="AIS ABHIJATI ADMIN", layout="centered")

st.markdown("""
    <style>
    /* Background utama gelap elegan */
    .stApp { background-color: #0f172a; }

    /* TOMBOL BIRU ABHIJATI - TEKS HITAM PEKAT (Kontras Tinggi) */
    div.stButton > button:first-child {
        background-color: #38bdf8 !important;
        color: #000000 !important; 
        font-weight: 900 !important;
        font-size: 18px !important;
        border-radius: 12px;
        height: 3.5em;
        width: 100%;
        border: 2px solid #ffffff;
        box-shadow: 0px 4px 15px rgba(56, 189, 248, 0.4);
    }
    
    /* Hover Effect Tombol */
    div.stButton > button:hover {
        background-color: #ffffff !important;
        color: #38bdf8 !important;
        border: 2px solid #38bdf8;
    }

    /* INPUT BOX BIAR JELAS (Teks Biru Cerah) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        font-weight: bold !important;
    }

    /* Label Input (Nama Barang, dll) agar Putih Terang */
    label p { 
        color: #f8fafc !important; 
        font-size: 15px !important; 
        font-weight: bold !important;
        margin-bottom: -10px;
    }

    /* Header */
    h1 { color: #38bdf8 !important; text-align: center; font-weight: 800; }
    h3 { color: #94a3b8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE GOOGLE SHEETS & CONFIG ---
# Link Publish to Web Anda (Jalur Cepat Baca)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR5brEySXNZAel-ZXXi9psodyPHSBCXUFzSaNHxOK2Ym35FmhWkfw4tQNWVs99gC41rHsx6lbdeKddz/pub?gid=0&single=true&output=csv"

# API Key ImgBB (Silakan ganti dengan Key Anda sendiri nanti)
IMGBB_API_KEY = "MASUKKAN_API_KEY_IMGBB_ANDA" 

# --- 3. LOGIKA CEK ID OTOMATIS ---
try:
    df_existing = pd.read_csv(CSV_URL)
    # Mencari angka terbesar di kolom 'no', jika kosong mulai dari 1
    if not df_existing.empty and 'no' in df_existing.columns:
        next_id = int(df_existing['no'].max() + 1)
    else:
        next_id = 1
except Exception:
    next_id = 1

# --- 4. FUNGSI UPLOAD GAMBAR (ImgBB) ---
def upload_to_imgbb(image_file):
    if IMGBB_API_KEY == "a1e87954926748a99225b52ce641c807":
        st.error("⚠️ API Key ImgBB belum diisi!")
        return None
    
    url = "https://api.imgbb.com/1/upload"
    img_bytes = image_file.read()
    encoded_string = base64.b64encode(img_bytes)
    
    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_string
    }
    
    try:
        res = requests.post(url, payload)
        if res.status_code == 200:
            return res.json()['data']['url']
    except:
        return None
    return None

# --- 5. UI UTAMA ---
st.title("🏢 AIS ABHIJATI ADMIN")
st.markdown("<h3 style='text-align: center;'>Fase Beta - Cloud Integration</h3>", unsafe_allow_html=True)
st.divider()

with st.form("form_input_aset"):
    col1, col2 = st.columns(2)
    
    with col1:
        no = st.number_input("Nomor Urut (ID)", value=next_id, step=1)
        nama = st.text_input("Nama Barang", placeholder="Contoh: Mesin Jahit Singer")
        kategori = st.selectbox("Kategori Aset", ["Mesin Produksi", "Elektronik", "Kendaraan", "Furniture", "Alat Kantor"])
        kode = st.text_input("Kode Aset", value=f"ASD/MSN/I/2026/PROD/{no:02d}")

    with col2:
        lokasi = st.text_input("Lokasi Penempatan", value="ABHIJATI_PRODUKSI")
        jumlah = st.text_input("Jumlah/Satuan", value="1 Unit")
        bulan = st.selectbox("Bulan Beli", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        kondisi = st.selectbox("Status Kondisi", ["Berfungsi", "Rusak", "Dalam Perbaikan", "Maintenance"])

    st.write("---")
    uploaded_file = st.file_uploader("📸 Upload Foto Barang (Cloud Storage)", type=["jpg", "png", "jpeg"])
    
    # Tombol Submit Gagah
    submitted = st.form_submit_button("SIMPAN DATA & GENERATE QR")

# --- 6. LOGIKA SETELAH TOMBOL DIKLIK ---
if submitted:
    if not nama:
        st.error("❌ Nama Barang tidak boleh kosong!")
    else:
        with st.spinner('Sedang memproses foto dan QR...'):
            # 1. Proses Foto
            url_foto = ""
            if uploaded_file:
                url_foto = upload_to_imgbb(uploaded_file)
            
            # 2. Buat Link QR (Target Vercel)
            link_target = f"https://abhijati-reaperbytees-projects.vercel.app/?id={no}"
            qr = qrcode.make(link_target)
            
            # 3. Tampilkan Hasil
            st.balloons()
            st.success(f"✅ Berhasil! Data ID {no} siap dimasukkan ke Sheets.")
            
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.info("🖼️ Preview Foto Cloud")
                if url_foto:
                    st.image(url_foto, use_container_width=True)
                    st.caption(f"Link: {url_foto}")
                else:
                    st.warning("Tanpa Foto")

            with res_col2:
                st.info("📱 Scan QR Code")
                buf = BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf, width=230)
                st.download_button(
                    label="💾 Download QR Code",
                    data=buf.getvalue(),
                    file_name=f"QR_AIS_{no}.png",
                    mime="image/png"
                )
            
            st.warning("⚠️ Langkah Terakhir: Besok pagi kita aktifkan fitur 'Auto-Write' ke Sheets agar Anda tidak perlu copy-paste manual lagi!")

