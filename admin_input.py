import streamlit as st
import qrcode
import requests
import base64
from io import BytesIO

# =========================================================
# 1. LINK JEMBATAN ASLI MILIKMU (SUDAH DIUPDATE!)
# =========================================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyryX8kH8Fjtq5bK_BPPWn6b1fU0CLBjiNqymaFCl7hWaRgRE0UVPwSfam8BLlBmiIcxw/exec"

IMGBB_API_KEY = "a1e87954926748a99225b52ce641c807"

st.set_page_config(page_title="AIS ABHIJATI ADMIN", layout="centered")

# Custom CSS biar tampilan makin sangar
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #1e293b !important; color: white !important; border: 1px solid #38bdf8 !important;
    }
    div.stButton > button:first-child {
        background-color: #38bdf8 !important; color: #000 !important;
        font-weight: bold; width: 100%; border-radius: 10px; height: 3.5em; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 AIS ADMIN - LIVE SYNC")
st.write("Database: Abhijati Inventory System (Connected ✅)")

# Map singkatan untuk saran kode
prefix_map = {
    "tanah":"TNH",
    "Bangunan":"BGN",
    "Mesin Produksi": "MSN",
    "Kendaraan": "TRN",
    "Elektronik": "ELK",
    "Furniture": "FURN",
    "Alat Kantor": "OFC"
}

# --- FORM INPUT ---
with st.form("main_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        no = st.number_input("ID Unit (Nomor Urut)", min_value=1, value=1, step=1)
        nama = st.text_input("Nama Barang", placeholder="Misal: Forklift Toyota")
        kategori = st.selectbox("Kategori", list(prefix_map.keys()))
        tahun = st.number_input("Tahun Pembelian", min_value=1900, max_value=2100, value=2024)
        
    with col2:
        lokasi = st.text_input("Lokasi Penempatan", value="ABHIJATI_PRODUKSI")
        kondisi = st.selectbox("Kondisi", ["Berfungsi", "Rusak", "Maintenance"])
        bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        
        # Saran kode dinamis tapi tetap bisa diedit manual
        singkatan = prefix_map.get(kategori, "AST")
        saran_kode = f"ASD/{singkatan}/{tahun}/{no:02d}"
        kode_barang = st.text_input("Kode Aset (Bebas Edit)", value=saran_kode)
    
    uploaded_file = st.file_uploader("Upload Foto Barang", type=["jpg", "png", "jpeg"])
    submitted = st.form_submit_button("SIMPAN DATA & CETAK QR")

# --- PROSES EKSEKUSI ---
if submitted:
    if not nama or not kode_barang:
        st.error("❌ Nama Barang dan Kode tidak boleh kosong!")
    else:
        with st.spinner("Mengirim data ke database..."):
            # 1. Upload ke ImgBB
            url_foto = ""
            if uploaded_file:
                try:
                    file_bytes = uploaded_file.read()
                    res_img = requests.post("https://api.imgbb.com/1/upload", 
                                            data={"key": IMGBB_API_KEY, "image": base64.b64encode(file_bytes)})
                    if res_img.status_code == 200:
                        url_foto = res_img.json()['data']['url']
                except:
                    st.warning("Gagal upload foto, data teks tetap dikirim.")

            # 2. Payload Data untuk Google Sheets
            payload = {
                "no": no,
                "kategori": kategori,
                "kode": kode_barang,
                "nama": nama,
                "jumlah": "1 Unit",
                "bulan": bulan,
                "tahun": tahun,
                "lokasi": lokasi,
                "kondisi": kondisi,
                "gambar": url_foto
            }
            
            try:
                # Tembak ke Apps Script
                response = requests.post(WEB_APP_URL, json=payload)
                
                if response.status_code == 200:
                    st.success(f"✅ SUKSES! Aset {nama} sudah masuk ke Google Sheets.")
                    
                    # 3. Generate QR (Link ke Vercel)
                    link_target = f"https://abhijati-reaperbytees-projects.vercel.app/?id={kode_barang}"
                    qr = qrcode.make(link_target)
                    
                    # Tampilkan hasil di UI
                    st.divider()
                    res_col1, res_col2 = st.columns(2)
                    with res_col1:
                        if url_foto: 
                            st.image(url_foto, caption="Foto Aset Terupload")
                        else:
                            st.info("Data terkirim tanpa foto.")
                    with res_col2:
                        buf = BytesIO()
                        qr.save(buf, format="PNG")
                        st.image(buf, caption=f"Scan ID: {no}", width=200)
                else:
                    st.error(f"Gagal kirim ke Sheets. Kode Error: {response.status_code}")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")

