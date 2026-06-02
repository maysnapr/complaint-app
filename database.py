import sqlite3

DB_NAME = "complaints.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            complaint TEXT,
            priority TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_complaint(category, complaint, priority):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO complaints
        (category, complaint, priority, status)
        VALUES (?, ?, ?, ?)
    """,
    (category, complaint, priority, "Diterima"))

    conn.commit()
    conn.close()


def get_all_complaints():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM complaints")

    data = c.fetchall()

    conn.close()

    return data


def update_status(id_pengaduan, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        UPDATE complaints
        SET status=?
        WHERE id=?
    """,
    (status, id_pengaduan))

    conn.commit()
    conn.close()