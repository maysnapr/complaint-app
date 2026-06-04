import streamlit as st
import pandas as pd

from database import *
from auth import login
from nlp import detect_priority

create_table()

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Sistem Pengaduan Mahasiswa",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0d2137 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    /* Hapus selector universal '*' tadi dan ganti dengan ini agar tidak merusak background input */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .sidebar-logo .logo-sub {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #94a3b8 !important;
        font-size: 0.85rem;
    }

    /* === MODIFIKASI DROPDOWN/SELECTBOX KHUSUS SIDEBAR === */
    /* Mengubah background kotak selectbox di sidebar menjadi semi-transparan */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }

    /* Mengubah warna teks pilihan utama di dalam kotak */
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* Mengubah warna background list dropdown saat diklik/terbuka */
    div[data-baseweb="menu"] {
        background-color: #162a45 !important; /* Warna biru gelap menyesuaikan sidebar */
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Mengubah warna teks pilihan di dalam list dropdown */
    div[data-baseweb="menu"] li {
        color: #ffffff !important;
        background-color: transparent !important;
    }

    /* Efek ketika kursor diarahkan (hover) ke pilihan di dalam dropdown */
    div[data-baseweb="menu"] li:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* === HEADER HERO === */
    .hero-section {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
    }
    .hero-section h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .hero-section p {
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        font-size: 1rem;
    }

    /* === CARDS === */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0,0,0,0.05);
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a5f;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* === PRIORITY BADGES === */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-high {
        background: #fee2e2;
        color: #dc2626;
        border: 1px solid #fca5a5;
    }
    .badge-medium {
        background: #fef3c7;
        color: #d97706;
        border: 1px solid #fcd34d;
    }
    .badge-low {
        background: #d1fae5;
        color: #059669;
        border: 1px solid #6ee7b7;
    }

    /* === STATUS INDICATOR === */
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    /* === BUTTONS === */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4) !important;
    }

    /* === FORM INPUTS === */
    .stTextInput input, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #e2e8f0 !important;
    }

    /* === SUCCESS / WARNING / ERROR MESSAGES === */
    .stSuccess, .element-container .stAlert[data-baseweb="notification"][kind="positive"] {
        border-radius: 10px !important;
        border-left: 4px solid #059669 !important;
    }
    .stWarning {
        border-radius: 10px !important;
        border-left: 4px solid #d97706 !important;
    }
    .stError {
        border-radius: 10px !important;
        border-left: 4px solid #dc2626 !important;
    }

    /* === DATAFRAME === */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    }

    /* === DIVIDER === */
    hr {
        border: none !important;
        border-top: 2px solid #e2e8f0 !important;
        margin: 1.5rem 0 !important;
    }

    /* === STAT CARDS === */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 4px solid;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748b;
        margin: 0.25rem 0 0 0;
    }

    /* Sidebar logo area */
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0 1.5rem;
    }
    .sidebar-logo .logo-icon {
        font-size: 2.5rem;
    }
    .sidebar-logo .logo-text {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.4rem;
    }
    .sidebar-logo .logo-sub {
        font-size: 0.75rem;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🎓</div>
        <div class="logo-text">SiPengadu</div>
        <div class="logo-sub">Sistem Pengaduan Mahasiswa</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    menu = st.selectbox(
        "🔀 Pilih Menu",
        ["📝  Mahasiswa", "🔐  Admin"]
    )

    st.markdown("---")
    st.markdown("""
    <div style="padding: 0.5rem 0;">
        <p style="font-size:0.78rem; color:#64748b;">
            💡 Sampaikan pengaduan Anda dengan jelas dan lengkap agar dapat ditindaklanjuti dengan cepat.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ===== MAIN CONTENT =====

# ==================================================
# MAHASISWA
# ==================================================
if "Mahasiswa" in menu:

    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1>📢 Form Pengaduan Mahasiswa</h1>
        <p>Sampaikan keluhan atau masukan Anda, kami siap menindaklanjutinya</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown('<div class="card-header">📋 Detail Pengaduan</div>', unsafe_allow_html=True)

        kategori = st.selectbox(
            "Kategori Pengaduan",
            ["Akademik", "Fasilitas", "IT/Sistem SPADA", "Administrasi", "Lainnya"],
            help="Pilih kategori yang sesuai dengan pengaduan Anda"
        )

        pengaduan = st.text_area(
            "Isi Pengaduan",
            placeholder="Tuliskan pengaduan Anda secara detail di sini...",
            height=180,
            help="Semakin detail pengaduan, semakin cepat dapat kami tindak lanjuti"
        )

        col_btn, col_info = st.columns([1, 1])
        with col_btn:
            kirim = st.button("📨  Kirim Pengaduan", use_container_width=True)

        if kirim:
            if pengaduan.strip() == "":
                st.warning("⚠️  Isi pengaduan tidak boleh kosong!")
            else:
                priority = detect_priority(pengaduan)
                add_complaint(kategori, pengaduan, priority)
                st.success(f"✅  Pengaduan berhasil terkirim!  Prioritas: **{priority}**")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">📌 Panduan Pengaduan</div>
            <div style="color:#475569; font-size:0.9rem; line-height:1.8;">
                <p>🔹 <b>Akademik</b><br>Nilai, KRS, jadwal kuliah, dosen</p>
                <p>🔹 <b>Fasilitas</b><br>Gedung, laboratorium, ruang kelas</p>
                <p>🔹 <b>IT/Sistem SPADA</b><br>E-learning, akun mahasiswa</p>
                <p>🔹 <b>Administrasi</b><br>Surat, legalisir, administrasi kampus</p>
                <p>🔹 <b>Lainnya</b><br>Hal-hal di luar kategori di atas</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="background: linear-gradient(135deg, #eff6ff, #dbeafe); border: 1px solid #bfdbfe;">
            <div class="card-header" style="color:#1d4ed8; border-bottom-color:#bfdbfe;">ℹ️ Informasi</div>
            <div style="color:#1e40af; font-size:0.85rem; line-height:1.7;">
                <p>📊 Pengaduan diproses berdasarkan <b>tingkat prioritas</b> yang terdeteksi secara otomatis.</p>
                <p>⏱️ Estimasi respons <b>1–3 hari kerja</b>.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# ADMIN
# ==================================================
elif "Admin" in menu:

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:

        # Login page
        st.markdown("""
        <div class="hero-section">
            <h1>🔐 Login Admin</h1>
            <p>Masuk untuk mengelola pengaduan mahasiswa</p>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_center, col_r = st.columns([1, 2, 1])
        with col_center:
            st.markdown('<div class="card-header">🔑 Masuk ke Dashboard</div>', unsafe_allow_html=True)

            username = st.text_input("👤  Username", placeholder="Masukkan username")
            password = st.text_input("🔒  Password", type="password", placeholder="Masukkan password")

            if st.button("Masuk", use_container_width=True):
                if login(username, password):
                    st.session_state.logged_in = True
                    st.success("✅  Login berhasil! Mengalihkan...")
                    st.rerun()
                else:
                    st.error("❌  Username atau password salah!")
            st.markdown('</div>', unsafe_allow_html=True)

    else:

        # Dashboard header
        st.markdown("""
        <div class="hero-section">
            <h1>📊 Dashboard Admin</h1>
            <p>Kelola dan pantau seluruh pengaduan mahasiswa</p>
        </div>
        """, unsafe_allow_html=True)

        data = get_all_complaints()

        if len(data) == 0:
            st.markdown("""
            <div class="card" style="text-align:center; padding:3rem;">
                <div style="font-size:3rem;">📭</div>
                <div style="font-size:1.2rem; font-weight:600; color:#1e3a5f; margin-top:1rem;">Belum Ada Pengaduan</div>
                <div style="color:#64748b; margin-top:0.5rem;">Pengaduan mahasiswa akan muncul di sini</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df = pd.DataFrame(
                data,
                columns=["ID", "Kategori", "Pengaduan", "Prioritas", "Status"]
            )

            # === Stats ===
            total = len(df)
            tinggi = len(df[df["Prioritas"] == "Tinggi"]) if "Tinggi" in df["Prioritas"].values else 0
            sedang = len(df[df["Prioritas"] == "Sedang"]) if "Sedang" in df["Prioritas"].values else 0
            selesai = len(df[df["Status"] == "Selesai"]) if "Selesai" in df["Status"].values else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="stat-card" style="border-color:#2563eb;">
                    <div class="stat-number" style="color:#2563eb;">{total}</div>
                    <div class="stat-label">Total Pengaduan</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="stat-card" style="border-color:#dc2626;">
                    <div class="stat-number" style="color:#dc2626;">{tinggi}</div>
                    <div class="stat-label">Prioritas Tinggi</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="stat-card" style="border-color:#d97706;">
                    <div class="stat-number" style="color:#d97706;">{sedang}</div>
                    <div class="stat-label">Prioritas Sedang</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="stat-card" style="border-color:#059669;">
                    <div class="stat-number" style="color:#059669;">{selesai}</div>
                    <div class="stat-label">Selesai</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # === Table ===
            st.markdown('<div class="card-header">📋 Daftar Pengaduan</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, height=300)
            st.markdown('</div>', unsafe_allow_html=True)

            # === Update status ===
            st.markdown('<div class="card-header">✏️ Update Status Pengaduan</div>', unsafe_allow_html=True)

            col_upd1, col_upd2, col_upd3 = st.columns([1, 1, 1])
            with col_upd1:
                ids = df["ID"].tolist()
                selected_id = st.selectbox("🔢  Pilih ID Pengaduan", ids)
            with col_upd2:
                new_status = st.selectbox(
                    "📌  Status Baru",
                    ["Diterima", "Diproses", "Selesai"]
                )
            with col_upd3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾  Simpan Perubahan", use_container_width=True):
                    update_status(selected_id, new_status)
                    st.success(f"✅  Status pengaduan #{selected_id} berhasil diperbarui menjadi **{new_status}**")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Logout
        col_lo1, col_lo2, col_lo3 = st.columns([2, 1, 2])
        with col_lo2:
            if st.button("🚪  Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
