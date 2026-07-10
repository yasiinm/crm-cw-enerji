import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# KONFIGURASI DATABASE SQLITE
# ==========================================
DB_NAME = "crm_cw_enerji.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prospek (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal_input TEXT,
            perusahaan TEXT,
            kawasan TEXT,
            kategori TEXT,
            nama_kontak TEXT,
            nomor_telepon TEXT,
            penanggung_jawab TEXT,
            status TEXT,
            nilai REAL,
            catatan TEXT
        )
    ''')
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM prospek", conn)
    conn.close()
    return df

def tambah_prospek(tanggal, perusahaan, kawasan, kategori, nama_kontak, nomor_telepon, penanggung_jawab, status, nilai, catatan):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO prospek (tanggal_input, perusahaan, kawasan, kategori, nama_kontak, nomor_telepon, penanggung_jawab, status, nilai, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tanggal, perusahaan, kawasan, kategori, nama_kontak, nomor_telepon, penanggung_jawab, status, nilai, catatan))
    conn.commit()
    conn.close()

def update_prospek(id_prospek, status_baru, catatan_baru):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE prospek 
        SET status = ?, catatan = ? 
        WHERE id = ?
    ''', (status_baru, catatan_baru, id_prospek))
    conn.commit()
    conn.close()

# Inisialisasi Database
init_db()

# ==========================================
# ANTARMUKA PENGGUNA (UI)
# ==========================================
st.set_page_config(page_title="CRM CW Enerji", page_icon="☀️", layout="wide")
st.title("☀️ Sistem Manajemen Prospek CW Enerji")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📝 Input Prospek", "📊 Database & Update", "📈 Analisis Funnel"])

# ==========================================
# TAB 1: FORMULIR INPUT DATA (Tetap Sama)
# ==========================================
with tab1:
    st.header("Tambah Prospek Baru")
    with st.form("form_tambah_prospek", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            perusahaan = st.text_input("Nama Perusahaan (Wajib)")
            kawasan = st.selectbox("Kawasan Industri", ["MM2100", "Jababeka", "KIIC Karawang", "Kawasan Industri Mitra (KIM)", "Lainnya"])
            kategori = st.selectbox("Kategori Klien", ["Manufaktur Komponen", "Kontraktor EPC", "Konsultan Elektrikal"])
            nama_kontak = st.text_input("Nama Kontak Person")
            nomor_telepon = st.text_input("Nomor Telepon (Contoh: 62815179...)")
        with col2:
            penanggung_jawab = st.selectbox("Penanggung Jawab (PIC Internal)", [
                "Yasin Mubarok (Direktur)", "Sales Executive B2B", "Technical Supervisor", "Admin & Logistik"
            ])
            status = st.selectbox("Status Negosiasi", ["Baru", "Follow-up 1", "Penawaran Terkirim", "Survei Lokasi", "Deal", "Lost"])
            nilai_input = st.text_input("Estimasi Nilai Proyek (Masukkan Angka Saja)", value="0")
            catatan = st.text_area("Catatan Tindakan / Langkah Selanjutnya")
        submitted = st.form_submit_button("💾 Simpan Data Prospek")

    nilai_clean = nilai_input.replace(".", "").replace(",", "")
    nilai_final = float(nilai_clean) if nilai_clean.isdigit() else 0
    if nilai_clean.isdigit():
        st.info(f"💡 **Cek Kembali Nilai Proyek:** Rp {nilai_final:,.0f}".replace(",", "."))

    if submitted:
        if perusahaan.strip() == "":
            st.error("Gagal! Nama Perusahaan wajib diisi.")
        else:
            tanggal_sekarang = datetime.now().strftime("%Y-%m-%d")
            tambah_prospek(tanggal_sekarang, perusahaan, kawasan, kategori, nama_kontak, nomor_telepon, penanggung_jawab, status, nilai_final, catatan)
            st.success(f"Berhasil! Data '{perusahaan}' telah tersimpan.")

# ==========================================
# TAB 2: DATABASE & UPDATE STATUS
# ==========================================
with tab2:
    st.header("Database Prospek & Update Status")
    df = load_data()
    
    if not df.empty:
        # Fitur Update Status Cepat
        with st.expander("🔄 Perbarui Status Prospek (Klik untuk membuka)"):
            form_update_col1, form_update_col2 = st.columns(2)
            
            with form_update_col1:
                # Membuat daftar pilihan format "ID - Nama Perusahaan"
                daftar_opsi = df.apply(lambda row: f"{row['id']} - {row['perusahaan']}", axis=1).tolist()
                pilihan_prospek = st.selectbox("Pilih Perusahaan yang akan diupdate:", daftar_opsi)
                id_terpilih = int(pilihan_prospek.split(" - ")[0])
                
                # Mengambil data lama
                status_lama = df.loc[df['id'] == id_terpilih, 'status'].values[0]
                catatan_lama = df.loc[df['id'] == id_terpilih, 'catatan'].values[0]
                
            with form_update_col2:
                # Menyiapkan list status untuk mencari index status lama
                list_status = ["Baru", "Follow-up 1", "Penawaran Terkirim", "Survei Lokasi", "Deal", "Lost"]
                idx_status = list_status.index(status_lama) if status_lama in list_status else 0
                
                status_baru = st.selectbox("Update Status Negosiasi Ke:", list_status, index=idx_status)
                catatan_baru = st.text_area("Update Catatan Terkini:", value=catatan_lama)
                
            if st.button("Simpan Pembaruan Status"):
                update_prospek(id_terpilih, status_baru, catatan_baru)
                st.success("Data berhasil diperbarui! Silakan refresh (tekan R) untuk melihat hasil di tabel.")
        
        st.markdown("---")
        
        # Pengolahan Data untuk Tabel
        df_tampil = df.copy()
        df_tampil['Nilai (Rp)'] = df_tampil['nilai'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        
        # Membuat Tautan WhatsApp Pintar
        def buat_link_wa(nomor):
            if pd.isna(nomor) or str(nomor).strip() == "":
                return ""
            nomor_bersih = str(nomor).replace("+", "").replace(" ", "").replace("-", "")
            if nomor_bersih.startswith("08"):
                nomor_bersih = "62" + nomor_bersih[1:]
            return f"https://wa.me/{nomor_bersih}"
            
        df_tampil['Hubungi_WA'] = df_tampil['nomor_telepon'].apply(buat_link_wa)
        
        # Merapikan urutan kolom tabel
        kolom_pilihan = ['id', 'tanggal_input', 'perusahaan', 'kawasan', 'kategori', 'nama_kontak', 'Hubungi_WA', 'penanggung_jawab', 'status', 'Nilai (Rp)', 'catatan']
        df_tampil = df_tampil[kolom_pilihan]
        
        # Menampilkan Tabel dengan Konfigurasi Tautan
        st.dataframe(
            df_tampil, 
            width="stretch", 
            hide_index=True,
            column_config={
                "Hubungi_WA": st.column_config.LinkColumn("Chat WhatsApp (Klik)")
            }
        )
        
    else:
        st.info("Database masih kosong.")

# ==========================================
# TAB 3: DASHBOARD & SALES FUNNEL
# ==========================================
with tab3:
    st.header("Analisis Konversi & Sales Funnel")
    df = load_data()
    
    if not df.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Prospek (Leads)", len(df))
        col_m2.metric("Total Pipeline", f"Rp {df['nilai'].sum():,.0f}".replace(",", "."))
        col_m3.metric("Proyek Deal", len(df[df['status'] == 'Deal']))
        
        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Beban Kerja PIC")
            pic_count = df['penanggung_jawab'].value_counts().reset_index()
            pic_count.columns = ['PIC', 'Jumlah Klien']
            fig_bar = px.bar(pic_count, x='PIC', y='Jumlah Klien', text_auto=True, color='PIC')
            st.plotly_chart(fig_bar, width="stretch")
            
        with col_chart2:
            st.subheader("Sales Funnel (Corong Penjualan)")
            # Mengurutkan status berdasarkan perjalanan negosiasi
            urutan_funnel = ["Baru", "Follow-up 1", "Penawaran Terkirim", "Survei Lokasi", "Deal"]
            
            hitung_funnel = df['status'].value_counts().to_dict()
            nilai_funnel = [hitung_funnel.get(status, 0) for status in urutan_funnel]
            
            fig_funnel = go.Figure(go.Funnel(
                y=urutan_funnel,
                x=nilai_funnel,
                textinfo="value+percent initial",
                marker={"color": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]}
            ))
            fig_funnel.update_layout(margin={"t": 30, "b": 10})
            st.plotly_chart(fig_funnel, width="stretch")
            
    else:
        st.info("Belum ada data untuk memuat grafik.")