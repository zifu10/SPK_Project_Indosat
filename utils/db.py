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
    
    Args:
        query  : SQL query string
        params : tuple/list parameter untuk prepared statement
        fetch  : True jika ingin mengambil hasil (SELECT)
    
    Returns:
        List of dict jika fetch=True, lastrowid jika INSERT, None jika error
    """
    conn = get_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            return result
        else:
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
    
    Args:
        query       : SQL INSERT query
        params_list : list of tuples
    
    Returns:
        True jika berhasil, False jika gagal
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
# Helper: Ambil semua project dari database
# ============================================================
def get_all_projects():
    query = "SELECT * FROM projects ORDER BY id ASC"
    return execute_query(query, fetch=True) or []


def get_project_by_id(project_id):
    query = "SELECT * FROM projects WHERE id = %s"
    result = execute_query(query, (project_id,), fetch=True)
    return result[0] if result else None


def insert_projects_bulk(projects: list):
    """
    Bulk insert project dari hasil upload Excel.
    projects: list of dict dengan key nama_project, mrc, sla, durasi
    """
    query = """
        INSERT INTO projects (nama_project, mrc, sla, durasi)
        VALUES (%s, %s, %s, %s)
    """
    params = [(p['nama_project'], p['mrc'], p['sla'], p['durasi']) for p in projects]
    return execute_many(query, params)


def update_project(project_id, nama, mrc, sla, durasi):
    query = """
        UPDATE projects
        SET nama_project = %s, mrc = %s, sla = %s, durasi = %s
        WHERE id = %s
    """
    return execute_query(query, (nama, mrc, sla, durasi, project_id))


def delete_project(project_id):
    query = "DELETE FROM projects WHERE id = %s"
    return execute_query(query, (project_id,))


def clear_all_projects():
    query = "DELETE FROM projects"
    return execute_query(query)


# ============================================================
# Helper: Simpan hasil perhitungan SPK
# ============================================================
def save_hasil(sesi_id, metode, hasil_list):
    """
    Simpan hasil ranking ke tabel hasil_perhitungan.
    hasil_list: list of dict {project_id, skor, ranking}
    """
    query = """
        INSERT INTO hasil_perhitungan (sesi_id, metode, project_id, skor, ranking)
        VALUES (%s, %s, %s, %s, %s)
    """
    params = [
        (sesi_id, metode, h['project_id'], h['skor'], h['ranking'])
        for h in hasil_list
    ]
    return execute_many(query, params)


def save_prediksi_ml(sesi_id, prediksi_list):
    """
    Simpan hasil prediksi ML.
    prediksi_list: list of dict {project_id, prediksi, probabilitas}
    """
    query = """
        INSERT INTO prediksi_ml (sesi_id, project_id, prediksi, probabilitas)
        VALUES (%s, %s, %s, %s)
    """
    params = [
        (sesi_id, p['project_id'], p['prediksi'], p['probabilitas'])
        for p in prediksi_list
    ]
    return execute_many(query, params)


def get_hasil_by_sesi(sesi_id, metode):
    """Ambil hasil perhitungan berdasarkan sesi_id dan metode."""
    query = """
        SELECT h.*, p.nama_project, p.mrc, p.sla, p.durasi
        FROM hasil_perhitungan h
        JOIN projects p ON h.project_id = p.id
        WHERE h.sesi_id = %s AND h.metode = %s
        ORDER BY h.ranking ASC
    """
    return execute_query(query, (sesi_id, metode), fetch=True) or []
