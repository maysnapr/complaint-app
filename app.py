import streamlit as st
import pandas as pd

from database import *
from auth import login
from nlp import detect_priority

create_table()

st.set_page_config(
    page_title="Sistem Pengaduan Mahasiswa",
    layout="wide"
)

st.title("📢 Sistem Pengaduan Mahasiswa")

menu = st.sidebar.selectbox(
    "Menu",
    ["Mahasiswa", "Admin"]
)

# ==================================================
# MAHASISWA
# ==================================================

if menu == "Mahasiswa":

    st.header("Form Pengaduan")

    kategori = st.selectbox(
        "Kategori",
        [
            "Akademik",
            "Fasilitas",
            "IT/Sistem SPADA",
            "Administrasi",
            "Lainnya"
        ]
    )

    pengaduan = st.text_area(
        "Tuliskan Pengaduan"
    )

    if st.button("Kirim Pengaduan"):

        if pengaduan.strip() == "":
            st.warning("Isi pengaduan terlebih dahulu")
        else:

            priority = detect_priority(
                pengaduan
            )

            add_complaint(
                kategori,
                pengaduan,
                priority
            )

            st.success(
                f"Pengaduan berhasil dikirim. Prioritas: {priority}"
            )

# ==================================================
# ADMIN
# ==================================================

elif menu == "Admin":

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:

        st.subheader("Login Admin")

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if login(username, password):

                st.session_state.logged_in = True

                st.success("Login Berhasil")

                st.rerun()

            else:

                st.error("Login Gagal")

    else:

        st.header("Dashboard Admin")

        data = get_all_complaints()

        if len(data) == 0:

            st.info(
                "Belum ada pengaduan"
            )

        else:

            df = pd.DataFrame(
                data,
                columns=[
                    "ID",
                    "Kategori",
                    "Pengaduan",
                    "Prioritas",
                    "Status"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            st.divider()

            st.subheader(
                "Update Status Pengaduan"
            )

            ids = df["ID"].tolist()

            selected_id = st.selectbox(
                "Pilih ID",
                ids
            )

            new_status = st.selectbox(
                "Status Baru",
                [
                    "Diterima",
                    "Diproses",
                    "Selesai"
                ]
            )

            if st.button("Update Status"):

                update_status(
                    selected_id,
                    new_status
                )

                st.success(
                    "Status berhasil diperbarui"
                )

                st.rerun()

        if st.button("Logout"):

            st.session_state.logged_in = False

            st.rerun()