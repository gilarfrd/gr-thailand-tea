import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURASI HALAMAN & DATABASE ---
st.set_page_config(page_title="GR THAILAND TEA", page_icon="🥤", layout="centered")
DB_FILE = "database_kasir.xlsx"
QRIS_IMAGE = "qris_toko.png"  # Taruh foto QRIS dari aplikasi Jago kamu di folder Dokumen dengan nama ini

# DATA KREDENSIAL KASIR (Silakan sesuaikan nomor HP & PIN kasir di sini)
AKUN_KASIR = {
    "083811931884": "300904",  # Contoh: Nomor HP dan PIN Kasir 1
    "081234567890": "123456"   # Contoh: Nomor HP dan PIN Kasir 2
}

if 'keranjang' not in st.session_state:
    st.session_state.keranjang = []
if 'kasir_logged_in' not in st.session_state:
    st.session_state.kasir_logged_in = False
if 'kasir_aktif' not in st.session_state:
    st.session_state.kasir_aktif = ""

# --- FUNGSI LOGIKA LEVEL MEMBERSHIP ---
def tentukan_level_dan_benefit(total_poin):
    if total_poin >= 100:
        return "Level 5: Diamond Overlord 💎", "Bisa Tukar 1 Minuman Gratis! 🎉"
    elif total_poin >= 75:
        return "Level 4: Platinum Elite 🪙", "Diskon 10% + Upgrade Size Gratis"
    elif total_poin >= 50:
        return "Level 3: Gold Vanguard 🟡", "Diskon 5% Semua Menu"
    elif total_poin >= 20:
        return "Level 2: Silver Challenger ⚪", "Voucher Potongan Rp2.000"
    else:
        return "Level 1: Bronze Initiate 🟤", "Member Baru (Beli terus untuk kejar 100 poin!)"

# ==========================================
# GATES/PEMBATAS UTAMA (ISOLASI TOTAL Halaman Kasir vs Member)
# ==========================================
st.sidebar.title("🛡️ Sistem Akses Portal")
pilihan_portal = st.sidebar.radio("Silakan Pilih Portal Anda:", ["📱 Portal Member / Pelanggan", "🏪 Portal internal Kasir"])

# ------------------------------------------
# PORTAL 1: MEMBER / PELANGGAN
# ------------------------------------------
if pilihan_portal == "📱 Portal Member / Pelanggan":
    # Jika kasir iseng buka portal member, paksa logout status kasirnya demi keamanan
    st.session_state.kasir_logged_in = False
    st.session_state.kasir_aktif = ""
    
    st.title("💳 GR THAILAND TEA")
    st.subheader("Digital Member Card & Poin Reward")
    st.write("Silakan masukkan nomor WhatsApp Anda untuk mengecek status poin.")

    cari_hp = st.text_input("Masukkan Nomor WhatsApp Kamu:", placeholder="Contoh: 083811931884")

    if cari_hp:
        if os.path.exists(DB_FILE):
            df_db = pd.read_excel(DB_FILE)
            data_member = df_db[df_db["Nomor_HP"] == cari_hp]
            
            if not data_member.empty:
                total_poin = int(data_member["Poin_Didapat"].sum())
                level_sekarang, benefit = tentukan_level_dan_benefit(total_poin)
                
                poin_untuk_klaim = total_poin % 100
                jumlah_reward_bisa_klaim = total_poin // 100
                sisa_ke_100 = 100 - poin_untuk_klaim
                
                # --- TAMPILAN KARTU MEMBER DIGITAL ---
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #111111, #2c3e50); padding: 25px; border-radius: 15px; color: white; box-shadow: 0px 4px 15px rgba(0,0,0,0.6); margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #f39c12; font-family: Arial;">GR THAILAND TEA MEMBER</h3>
                    <p style="font-size: 11px; opacity: 0.7; letter-spacing: 1px;">PREMIUM LOYALTY CARD</p>
                    <hr style="border-color: rgba(255,255,255,0.1); margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #bdc3c7;">ID MEMBER (WA)</p>
                            <b style="font-size: 18px; letter-spacing: 1px;">{cari_hp}</b>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 12px; color: #bdc3c7;">TOTAL POIN</p>
                            <b style="font-size: 24px; color: #f1c40f;">{total_poin:,} PTS</b>
                        </div>
                    </div>
                    <div style="margin-top: 15px; display: flex; justify-content: space-between;">
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #bdc3c7;">TINGKATAN LEVEL</p>
                            <b style="font-size: 15px; color: #2ecc71;">{level_sekarang}</b>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 12px; color: #e74c3c;">REWARD GRATIS</p>
                            <b style="font-size: 16px; color: #ffffff; background: #e74c3c; padding: 2px 8px; border-radius: 5px;">{jumlah_reward_bisa_klaim} Cup 🥤</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if jumlah_reward_bisa_klaim > 0:
                    st.success(f"🎉 Tunjukkan kartu ini ke kasir untuk mengklaim **{jumlah_reward_bisa_klaim} Cup Minuman Gratis** kamu!")
                
                st.progress(poin_untuk_klaim / 100)
                st.info(f"💡 Kumpulkan **{sisa_ke_100} poin lagi** untuk mendapatkan 1 minuman gratis berikutnya! (Status saat ini: {poin_untuk_klaim}/100 poin).")
                
                with st.expander("🕒 Lihat Riwayat Pembelian Anda"):
                    st.dataframe(df_db[df_db["Nomor_HP"] == cari_hp][["Waktu", "Menu", "Jumlah", "Total"]], use_container_width=True)
            else:
                st.warning("Nomor WhatsApp belum terdaftar. Lakukan transaksi di outlet untuk otomatis menjadi member!")
        else:
            st.error("Sistem sedang pemeliharaan (Database belum terbentuk).")

# ------------------------------------------
# PORTAL 2: KHUSUS KASIR / TOKO (SECURE LOGIN)
# ------------------------------------------
elif pilihan_portal == "🏪 Portal internal Kasir":
    if not st.session_state.kasir_logged_in:
        st.title("🔒 Login Otentikasi Staf Kasir")
        st.write("Silakan masukkan nomor telepon terdaftar dan kode PIN Anda untuk masuk ke sistem POS.")
        
        input_telp = st.text_input("Nomor Telepon Kasir:", placeholder="Contoh: 083811931884")
        input_pin = st.text_input("Masukkan Kode PIN Akses:", type="password", placeholder="******")
        
        if st.button("🔑 Masuk ke Sistem Kasir", use_container_width=True):
            if input_telp in AKUN_KASIR and AKUN_KASIR[input_telp] == input_pin:
                st.session_state.kasir_logged_in = True
                st.session_state.kasir_aktif = input_telp
                st.success(f"Selamat bekerja! Login berhasil sebagai Kasir ID: {input_telp}")
                st.rerun()
            else:
                st.error("🚨 Nomor Telepon atau Kode PIN salah! Akses ditolak.")
                
    else:
        # TAMPILAN JIKA KASIR SUDAH BERHASIL LOGIN LOGGED_IN == TRUE
        st.sidebar.write("---")
        st.sidebar.write(f"Kasir Aktif: **{st.session_state.kasir_aktif}**")
        if st.sidebar.button("🚪 Log Out (Keluar)", type="secondary"):
            st.session_state.kasir_logged_in = False
            st.session_state.kasir_aktif = ""
            st.rerun()
            
        st.title("🛒 MENU KASIR GR THAILAND TEA")
        
        no_hp = st.text_input("Nomor WhatsApp Pelanggan (Kosongkan jika bukan member):", placeholder="Contoh: 083811931884")

        DAFTAR_MENU = {
            "Thai Tea": 5000,
            "Thai Tea Delfi": 8000,
            "Green Tea": 5000,
            "Green Tea Delfi": 8000,
            "Coffee": 5000,
            "Coffee Delfi": 8000,
            "Cokelat Delfi": 8000,
            "Americano": 5000
        }

        st.write("---")
        col_menu, col_jumlah = st.columns([3, 1])
        with col_menu:
            pilihan_menu = st.selectbox("Pilih Jenis Minuman:", list(DAFTAR_MENU.keys()))
        with col_jumlah:
            jumlah_beli = st.number_input("Jumlah (Cup):", min_value=1, value=1, step=1)
            
        harga_satuan = DAFTAR_MENU[pilihan_menu]
        total_harga = harga_satuan * jumlah_beli

        if st.button("🛒 Masukkan ke Keranjang", use_container_width=True):
            poin_item = int(jumlah_beli)
            item_baru = {
                "Nomor_HP": no_hp if no_hp else "Tanpa Member",
                "Menu": pilihan_menu,
                "Harga_Satuan": harga_satuan,
                "Jumlah": jumlah_beli,
                "Total": total_harga,
                "Poin_Didapat": poin_item
            }
            st.session_state.keranjang.append(item_baru)
            st.toast(f"Berhasil menambah: {pilihan_menu}")

        if st.session_state.keranjang:
            st.write("---")
            st.write("### 🛍️ Daftar Belanjaan Saat Ini")
            df_keranjang = pd.DataFrame(st.session_state.keranjang)
            st.dataframe(df_keranjang[["Menu", "Harga_Satuan", "Jumlah", "Total", "Poin_Didapat"]], use_container_width=True)
            
            grand_total = df_keranjang["Total"].sum()
            total_poin_transaksi = df_keranjang["Poin_Didapat"].sum()
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="GRAND TOTAL", value=f"Rp {grand_total:,}")
            with c2:
                st.metric(label="TOTAL BONUS POIN", value=f"+{total_poin_transaksi:,} PTS")
            
            # --- FITUR METODE PEMBAYARAN BARU (QRIS & BANK JAGO) ---
            st.write("---")
            st.write("### 💳 Metode Pembayaran")
            metode_bayar = st.radio("Pilih Metode:", ["💵 Tunai (Cash)", "📱 QRIS", "🏦 Transfer Bank Jago"])
            
            if metode_bayar == "📱 QRIS":
                st.info(f"Silakan arahkan pelanggan untuk men-scan QRIS di bawah ini sebesar **Rp {grand_total:,}**")
                if os.path.exists(QRIS_IMAGE):
                    st.image(QRIS_IMAGE, caption="QRIS GR THAILAND TEA", width=300)
                else:
                    st.warning("⚠️ File 'qris_toko.png' tidak ditemukan di folder Dokumen. Silakan letakkan file QRIS Jago kamu di sana.")
            
            elif metode_bayar == "🏦 Transfer Bank Jago":
                st.success("ℹ️ **INFORMASI REKENING TUJUAN TRANSFER**")
                st.markdown(f"""
                * **Nama Bank:** Bank Jago
                * **Nomor Rekening:** `502145059811`
                * **Total Wajib Transfer:** **Rp {grand_total:,}**
                """)
                st.caption("Pastikan kasir memeriksa mutasi masuk di aplikasi Bank Jago sebelum menyelesaikan transaksi ini.")
            
            st.write("---")
            if st.button("❌ Kosongkan Keranjang", type="secondary"):
                st.session_state.keranjang = []
                st.rerun()
                
            if st.button("✅ SIMPAN TRANSAKSI & CETAK STRUK", type="primary", use_container_width=True):
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for item in st.session_state.keranjang:
                    item["Waktu"] = waktu
                    item["Nomor_HP"] = no_hp if no_hp else "Tanpa Member"
                    item["Metode_Bayar"] = metode_bayar
                    item["Staf_Kasir"] = st.session_state.kasir_aktif

                df_baru = pd.DataFrame(st.session_state.keranjang)
                if os.path.exists(DB_FILE):
                    df_lama = pd.read_excel(DB_FILE)
                    df_final = pd.concat([df_lama, df_baru], ignore_index=True)
                else:
                    df_final = df_baru
                    
                df_final.to_excel(DB_FILE, index=False)
                st.balloons()
                st.success("Transaksi Berhasil Disimpan!")
                st.session_state.keranjang = []
                st.rerun()

        if os.path.exists(DB_FILE):
            st.write("---")
            if st.checkbox("📊 Lihat Rekap Database Kasir & Omset"):
                df_db = pd.read_excel(DB_FILE)
                total_omset = df_db["Total"].sum()
                st.write(f"#### 💰 Total Pendapatan Masuk: **Rp {total_omset:,}**")
                st.dataframe(df_db, use_container_width=True)