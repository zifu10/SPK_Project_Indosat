# ============================================================
# routes/main.py — Halaman Utama
# ============================================================

import math
from flask import Blueprint, render_template, jsonify
from utils.db import get_all_projects, execute_query

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


# ------------------------------------------------------------
# GET /dashboard-stats
# Mengembalikan:
#   1. Jumlah Layak berdasarkan voting mayoritas (4 SPK + ML)
#   2. Preview top-5 hasil prediksi ML terbaru (untuk grafik dashboard)
# ------------------------------------------------------------
@main_bp.route('/dashboard-stats')
def dashboard_stats():

    METODE_SPK = ['AHP', 'SAW', 'MOORA', 'WP']

    # ── Voting mayoritas (untuk stat card) ───────────────────
    spk_votes        = {}
    metode_aktif_spk = 0

    for metode in METODE_SPK:
        rows = execute_query("""
            SELECT project_id, ranking
            FROM hasil_perhitungan
            WHERE metode = %s
              AND sesi_id = (
                  SELECT sesi_id FROM hasil_perhitungan
                  WHERE metode = %s
                  ORDER BY created_at DESC
                  LIMIT 1
              )
            ORDER BY ranking ASC
        """, (metode, metode), fetch=True) or []

        if not rows:
            continue

        metode_aktif_spk += 1
        total_rows        = len(rows)
        batas_layak       = math.ceil(total_rows / 2)

        for r in rows:
            pid = int(r['project_id'])
            spk_votes[pid] = spk_votes.get(pid, 0) + (
                1 if int(r['ranking']) <= batas_layak else 0
            )

    ada_spk = metode_aktif_spk > 0

    ml_rows_stat = execute_query("""
        SELECT project_id, prediksi
        FROM prediksi_ml
        WHERE sesi_id = (
            SELECT sesi_id FROM prediksi_ml
            ORDER BY created_at DESC
            LIMIT 1
        )
    """, fetch=True) or []

    ada_ml   = len(ml_rows_stat) > 0
    ml_votes = {}
    for r in ml_rows_stat:
        pid          = int(r['project_id'])
        ml_votes[pid] = 1 if r['prediksi'] == 'Layak' else 0

    if not ada_spk and not ada_ml:
        jumlah_layak     = None
        label_layak      = 'Belum dihitung'
    else:
        semua_pid         = set(spk_votes.keys()) | set(ml_votes.keys())
        total_suara_max   = metode_aktif_spk + (1 if ada_ml else 0)
        batas_mayoritas   = math.ceil(total_suara_max / 2)
        jumlah_layak      = sum(
            1 for pid in semua_pid
            if (spk_votes.get(pid, 0) + ml_votes.get(pid, 0)) >= batas_mayoritas
        )
        label_layak = _buat_label(ada_spk, ada_ml)

    # ── Preview hasil ML terbaru (top 5 + bottom 3) ──────────
    preview_ml = execute_query("""
        SELECT
            pm.project_id,
            p.nama_project,
            pm.prediksi,
            pm.probabilitas,
            p.mrc,
            p.sla,
            p.durasi
        FROM prediksi_ml pm
        JOIN projects p ON pm.project_id = p.id
        WHERE pm.sesi_id = (
            SELECT sesi_id FROM prediksi_ml
            ORDER BY created_at DESC
            LIMIT 1
        )
        ORDER BY pm.probabilitas DESC
        LIMIT 10
    """, fetch=True) or []

    # Konversi Decimal → float/str agar JSON-serializable
    preview_ml_clean = [
        {
            'project_id'  : int(r['project_id']),
            'nama_project': str(r['nama_project']),
            'prediksi'    : str(r['prediksi']),
            'skor_borda'  : round(float(r['probabilitas']) * 100, 1),
            'mrc'         : float(r['mrc']),
            'sla'         : float(r['sla']),
            'durasi'      : float(r['durasi']),
        }
        for r in preview_ml
    ]

    # Waktu sesi ML terakhir
    sesi_info = execute_query("""
        SELECT created_at FROM prediksi_ml
        ORDER BY created_at DESC
        LIMIT 1
    """, fetch=True) or []

    waktu_ml = str(sesi_info[0]['created_at']) if sesi_info else None
    
    # Ambil 5 project terbaru berdasarkan waktu input
    recent_projects = execute_query("""
        SELECT id, nama_project, mrc, sla, durasi
        FROM projects
        ORDER BY created_at DESC
        LIMIT 10
    """, fetch=True) or []

    recent_projects_clean = [
        {
            'id'          : int(r['id']),
            'nama_project': str(r['nama_project']),
            'mrc'         : float(r['mrc']),
            'sla'         : float(r['sla']),
            'durasi'      : float(r['durasi']),
        }
        for r in recent_projects
    ]
    
    return jsonify({
        'success'      : True,
        'ada_data'     : ada_spk or ada_ml,
        'ada_spk'      : ada_spk,
        'ada_ml'       : ada_ml,
        'jumlah_layak' : jumlah_layak,
        'label_layak'  : label_layak,
        'preview_ml'   : preview_ml_clean,
        'waktu_ml'     : waktu_ml,
        'recent_projects': recent_projects_clean,
    })


def _buat_label(ada_spk, ada_ml):
    if ada_spk and ada_ml:
        return 'Layak (Mayoritas 4 SPK + ML)'
    elif ada_spk:
        return 'Layak (Mayoritas SPK)'
    elif ada_ml:
        return 'Layak (ML terbaru)'
    return 'Belum dihitung'