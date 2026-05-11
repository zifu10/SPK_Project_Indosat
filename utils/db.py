# ============================================================
# utils/db.py — Koneksi dan Helper Database
# ============================================================

import mysql.connector
from mysql.connector import Error
from config import Config


def get_connection():
    """Membuat koneksi ke MySQL database."""
    try:
        conn = mysql.connector.connect(
            host     = Config.DB_HOST,
            user     = Config.DB_USER,
            password = Config.DB_PASSWORD,
            database = Config.DB_NAME,
            port     = Config.DB_PORT
        )
        return conn
    except Error as e:
        print(f"[DB ERROR] Gagal koneksi ke database: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    """
    Helper untuk menjalankan query.
    Returns list of dict jika fetch=True, lastrowid jika INSERT, None jika error.
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            return cursor.fetchall()

        conn.commit()
        return cursor.lastrowid

    except Error as e:
        print(f"[DB ERROR] Query gagal: {e}")
        print(f"  Query : {query}")
        print(f"  Params: {params}")
        conn.rollback()
        return None

    finally:
        cursor.close()
        conn.close()


def execute_many(query, params_list):
    """
    Helper untuk bulk insert (executemany).
    Returns True jika berhasil, False jika gagal.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return True

    except Error as e:
        print(f"[DB ERROR] Bulk insert gagal: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


# ============================================================
# Project helpers
# ============================================================

def get_all_projects():
    return execute_query("SELECT * FROM projects ORDER BY id ASC", fetch=True) or []


def insert_projects_bulk(projects: list):
    return execute_many(
        "INSERT INTO projects (nama_project, mrc, sla, durasi) VALUES (%s, %s, %s, %s)",
        [(p['nama_project'], p['mrc'], p['sla'], p['durasi']) for p in projects]
    )


def update_project(project_id, nama, mrc, sla, durasi):
    return execute_query(
        "UPDATE projects SET nama_project=%s, mrc=%s, sla=%s, durasi=%s WHERE id=%s",
        (nama, mrc, sla, durasi, project_id)
    )


def delete_project(project_id):
    return execute_query("DELETE FROM projects WHERE id = %s", (project_id,))


def clear_all_projects():
    return execute_query("DELETE FROM projects")


# ============================================================
# SPK helpers
# ============================================================

def save_hasil(sesi_id, metode, hasil_list):
    """Simpan hasil ranking ke tabel hasil_perhitungan."""
    return execute_many(
        "INSERT INTO hasil_perhitungan (sesi_id, metode, project_id, skor, ranking) VALUES (%s, %s, %s, %s, %s)",
        [(sesi_id, metode, h['project_id'], h['skor'], h['ranking']) for h in hasil_list]
    )


def get_hasil_by_sesi(sesi_id, metode):
    return execute_query(
        """SELECT h.*, p.nama_project, p.mrc, p.sla, p.durasi
           FROM hasil_perhitungan h
           JOIN projects p ON h.project_id = p.id
           WHERE h.sesi_id = %s AND h.metode = %s
           ORDER BY h.ranking ASC""",
        (sesi_id, metode), fetch=True
    ) or []