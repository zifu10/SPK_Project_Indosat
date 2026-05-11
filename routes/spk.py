# ============================================================
# routes/spk.py — Perhitungan SPK (AHP, SAW, MOORA, WP)
# ============================================================

import uuid
from flask import Blueprint, render_template, request, jsonify
from utils.db import get_all_projects, save_hasil, execute_many
from utils.algorithms import jalankan_metode

spk_bp = Blueprint('spk', __name__)


# ------------------------------------------------------------
# GET /spk — Halaman pilih metode & tampilkan hasil
# ------------------------------------------------------------
@spk_bp.route('/')
def index():
    projects = get_all_projects()
    return render_template('perhitungan.html', total_project=len(projects))


# ------------------------------------------------------------
# POST /spk/hitung — Jalankan perhitungan satu metode SPK
# ------------------------------------------------------------
@spk_bp.route('/hitung', methods=['POST'])
def hitung():
    data   = request.get_json()
    metode = data.get('metode', '').upper()

    if metode not in ['AHP', 'SAW', 'MOORA', 'WP']:
        return jsonify({
            'success': False,
            'message': 'Metode tidak valid. Pilih: AHP, SAW, MOORA, WP'
        }), 400

    try:
        projects = get_all_projects()
    except Exception as e:
        return jsonify({'success': False, 'message': f'Gagal mengambil data: {str(e)}'}), 500

    if not projects or len(projects) < 2:
        return jsonify({
            'success': False,
            'message': 'Minimal 2 project diperlukan. Silakan upload data project terlebih dahulu di menu Data Project.'
        }), 400

    for p in projects:
        p['mrc']    = float(p['mrc'])
        p['sla']    = float(p['sla'])
        p['durasi'] = float(p['durasi'])

    try:
        hasil = jalankan_metode(metode, projects)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error perhitungan: {str(e)}'}), 500

    sesi_id  = str(uuid.uuid4())
    hasil_db = [{'project_id': h['project_id'], 'skor': h['skor'], 'ranking': h['ranking']} for h in hasil]
    save_hasil(sesi_id, metode, hasil_db)
    _simpan_detail_normalisasi(sesi_id, metode, hasil)

    return jsonify({
        'success': True,
        'sesi_id': sesi_id,
        'metode':  metode,
        'hasil':   hasil,
        'message': f'Perhitungan {metode} berhasil untuk {len(hasil)} project'
    })


# ------------------------------------------------------------
# POST /spk/hitung-semua — Jalankan semua 4 metode sekaligus
# ------------------------------------------------------------
@spk_bp.route('/hitung-semua', methods=['POST'])
def hitung_semua():
    projects = get_all_projects()

    if len(projects) < 2:
        return jsonify({'success': False, 'message': 'Minimal 2 project diperlukan'}), 400

    for p in projects:
        p['mrc']    = float(p['mrc'])
        p['sla']    = float(p['sla'])
        p['durasi'] = float(p['durasi'])

    sesi_id     = str(uuid.uuid4())
    semua_hasil = {}

    for metode in ['AHP', 'SAW', 'MOORA', 'WP']:
        try:
            hasil        = jalankan_metode(metode, projects)
            semua_hasil[metode] = hasil
            hasil_db     = [{'project_id': h['project_id'], 'skor': h['skor'], 'ranking': h['ranking']} for h in hasil]
            save_hasil(sesi_id, metode, hasil_db)
            _simpan_detail_normalisasi(sesi_id, metode, hasil)
        except Exception as e:
            semua_hasil[metode] = {'error': str(e)}

    return jsonify({
        'success':     True,
        'sesi_id':     sesi_id,
        'semua_hasil': semua_hasil,
        'message':     'Semua metode berhasil dihitung'
    })


# ------------------------------------------------------------
# GET /spk/hasil/<sesi_id>/<metode> — Ambil hasil dari DB
# ------------------------------------------------------------
@spk_bp.route('/hasil/<sesi_id>/<metode>', methods=['GET'])
def get_hasil(sesi_id, metode):
    from utils.db import get_hasil_by_sesi
    hasil = get_hasil_by_sesi(sesi_id, metode.upper())

    for h in hasil:
        h['skor']       = float(h['skor'])
        h['mrc']        = float(h['mrc'])
        h['sla']        = float(h['sla'])
        h['durasi']     = float(h['durasi'])
        h['created_at'] = str(h['created_at'])

    return jsonify({'success': True, 'data': hasil})


# ------------------------------------------------------------
# HELPER: Simpan detail normalisasi ke database
# ------------------------------------------------------------
def _simpan_detail_normalisasi(sesi_id, metode, hasil):
    execute_many(
        """INSERT INTO detail_normalisasi
               (sesi_id, metode, project_id, nilai_mrc_norm, nilai_sla_norm, nilai_dur_norm)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        [
            (sesi_id, metode, h['project_id'],
             h.get('norm_mrc', 0), h.get('norm_sla', 0), h.get('norm_durasi', 0))
            for h in hasil
        ]
    )