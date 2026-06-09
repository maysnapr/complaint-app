import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
from pyngrok import ngrok as pyngrok_ngrok, conf as pyngrok_conf

from database import *
from auth import login
from nlp import detect_priority

create_table()

# ===================================================
# CONFIG TOKEN NGROK
# ===================================================
MY_NGROK_TOKEN = "3EsvaK3vL2JBVLOZiVZYyWbiLcH_2pypYGyJ2uKPsGbduZiZo"

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Sistem Pengaduan Mahasiswa",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================
# FUNGSI NGROK AMAN (MENGGUNAKAN CACHE AGAR TIDAK LOOP)
# ===================================================
@st.cache_resource
def start_ngrok_tunnel(token):
    if token and token != "TULIS_TOKEN_NGROK_MU_DI_SINI":
        try:
            # Bersihkan sisa tunnel lama yang menggantung
            pyngrok_ngrok.kill()
            
            # Set token konfigurasi
            pyngrok_conf.get_default().auth_token = token
            
            # Hubungkan port 8501 dengan opsi secure HTTPS (bind_tls=True)
            tunnel = pyngrok_ngrok.connect(8501, proto="http", bind_tls=True)
            return tunnel.public_url
        except Exception as e:
            return f"ERROR: {e}"
    return None

# Panggil fungsi terowongan otomatis
if "ngrok_url" not in st.session_state:
    st.session_state.ngrok_url = start_ngrok_tunnel(MY_NGROK_TOKEN)

# ===== CUSTOM CSS (AESTHETIC TEAL & SLATE PALETTE) =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Reset & Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* === SIDEBAR DESIGN (Modern Teal Charcoal) === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #115e59 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] p {
        color: #ccfbf1 !important;
        font-size: 0.85rem;
        opacity: 0.8;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] input {
        background-color: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    /* === HERO SECTION (Soft Teal Gradient) === */
    .hero-section {
        background: linear-gradient(135deg, #115e59 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(17, 94, 89, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .hero-section h1 { font-size: 2.25rem; font-weight: 700; margin: 0; letter-spacing: -0.03em; color: #ffffff !important;}
    .hero-section p { margin-top: 0.5rem; opacity: 0.9; font-size: 1.05rem; font-weight: 300; color: #ccfbf1 !important; }

    /* === CARDS & CONTAINERS === */
    .custom-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-left: 4px solid #14b8a6;
        padding-left: 10px;
    }

    /* === STAT CARDS === */
    .stat-card { 
        background: white; 
        border-radius: 14px; 
        padding: 1.25rem; 
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); 
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
    }
    .stat-card:hover { transform: translateY(-2px); box-shadow: 0 12px 20px -3px rgba(0,0,0,0.05); }
    .stat-number { font-size: 2rem; font-weight: 700; margin: 0; line-height: 1; }
    .stat-label { font-size: 0.85rem; color: #64748b; font-weight: 500; margin-top: 0.5rem; }

    /* === BADGES === */
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .badge-high { background: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; }
    .badge-medium { background: #fef3c7; color: #d97706; border: 1px solid #fcd34d; }
    .badge-low { background: #ccfbf1; color: #0d9488; border: 1px solid #99f6e4; }

    /* === DETAIL VIEW FOR ADMIN === */
    .detail-complaint-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
    }
    .detail-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .detail-value {
        font-size: 0.95rem;
        color: #0f172a;
        margin-bottom: 1rem;
    }
    .detail-value-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #334155;
        margin-bottom: 1rem;
    }

    /* === TIMELINE FLOW (PREVIEW) === */
    .timeline-flow {
        background: #f0fdf4;
        border: 1px dashed #22c55e;
        border-radius: 10px;
        padding: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        font-size: 0.95rem;
        color: #166534;
    }

    /* === BUTTONS & INPUTS === */
    .stButton > button {
        background: linear-gradient(135deg, #14b8a6, #0d9488) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(20, 184, 166, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 16px rgba(20, 184, 166, 0.3) !important;
        background: linear-gradient(135deg, #0d9488, #0f172a) !important;
    }
    
    /* Branding Sidebar */
    .sidebar-logo { text-align: center; padding: 1.5rem 0 0.5rem 0; }
    .sidebar-logo .logo-icon { font-size: 2.5rem; margin-bottom: 0.25rem; }
    .sidebar-logo .logo-text { font-size: 1.35rem; font-weight: 700; color: #ffffff; letter-spacing: 0.5px; }
    .sidebar-logo .logo-sub { font-size: 0.8rem; color: #ccfbf1; opacity: 0.7; margin-top: 0.1rem; }
</style>
""", unsafe_allow_html=True)

# ===== HELPER: QR CODE =====
def make_qr(url: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, box_size=6, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    return img

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">📢</div>
        <div class="logo-text">SiPengadu</div>
        <div class="logo-sub">Sistem Pengaduan Mahasiswa</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    menu = st.selectbox("🔀 Pilih Akses Menu", ["📝  Layanan Mahasiswa", "🔐  Dashboard Admin"])
    st.markdown("---")

    # ===== DISPLAY QR CODE AUTOMATED =====
    st.markdown("**📲 Akses Mobile Link**")
    
    url_aktif = st.session_state.ngrok_url

    if url_aktif:
        if "ERROR" in url_aktif:
            st.error(f"❌ Jalur Ngrok gagal: {url_aktif}")
        else:
            # Membikin QR Code berdasarkan URL yang sukses di-cache
            qr_img = make_qr(url_aktif)
            buf = BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, caption="Scan QR untuk membuka di Smartphone", use_container_width=True)
            st.markdown(f"<div style='word-break:break-all; font-size:0.75rem; color:#ccfbf1; text-align:center;'>🌐 {url_aktif}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div style='font-size:0.8rem; color:#ccfbf1; opacity:0.8; background:rgba(255,255,255,0.04);"
            "border-radius:10px; padding:0.75rem; text-align:center; border: 1px dashed rgba(255,255,255,0.15);'>"
            "⚠️ Periksa kembali baris token Ngrok Anda di file app.py."
            "</div>",
            unsafe_allow_html=True
        )

# ===================================================
# HALAMAN MAHASISWA
# ===================================================
if "Mahasiswa" in menu:
    st.markdown("""
    <div class="hero-section">
        <h1>Formulir Pengaduan Mahasiswa</h1>
        <p>Sampaikan aspirasi, keluhan, atau kendala fasilitas Anda dengan aman dan responsif</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_guide = st.columns([7, 5], gap="large")

    with col_main:
        with st.container(border=True):
            st.markdown('<div class="section-title">📝 Tulis Laporan Pengaduan</div>', unsafe_allow_html=True)
            
            kategori = st.selectbox(
                "Pilih Kategori Masalah",
                ["Akademik", "Fasilitas", "Layanan IT", "Keamanan", "Lainnya"],
                help="Sesuaikan pengaduan dengan rumpun bidang penanganan"
            )

            pengaduan = st.text_area(
                "Deskripsi Laporan Pengaduan",
                placeholder="Tulis kronologi atau detail kendala secara komprehensif di sini...",
                height=220,
                help="Uraikan laporan secara mendetail agar memudahkan tim administrasi melakukan verifikasi"
            )

            c_btn, _ = st.columns([5, 4])
            with c_btn:
                kirim = st.button("📨  Kirim Laporan Resmi", use_container_width=True)

            if kirim:
                if not pengaduan.strip():
                    st.warning("⚠️ Isi teks deskripsi pengaduan tidak boleh kosong!")
                else:
                    priority = detect_priority(pengaduan)
                    add_complaint(kategori, pengaduan, priority)
                    st.success(f"🎉 Laporan berhasil dikirimkan! Sistem mendeteksi otomatis skala prioritas: **{priority}**")

    with col_guide:
        st.markdown("""
        <div class="custom-card">
            <div class="section-title">📌 Klasterisasi Kategori</div>
            <div style="color:#475569; font-size:0.9rem; line-height:1.7;">
                <p style="margin-bottom: 0.8rem;"><strong>🔹 Akademik</strong><br><span style="color:#64748b;">Permasalahan nilai, sistem KRS, jadwal perkuliahan, atau bimbingan dosen.</span></p>
                <p style="margin-bottom: 0.8rem;"><strong>🔹 Fasilitas</strong><br><span style="color:#64748b;">Kerusakan ruang kelas, pendingin ruangan (AC), laboratorium, atau area parkir.</span></p>
                <p style="margin-bottom: 0.8rem;"><strong>🔹 Layanan IT</strong><br><span style="color:#64748b;">Kendala akses SIAKAD, Learning Management System (LMS), atau jaringan Wi-Fi kampus.</span></p>
                <p style="margin-bottom: 0.8rem;"><strong>🔹 Keamanan</strong><br><span style="color:#64748b;">Laporan kehilangan barang, tindakan kriminal, atau gangguan kenyamanan lingkungan.</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="custom-card" style="background: #f0fdf4; border: 1px solid #bbf7d0;">
            <div class="section-title" style="color:#166534; border-left-color: #22c55e;">📊 Informasi Penanganan</div>
            <div style="color:#166534; font-size:0.88rem; line-height:1.6;">
                Setiap berkas laporan yang masuk akan melewati klasifikasi Natural Language Processing (NLP) untuk penentuan tingkat urgensi. Estimasi peninjauan berkas berkisar antara <b>1–3 hari kerja</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===================================================
# DASHBOARD ADMIN
# ===================================================
elif "Admin" in menu:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("""
        <div class="hero-section">
            <h1>🔐 Autentikasi Admin</h1>
            <p>Silakan masuk untuk mengakses panel kendali dan manajemen pengaduan</p>
        </div>
        """, unsafe_allow_html=True)

        _, col_center, _ = st.columns([1, 1.8, 1])
        with col_center:
            with st.container(border=True):
                st.markdown('<div class="section-title">🔑 Login Kredensial</div>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Masukkan kode username admin")
                password = st.text_input("Password", type="password", placeholder="Masukkan kata sandi")

                if st.button("Masuk Ke Dashboard", use_container_width=True):
                    if login(username, password):
                        st.session_state.logged_in = True
                        st.success("✅ Otentikasi berhasil! Memuat halaman...")
                        st.rerun()
                    else:
                        st.error("❌ Kombinasi identitas username atau password salah!")
    else:
        st.markdown("""
        <div class="hero-section">
            <h1>📊 Central Dashboard Admin</h1>
            <p>Panel monitoring, filter data, dan manajemen disposisi status pengaduan mahasiswa</p>
        </div>
        """, unsafe_allow_html=True)

        data = get_all_complaints()

        if len(data) == 0:
            st.markdown("""
            <div class="custom-card" style="text-align:center; padding:4rem 2rem;">
                <div style="font-size:3.5rem;">📭</div>
                <div style="font-size:1.25rem; font-weight:600; color:#0f172a; margin-top:1rem;">Arsip Pengaduan Kosong</div>
                <div style="color:#64748b; margin-top:0.25rem;">Belum ada pengaduan baru yang dikirimkan oleh mahasiswa.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df = pd.DataFrame(data, columns=["ID", "Kategori", "Pengaduan", "Prioritas", "Status"])

            # Ringkasan Statistik Utama
            total = len(df)
            tinggi = len(df[df["Prioritas"] == "Tinggi"])
            sedang = len(df[df["Prioritas"] == "Sedang"])
            rendah = len(df[df["Prioritas"] == "Rendah"])
            selesai = len(df[df["Status"] == "Selesai"])

            c1, c2, c3, c4, c5 = st.columns(5)
            stats = [
                (c1, total, "Total Laporan", "#0f172a"),
                (c2, tinggi, "Prioritas Tinggi", "#ef4444"),
                (c3, sedang, "Prioritas Sedang", "#d97706"),
                (c4, rendah, "Prioritas Rendah", "#0d9488"),
                (c5, selesai, "Selesai Diproses", "#14b8a6")
            ]
            for col, val, label, color in stats:
                with col:
                    st.markdown(f"""
                    <div class="stat-card" style="border-top: 4px solid {color};">
                        <div class="stat-number" style="color:{color};">{val}</div>
                        <div class="stat-label">{label}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Bagian Filter Tabular Data
            with st.container(border=True):
                st.markdown('<div class="section-title">🔍 Parameter Filter Laporan</div>', unsafe_allow_html=True)
                
                def reset_filter():
                    st.session_state["filter_prioritas"] = "Semua"
                    st.session_state["filter_status"] = "Semua"

                if "filter_prioritas" not in st.session_state:
                    st.session_state["filter_prioritas"] = "Semua"
                if "filter_status" not in st.session_state:
                    st.session_state["filter_status"] = "Semua"

                fcol1, fcol2, fcol3 = st.columns([3, 3, 2])
                with fcol1:
                    priority_options = ["Semua"] + sorted(df["Prioritas"].unique().tolist())
                    filter_prioritas = st.selectbox(
                        "Skala Prioritas", priority_options,
                        index=priority_options.index(st.session_state["filter_prioritas"]),
                        key="filter_prioritas"
                    )
                with fcol2:
                    status_options = ["Semua"] + sorted(df["Status"].unique().tolist())
                    filter_status = st.selectbox(
                        "Status Tindak Lanjut", status_options,
                        index=status_options.index(st.session_state["filter_status"]),
                        key="filter_status"
                    )
                with fcol3:
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    st.button("🔄 Reset Parameter", use_container_width=True, on_click=reset_filter)

                df_filtered = df.copy()
                if filter_prioritas != "Semua":
                    df_filtered = df_filtered[df_filtered["Prioritas"] == filter_prioritas]
                if filter_status != "Semua":
                    df_filtered = df_filtered[df_filtered["Status"] == filter_status]

                st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
                st.dataframe(df_filtered, use_container_width=True, height=250, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Bagian Eksaminasi & Tindak Lanjut Pembaruan Status
            with st.container(border=True):
                st.markdown('<div class="section-title">✏️ Manajemen Disposisi & Pembaruan Status</div>', unsafe_allow_html=True)
                
                ids_available = df["ID"].tolist()
                col_left, col_right = st.columns([1, 1], gap="large")

                with col_left:
                    selected_id = st.selectbox("🔢 Pilih Nomor ID Laporan", ids_available)
                    if selected_id:
                        row = df[df["ID"] == selected_id].iloc[0]
                        
                        badge_map = {
                            "Tinggi": ("badge badge-high", "🔴 Tinggi"),
                            "Sedang": ("badge badge-medium", "🟡 Sedang"),
                            "Rendah": ("badge badge-low", "🟢 Rendah"),
                        }
                        badge_cls, badge_txt = badge_map.get(row["Prioritas"], ("badge", row["Prioritas"]))
                        status_icon = {"Diterima": "📥", "Diproses": "⚙️", "Selesai": "✅"}.get(row["Status"], "📌")

                        st.markdown(f"""
                        <div class="detail-complaint-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                                <span style="font-weight:700; color:#0f172a; font-size:1.05rem;">Berkas Kasus #{row['ID']}</span>
                                <span class="{badge_cls}">{badge_txt}</span>
                            </div>
                            <div class="detail-label">Rumpun Kategori</div>
                            <div class="detail-value">🗂️ {row['Kategori']}</div>
                            <div class="detail-label">Substansi Isi Laporan</div>
                            <div class="detail-value-box">{row['Pengaduan']}</div>
                            <div class="detail-label">Status Penanganan Saat Ini</div>
                            <div class="detail-value">{status_icon} <b>{row['Status']}</b></div>
                        </div>
                        """, unsafe_allow_html=True)

                with col_right:
                    new_status = st.selectbox(
                        "Tentukan Status Aksi Baru",
                        ["Diterima", "Diproses", "Selesai"],
                        help="Ubah status penanganan untuk menginformasikan progres kepada mahasiswa"
                    )

                    if selected_id:
                        row = df[df["ID"] == selected_id].iloc[0]
                        old_status = row["Status"]
                        
                        icon_old = {"Diterima": "📥", "Diproses": "⚙️", "Selesai": "✅"}.get(old_status, "📌")
                        icon_new = {"Diterima": "📥", "Diproses": "⚙️", "Selesai": "✅"}.get(new_status, "📌")
                        
                        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="detail-label">Simulasi Arus Perubahan Alur</div>
                        <div class="timeline-flow" style="background: {'#f0fdf4' if new_status != old_status else '#fffbeb'}; border-color: {'#22c55e' if new_status != old_status else '#f59e0b'}; color: {'#166534' if new_status != old_status else '#713f12'};">
                            <span>{icon_old} {old_status}</span>
                            <span style="font-weight:bold;">➔</span>
                            <span>{icon_new} <b>{new_status}</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
                    if st.button("💾 Simpan & Perbarui Status Kasus", use_container_width=True):
                        update_status(selected_id, new_status)
                        st.success(f"⚡ Sukses! Status Pengaduan #{selected_id} beralih menjadi berkas **{new_status}**")
                        st.rerun()

        # Tombol Keluar Sesi Admin
        st.markdown("<br><br>", unsafe_allow_html=True)
        _, col_logout_center, _ = st.columns([2, 1, 2])
        with col_logout_center:
            if st.button("🚪 Keluar Sesi Admin", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()