import streamlit as st
import json
import os

st.markdown("""
    <style>
    /* Mengubah warna latar belakang aplikasi */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Mengubah gaya inputan (TextBox) */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: #38bdf8;
        border: 1px solid #334155;
        border-radius: 8px;
    }
    
    /* Mengubah gaya tombol (Submit Button) */
    div.stButton > button:first-child {
        background-color: #38bdf8;
        color: #0f172a;
        font-weight: bold;
        border-radius: 20px;
        width: 100%;
        border: none;
    }
    
    /* Hover effect untuk tombol */
    div.stButton > button:first-child:hover {
        background-color: #0ea5e9;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Judul Aplikasi & Konfigurasi
st.set_page_config(page_title="Admin Inventaris Abhijati", page_icon="🏢", layout="wide")
st.title("A.I.S (Abhijati Inventory System) Input Data")
st.write("Silakan input aset.")

file_json = 'data_inven_mesin.json'

# Fungsi untuk membaca data lama
def load_data():
    if os.path.exists(file_json):
        try:
            with open(file_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# Fungsi untuk menyimpan data baru
def save_data(new_entry):
    data = load_data()
    data.append(new_entry)
    with open(file_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# --- BAGIAN FORM INPUT ---
with st.form("form_aset", clear_on_submit=True):
    st.subheader("📝 Tambah Aset Baru")
    
    # Baris 1: Kategori & Nomor
    col_kat, col_no = st.columns([3, 1])
    with col_kat:
        kategori = st.selectbox("Kategori Aset", [
            "Mesin Produksi", 
            "Elektronik (Laptop, AC, dll)", 
            "Kendaraan", 
            "Tanah & Bangunan",
            "Furniture & Kantor"
        ])
    with col_no:
        no = st.number_input("Nomor Urut (ID)", min_value=1, step=1)

    st.divider()

    # Baris 2: Detail Barang
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama Barang/Mesin", placeholder="Contoh: Honda Vario atau Compressor")
        kode = st.text_input("Kode Aset (Sesuai SOP)", placeholder="Contoh: ASD/MSN/...")
        jumlah = st.text_input("Jumlah/Satuan", value="1 Unit")
    
    with col2:
        # Gabungan Bulan & Tahun agar lebih rapi
        c_bln, c_thn = st.columns(2)
        with c_bln:
            bulan = st.selectbox("Bulan Beli", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        with c_thn:
            tahun = st.text_input("Tahun Beli", value="2024")
            
        lokasi = st.text_input("Lokasi Penempatan", value="ABHIJATI_PRODUKSI")
        keterangan = st.selectbox("Kondisi Saat Ini", ["Berfungsi", "Rusak", "Dalam Perbaikan", "Dijual/Sewa"])

    # Tombol Simpan
    submit = st.form_submit_button("💾 SIMPAN KE DATABASE")

    if submit:
        if not nama or not kode:
            st.error("Waduh! Nama Barang dan Kode Aset jangan dikosongin ya.")
        else:
            entry_baru = {
                "no": int(no),
                "kategori": kategori,
                "kode_barang": kode,
                "nama_barang": nama,
                "jumlah_item": jumlah,
                "bulan_pembelian": bulan,
                "tahun_pembelian": tahun,
                "lokasi": lokasi,
                "keterangan": keterangan
            }
            save_data(entry_baru)
            st.success(f"Mantap! {nama} ({kategori}) berhasil masuk list.")

# --- BAGIAN MONITORING DATA ---
st.divider()
st.subheader("📋 Daftar Seluruh Aset Terdaftar")

data_sekarang = load_data()

if data_sekarang:
    import pandas as pd
    df_tampil = pd.DataFrame(data_sekarang)
    
    # CEK: Jika kolom 'kategori' belum ada di data lama, buat kolomnya dengan isi "Mesin Produksi"
    if 'kategori' not in df_tampil.columns:
        df_tampil['kategori'] = "Mesin Produksi"
    
    # Ngatasi data yang kategori-nya kosong (NaN) agar tidak error saat difilter
    df_tampil['kategori'] = df_tampil['kategori'].fillna("Mesin Produksi")
    
    # Filter sekarang jadi aman
    opsi_kategori = df_tampil['kategori'].unique()
    filter_kat = st.multiselect("Filter Tampilan Berdasarkan Kategori:", options=opsi_kategori, default=opsi_kategori)
    
    df_filtered = df_tampil[df_tampil['kategori'].isin(filter_kat)]
    
    st.dataframe(df_filtered, use_container_width=True)
    st.write(f"Total Aset: {len(df_filtered)} item")
else:
    st.info("Database kosong. Ayo input aset pertamamu!")