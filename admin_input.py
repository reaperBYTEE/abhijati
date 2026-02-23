import streamlit as st
import json
import os
import qrcode
import pandas as pd
from PIL import Image
from io import BytesIO

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Admin A.I.S Abhijati", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1e293b; color: #38bdf8; border: 1px solid #334155; border-radius: 8px;
    }
    div.stButton > button:first-child {
        background-color: #38bdf8; color: #0f172a; font-weight: bold; border-radius: 20px; width: 100%; border: none; height: 3em;
    }
    div.stButton > button:first-child:hover { background-color: #0ea5e9; color: white; }
    h1, h2, h3 { color: #38bdf8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KONFIGURASI FILE & FOLDER ---
file_json = 'data_inven_mesin.json'
qr_folder = 'QR_ABHIJATI_OFFICIAL'
img_folder = 'img'
base_url = "https://abhijati-reaperbytees-projects.vercel.app/?id="

for folder in [qr_folder, img_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def load_data():
    if os.path.exists(file_json):
        try:
            with open(file_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

# --- 3. UI UTAMA ---
st.title("🏢 A.I.S (Abhijati Inventory System)")
st.write("Silakan input aset untuk kantor Pusat (Jogja) atau Cabang (Cisauk).")

data_sekarang = load_data()
suggested_no = max([item['no'] for item in data_sekarang]) + 1 if data_sekarang else 1

# Buka Form
with st.form("form_aset", clear_on_submit=False):
    st.subheader("📝 Tambah Aset Baru")
    
    col_kat, col_no = st.columns([3, 1])
    with col_kat:
        kategori = st.selectbox("Kategori Aset", [
            "Mesin Produksi", "Elektronik (Laptop, AC, dll)", 
            "Kendaraan", "Tanah & Bangunan", "Furniture & Kantor"
        ])
    with col_no:
        no = st.number_input("Nomor Urut (ID)", min_value=1, value=suggested_no, step=1)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Barang/Mesin", placeholder="Contoh: Honda Vario")
        kode = st.text_input("Kode Aset (Sesuai SOP)", value=f"ASD/MSN/I/2026/PROD/{no:02d}")
        jumlah = st.text_input("Jumlah/Satuan", value="1 Unit")
        uploaded_file = st.file_uploader("📸 Upload Foto Barang", type=["jpg", "png", "jpeg"])
    
    with col2:
        c_bln, c_thn = st.columns(2)
        with c_bln:
            bulan = st.selectbox("Bulan Beli", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        with c_thn:
            tahun = st.text_input("Tahun Beli", value="2026")
            
        lokasi = st.text_input("Lokasi Penempatan", value="ABHIJATI_PRODUKSI")
        kondisi = st.selectbox("Kondisi Saat Ini", ["Berfungsi", "Rusak", "Dalam Perbaikan", "Dijual/Sewa"])

    # Tombol submit hanya untuk memproses form
    submit = st.form_submit_button("💾 SIMPAN KE DATABASE & BUAT QR")

# --- 4. PROSES LOGIKA (DI LUAR FORM) ---
# Bagian ini sejajar dengan 'with st.form', bukan di dalamnya.
if submit:
    if not nama or not kode:
        st.error("Waduh! Nama Barang dan Kode Aset jangan dikosongin ya.")
    else:
        # PROSES FOTO
        nama_foto = f"mesin_{no}.jpg" if uploaded_file else ""
        if uploaded_file:
            img = Image.open(uploaded_file)
            img.thumbnail((800, 800)) 
            img.convert('RGB').save(os.path.join(img_folder, nama_foto), "JPEG", quality=85)

        # SIMPAN JSON
        entry_baru = {
            "no": int(no),
            "kategori": kategori,
            "kode_barang": kode,
            "nama_barang": nama,
            "jumlah_item": jumlah,
            "bulan_pembelian": bulan,
            "tahun_pembelian": tahun,
            "lokasi": lokasi,
            "keterangan": kondisi,
            "gambar": nama_foto
        }
        
        data_sekarang.append(entry_baru)
        with open(file_json, 'w', encoding='utf-8') as f:
            json.dump(data_sekarang, f, indent=2)

        # GENERATE QR
        isi_qr = f"{base_url}{no}"
        qr_img = qrcode.make(isi_qr)
        nama_qr = f"{no}_{nama.replace(' ', '_')}.png"
        qr_img.save(os.path.join(qr_folder, nama_qr))

        st.success(f"✅ Mantap! {nama} berhasil disimpan ke database.")
        
        # PREVIEW & DOWNLOAD
        st.divider()
        st.subheader("✅ QR Code & Dokumentasi")
        c1, c2 = st.columns([1,3])
        with c1:
            st.image(os.path.join(qr_folder, nama_qr), width=200, caption="Scan untuk detail")
            
            # Menyiapkan data untuk download button
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            st.download_button(
                label="💾 DOWNLOAD GAMBAR QR",
                data=buf.getvalue(),
                file_name=nama_qr,
                mime="image/png"
            )
        with c2:
            if uploaded_file:
                st.image(os.path.join(img_folder, nama_foto), width=300, caption="Preview Foto Mesin")
            st.info(f"**Ringkasan Data:**\n- ID: {no}\n- Kode: {kode}\n- Lokasi: {lokasi}")

# --- 5. MONITORING DATA ---
st.divider()
st.subheader("📋 Daftar Seluruh Aset")
if data_sekarang:
    df_tampil = pd.DataFrame(data_sekarang)
    st.dataframe(df_tampil, use_container_width=True)
