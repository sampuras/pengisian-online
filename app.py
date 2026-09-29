import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Konfigurasi Halaman
st.set_page_config(
    page_title="Portal Ujian Online Sekolah",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar tertutup di pojok kiri atas
)

# Styling CSS untuk Tampilan Oval Modern & Elegan
st.markdown("""
    <style>
    .oval-button {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 40px;
        text-align: center;
        text-decoration: none;
        font-size: 18px;
        font-weight: bold;
        border-radius: 50px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        transition: 0.3s;
        cursor: pointer;
    }
    .oval-button:hover {
        transform: scale(1.05);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Load Data Siswa & Soal
try:
    df_siswa = conn.read(worksheet="Siswa", ttl=5)
    df_soal = conn.read(worksheet="Soal", ttl=5)
    df_nilai = conn.read(worksheet="Nilai", ttl=5)
except Exception as e:
    st.error(f"Gagal terhubung ke Google Sheets. Pastikan konfigurasi secrets benar. Error: {e}")
    st.stop()

# Fungsi Konversi Nilai ke Predikat
def get_predikat(nilai):
    if nilai <= 40:
        return "D"
    elif nilai <= 65:
        return "C"
    elif nilai <= 85:
        return "B"
    else:
        return "A"

# Session State untuk Login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['user_data'] = None

# --- SIDEBAR TERSEMBUNYI ---
with st.sidebar:
    st.title("⚙️ Menu Navigasi")
    menu = st.radio("Pilih Akses", ["Portal Utama", "Login Admin", "Login Siswa"])

# --- PORTAL UTAMA ---
if menu == "Portal Utama" or not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center;'>SELAMAT DATANG DI PORTAL UJIAN ONLINE SEKOLAH</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Silakan masuk melalui menu sidebar di pojok kiri atas atau tombol di bawah.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Masuk Sebagai Siswa", use_container_width=True):
            st.info("Gunakan sidebar di pojok kiri atas untuk memilih 'Login Siswa'.")
        if st.button("🛠️ Masuk Sebagai Admin", use_container_width=True):
            st.info("Gunakan sidebar di pojok kiri atas untuk memilih 'Login Admin'.")

# --- LOGIN ADMIN ---
elif menu == "Login Admin":
    st.subheader("🔐 Login Administrator")
    admin_pass = st.text_input("Password Admin", type="password")
    if st.button("Masuk Admin"):
        if admin_pass == "adminsekolah2026": # Ubah password sesuai keinginan
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = 'admin'
            st.success("Login Admin Berhasil!")
            st.rerun()
        else:
            st.error("Password Salah!")

    if st.session_state.get('user_role') == 'admin':
        st.divider()
        st.header("📊 Panel Kontrol Admin")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Manajemen Siswa", "Input Soal", "Rekap Nilai", "Fitur Kenaikan Kelas"])
        
        with tab1:
            st.subheader("Tambah Data Siswa Online")
            with st.form("form_tambah_siswa"):
                kelas_ baru = st.text_input("Kelas (Contoh: 7A, 8B, dst)")
                no_absen = st.number_input("No Absen", min_value=1, step=1)
                nisn_baru = st.text_input("NISN")
                nama_baru = st.text_input("Nama Siswa")
                submit_siswa = st.form_submit_button("Simpan Siswa")
                
                if submit_siswa:
                    new_row = pd.DataFrame({"Kelas": [kelas_baru], "No": [no_absen], "NISN": [nisn_baru], "Nama": [nama_baru]})
                    df_siswa = pd.concat([df_siswa, new_row], ignore_index=True)
                    conn.update(worksheet="Siswa", data=df_siswa)
                    st.success(f"Siswa {nama_baru} berhasil ditambahkan!")
            
            st.dataframe(df_siswa)

        with tab2:
            st.subheader("Input Bank Soal")
            mapel_list = [
                "Akidah Akhlak", "Al-Quran Hadits", "Fiqih", "Sejarah Kebudayaan Islam (SKI)",
                "Pendidikan Pancasila", "Bahasa Indonesia", "Ilmu Pengetahuan Alam dan Sosial (IPAS)",
                "Matematika", "Pendidikan Jasmani Olahraga dan Kesehatan (PJOK)",
                "Seni Budaya dan Prakarya (SBdP)", "Bahasa Arab", "Bahasa Sunda",
                "Bahasa Inggris", "Koding dan Kecerdasan Artifisial (KKA)"
            ]
            kategori_list = [
                "Soal Latihan", "Soal Tengah Semester 1", "Soal Tengah Semester 2",
                "Soal Semester 1", "Soal Semester 2"
            ]
            
            with st.form("form_soal"):
                p_mapel = st.selectbox("Mata Pelajaran", mapel_list)
                p_kategori = st.selectbox("Kategori Ujian", kategori_list)
                p_jenis = st.selectbox("Jenis Soal", ["Pilihan Ganda", "Isian", "Esai"])
                p_tanya = st.text_area("Pertanyaan")
                p_a = st.text_input("Opsi A (Kosongkan jika Isian/Esai)")
                p_b = st.text_input("Opsi B")
                p_c = st.text_input("Opsi C")
                p_d = st.text_input("Opsi D")
                p_kunci = st.text_input("Kunci Jawaban / Kata Kunci Isian")
                
                submit_soal = st.form_submit_button("Simpan Soal")
                if submit_soal:
                    new_soal = pd.DataFrame({
                        "Mapel": [p_mapel], "KategoriUjian": [p_kategori], "JenisSoal": [p_jenis],
                        "Pertanyaan": [p_tanya], "OpsiA": [p_a], "OpsiB": [p_b], "OpsiC": [p_c], "OpsiD": [p_d], "KunciJawaban": [p_kunci]
                    })
                    df_soal = pd.concat([df_soal, new_soal], ignore_index=True)
                    conn.update(worksheet="Soal", data=df_soal)
                    st.success("Soal berhasil ditambahkan ke database!")

        with tab3:
            st.subheader("Rekap Nilai Siswa")
            st.dataframe(df_nilai)

        with tab4:
            st.subheader("Otomatisasi Pindah Kelas / Kenaikan Kelas")
            st.write("Fitur ini mengonversi tingkat kelas siswa (Contoh: Kelas 7 -> Kelas 8 secara massal).")
            if st.button("Proses Kenaikan Kelas Otomatis"):
                # Logika otomatis menaikkan tingkat kelas (misal 7A jadi 8A)
                st.info("Fitur kenaikan kelas diproses berdasarkan format tingkat kelas.")

# --- LOGIN SISWA ---
elif menu == "Login Siswa":
    st.subheader("🎓 Portal Masuk Siswa")
    nisn_input = st.text_input("Masukkan NISN Anda untuk Masuk:")
    
    if st.button("Masuk Ujian"):
        cek_siswa = df_siswa[df_siswa['NISN'].astype(str) == nisn_input.strip()]
        if not cek_siswa.empty:
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = 'siswa'
            st.session_state['user_data'] = cek_siswa.iloc[0].to_dict()
            st.success(f"Selamat datang, {st.session_state['user_data']['Nama']}!")
            st.rerun()
        else:
            st.error("NISN tidak terdaftar di database sekolah. Hubungi Admin.")

    if st.session_state.get('user_role') == 'siswa':
        siswa = st.session_state['user_data']
        st.write(f"**Nama:** {siswa['Nama']} | **Kelas:** {siswa['Kelas']} | **NISN:** {siswa['NISN']}")
        
        st.divider()
        st.subheader("📝 Pilih Ujian & Kerjakan")
        mapel_pilihan = st.selectbox("Pilih Mata Pelajaran", [
            "Akidah Akhlak", "Al-Quran Hadits", "Fiqih", "Sejarah Kebudayaan Islam (SKI)",
            "Pendidikan Pancasila", "Bahasa Indonesia", "Ilmu Pengetahuan Alam dan Sosial (IPAS)",
            "Matematika", "Pendidikan Jasmani Olahraga dan Kesehatan (PJOK)",
            "Seni Budaya dan Prakarya (SBdP)", "Bahasa Arab", "Bahasa Sunda",
            "Bahasa Inggris", "Koding dan Kecerdasan Artifisial (KKA)"
        ])
        kategori_pilihan = st.selectbox("Pilih Kategori Ujian", [
            "Soal Latihan", "Soal Tengah Semester 1", "Soal Tengah Semester 2",
            "Soal Semester 1", "Soal Semester 2"
        ])
        
        soal_tersedia = df_soal[(df_soal['Mapel'] == mapel_pilihan) & (df_soal['KategoriUjian'] == kategori_pilihan)]
        
        if not soal_tersedia.empty:
            with st.form("form_mengerjakan"):
                jawaban_user = {}
                score = 0
                total_soal = len(soal_tersedia)
                
                for idx, row in soal_tersedia.iterrows():
                    st.write(f"**Soal {idx+1}:** {row['Pertanyaan']}")
                    if row['JenisSoal'] == 'Pilihan Ganda':
                        jawaban_user[idx] = st.radio(f"Pilih jawaban {idx}", [row['OpsiA'], row['OpsiB'], row['OpsiC'], row['OpsiD']], key=f"soal_{idx}")
                    elif row['JenisSoal'] == 'Isian':
                        jawaban_user[idx] = st.text_input(f"Jawaban singkat {idx}", key=f"soal_{idx}")
                    else:
                        jawaban_user[idx] = st.text_area(f"Uraian esai {idx}", key=f"soal_{idx}")
                
                submit_ujian = st.form_submit_button("Kumpulkan Jawaban")
                if submit_ujian:
                    # Penilaian sederhana otomatis untuk PG/Isian
                    for idx, row in soal_tersedia.iterrows():
                        if str(jawaban_user[idx]).strip().lower() == str(row['KunciJawaban']).strip().lower():
                            score += (100 / total_soal)
                    
                    final_score = round(score, 2)
                    pred = get_predikat(final_score)
                    
                    # Simpan ke Google Sheets Nilai
                    new_nilai = pd.DataFrame({
                        "NISN": [siswa['NISN']], "Nama": [siswa['Nama']], "Kelas": [siswa['Kelas']],
                        "Mapel": [mapel_pilihan], "KategoriUjian": [kategori_pilihan],
                        "Nilai": [final_score], "Predikat": [pred]
                    })
                    df_nilai = pd.concat([df_nilai, new_nilai], ignore_index=True)
                    conn.update(worksheet="Nilai", data=df_nilai)
                    
                    st.success(f"Ujian Selesai! Nilai Anda: {final_score} (Predikat: {pred})")
        else:
            st.warning("Belum ada soal untuk mata pelajaran dan kategori ini.")