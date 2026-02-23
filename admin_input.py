import streamlit as st
import pandas as pd
import qrcode
import requests
import base64
from io import BytesIO

# --- CONFIG ---
# Link Publish to Web (CSV)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR5brEySXNZAel-ZXXi9psodyPHSBCXUFzSaNHxOK2Ym35FmhWkfw4tQNWVs99gC41rHsx6lbdeKddz/pub?gid=0&single=true&output=csv"
# API Key ImgBB kamu
IMGBB_API_KEY = "a1e87954926748a99225b52ce641c807" 

st.set_page_config(page_title="ADMIN AIS", layout="centered")

# --- STYLE ---
st.markdown("""<style>
    .stApp { background-color: #0f172a; color: white; }
    div.stButton > button:first-child {
        background-color: #38bdf8 !important; color: black !important;
        font-weight: bold; width: 100%; border-radius: 10px;
    }
</style>""", unsafe_allow_html=True)

# --- LOGIKA ID ---
try:
    df_existing = pd.read_csv(CSV_URL)
    next_id = int(df_existing.iloc[:, 0].max() + 1) if not df_existing.empty else 1
except:
    next_id = 1

st.title("🏢 AIS ADMIN - INPUT")

with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        no = st.number_input("ID Unit", value=next_id)
        nama = st.text_input("Nama Barang")
    with col2:
        lokasi = st.text_input("Lokasi", value="ABHIJATI_PRODUKSI")
        kondisi = st.selectbox("Kondisi", ["Berfungsi", "Rusak", "Maintenance"])
    
    uploaded_file = st.file_uploader("Upload Foto", type=["jpg", "png", "jpeg"])
    submitted = st.form_submit_button("SIMPAN & GENERATE QR")

if submitted:
    if not nama:
        st.error("Nama harus diisi!")
    else:
        # Upload ke ImgBB
        url_foto = ""
        if uploaded_file:
            img_bytes = uploaded_file.read()
            res = requests.post("https://api.imgbb.com/1/upload", 
                                data={"key": IMGBB_API_KEY, "image": base64.b64encode(img_bytes)})
            if res.status_code == 200:
                url_foto = res.json()['data']['url']
        
        # Link QR (Target Vercel)
        link_target = f"https://abhijati-reaperbytees-projects.vercel.app/?id={no}"
        qr = qrcode.make(link_target)
        
        st.success(f"Data Siap! ID: {no}")
        st.info(f"Link Foto: {url_foto}")
        
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, caption="Scan untuk Cek di Vercel", width=200)
