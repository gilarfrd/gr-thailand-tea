import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="GR THAILAND TEA", 
    page_icon="🥤", 
    layout="centered"
)

# --- NAMA FILE DATABASE EXCEL ---
DB_FILE = "database_kasir.xlsx"

# Fungsi untuk membaca data dari Excel secara real-time
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_excel(DB_FILE, dtype={'Nomor_HP': str})
        except Exception:
            pass
    # Jika file tidak ditemukan atau bermasalah, buat struktur data baru
    return pd.DataFrame(columns=["Nomor_HP", "Nama_Member", "Total_Poin", "Terakhir_Transaksi"])

# Fungsi untuk menyimpan data kembali ke Excel
def save_data(df):
    df.to_excel(DB_FILE, index=False)

# Memuat database member di awal program
df_member = load_data()

# --- DATA PIN KASIR OUTLET ---
AKUN_KASIR = {
    "083811931884": "300904",  # Nomor HP & PIN Kasir Utama
}

# --- INISIALISASI SESSION STATE ---
if 'kasir_login' not in st.session_state:
    st.session_state.kasir_login = False

# --- TAMPILAN HEADER UTAMA ---
st.markdown("<h1 style='text-align: center; color: #7F5539;'>🧋 GR THAILAND TEA 🧋</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #B5828C;'>Sistem Poin Kasir & Portal Cek Poin Member Resmi</p>", unsafe_allow_html=True)
st.write("---")

# --- MENU NAVIGASI UTAMA ---
st.sidebar.title("🗂️ Menu Navigasi")
pilihan_portal = st.sidebar.radio(
    "Pilih Akses Portal:",
    ["📱 Portal Cek Poin Member", "🏪 Portal Internal Kasir"]
)

# ==============================================================================
# 📱 PORTAL CEK POIN MEMBER (Akses Pelanggan via HP)
# ==============================================================================
if pilihan_portal == "📱 Portal Cek Poin Member":
    st.subheader("📱 Portal Pelanggan")
    st.info("Silakan masukkan Nomor HP kamu yang terdaftar untuk memeriksa total poin saat ini.")
    
    hp_member_input = st.text_input("Masukkan Nomor HP Kamu:", placeholder="Contoh: 08123456xxx")
    
    if hp_member_input:
        hp_member_input = hp_member_input.strip()
        member_data = df_member[df_member['Nomor_HP'] == hp_member_input]
        
        if not member_data.empty:
            nama = member_data.iloc[0]['Nama_Member']
            poin = member_data.iloc[0]['Total_Poin']
            update_terakhir = member_data.iloc[0]['Terakhir_Transaksi']
            
            st.markdown(f"""
            <div style="background-color: #F1FAEE; padding: 20px; border-radius: 10px; border-left: 5px solid #457B9D;">
                <h3 style="color: #1D3557; margin: 0;">Halo, {nama}! 👋</h3>
                <p style="color: #457B9D; font-size: 18px; margin: 10px 0 5px 0;">Total Poin Kamu Saat Ini:</p>
                <h1 style="color: #E63946; margin: 0; font-size: 48px;">{int(poin)} Poin</h1>
                <p style="color: #6C757D; font-size: 12px; margin-top: 15px;">Terakhir transaksi: {update_terakhir}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if poin >= 10:
                st.balloons()
                st.success("🎉 Poin kamu sudah cukup untuk ditukarkan dengan 1 Cup Free Thai Tea! Sampaikan ke kasir saat memesan.")
            else:
                poin_kurang = 10 - poin
                st.warning(f"Kumpulkan {int(poin_kurang)} poin lagi untuk mendapatkan 1 Cup Free Thai Tea! ✨")
        else:
            st.error("Nomor HP tidak ditemukan. Pastikan nomor sudah benar atau daftarkan diri kamu ke kasir outlet GR THAILAND TEA.")

# ==============================================================================
# 🏪 PORTAL INTERNAL KASIR (Akses Staf Toko - Dikunci PIN)
# ==============================================================================
elif pilihan_portal == "🏪 Portal Internal Kasir":
    st.subheader("🏪 Portal Internal Kasir")
    
    if not st.session_state.kasir_login:
        st.warning("Akses dibatasi. Silakan masuk menggunakan kredensial kasir resmi.")
        input_hp_kasir = st.text_input("Masukkan Nomor HP Kasir:")
        input_pin_kasir = st.text_input("Masukkan 6 Digit PIN Kasir:", type="password", max_chars=6)
        
        if st.button("Masuk ke Sistem Kasir"):
            if input_hp_kasir in AKUN_KASIR and AKUN_KASIR[input_hp_kasir] == input_pin_kasir:
                st.session_state.kasir_login = True
                st.success("Log masuk berhasil!")
                st.rerun()
            else:
                st.error("Nomor HP Kasir atau PIN salah! Akses ditolak.")
                
    else:
        if st.sidebar.button("🚪 Keluar dari Sistem Kasir"):
            st.session_state.kasir_login = False
            st.rerun()
            
        st.success("🔓 Mode Kasir Aktif")
        aksi_kasir = st.tabs(["➕ Tambah / Kurang Poin", "📝 Registrasi Member Baru", "📊 Lihat Semua Data"])
        
        # --- TAB TAMBAH / KURANG POIN ---
        with aksi_kasir[0]:
            st.write("### Transaksi Poin Member")
            hp_transaksi = st.text_input("Cari Nomor HP Member:", key="hp_trans")
            
            if hp_transaksi:
                hp_transaksi = hp_transaksi.strip()
                member_idx = df_member[df_member['Nomor_HP'] == hp_transaksi].index
                
                if len(member_idx) > 0:
                    nama_m = df_member.loc[member_idx[0], 'Nama_Member']
                    poin_sekarang = df_member.loc[member_idx[0], 'Total_Poin']
                    
                    st.write(f"**Nama Member:** {nama_m}")
                    st.write(f"**Poin Saat Ini:** {int(poin_sekarang)} Poin")
                    
                    opsi_poin = st.radio("Pilih Tindakan:", ["Tambah Poin (Pembelian)", "Kurangi Poin (Klaim Hadiah)"])
                    jumlah_poin = st.number_input("Jumlah Poin:", min_value=1, value=1, step=1)
                    
                    if st.button("Proses Transaksi Poin"):
                        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        if opsi_poin == "Tambah Poin (Pembelian)":
                            df_member.loc[member_idx[0], 'Total_Poin'] += jumlah_poin
                            st.success(f"Berhasil menambahkan {jumlah_poin} poin!")
                        else:
                            if poin_sekarang >= jumlah_poin:
                                df_member.loc[member_idx[0], 'Total_Poin'] -= jumlah_poin
                                st.success(f"Berhasil memotong {jumlah_poin} poin!")
                            else:
                                st.error("Poin member tidak mencukupi!")
                                st.stop()
                                
                        df_member.loc[member_idx[0], 'Terakhir_Transaksi'] = waktu_sekarang
                        save_data(df_member)
                        st.rerun()
                else:
                    st.error("Member tidak ditemukan. Silakan registrasikan nomor baru terlebih dahulu.")
                    
        # --- TAB REGISTRASI MEMBER BARU ---
        with aksi_kasir[1]:
            st.write("### Pendaftaran Member Baru GR THAILAND TEA")
            hp_baru = st.text_input("Masukkan Nomor HP Member Baru:")
            nama_baru = st.text_input("Masukkan Nama Lengkap Member:")
            poin_awal = st.number_input("Poin Bonus Awal:", min_value=0, value=1, step=1)
            
            if st.button("Daftarkan Pelanggan"):
                if hp_baru and nama_baru:
                    hp_baru = hp_baru.strip()
                    if hp_baru in df_member['Nomor_HP'].values:
                        st.error("Nomor HP tersebut sudah terdaftar!")
                    else:
                        waktu_daftar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_row = pd.DataFrame({
                            "Nomor_HP": [hp_baru],
                            "Nama_Member": [nama_baru],
                            "Total_Poin": [poin_awal],
                            "Terakhir_Transaksi": [waktu_daftar]
                        })
                        df_member = pd.concat([df_member, new_row], ignore_index=True)
                        save_data(df_member)
                        st.success(f"Member '{nama_baru}' berhasil didaftarkan!")
                        st.rerun()
                else:
                    st.warning("Harap lengkapi Nomor HP dan Nama Member!")
                    
        # --- TAB LIHAT SEMUA DATA ---
        with aksi_kasir[2]:
            st.write("### Database Seluruh Member")
            if not df_member.empty:
                st.dataframe(df_member, use_container_width=True)
                st.caption(f"Total pelanggan terdaftar: {len(df_member)} orang.")
            else:
                st.info("Belum ada data member yang tersimpan.")
