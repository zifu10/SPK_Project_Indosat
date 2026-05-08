# ============================================================
# routes/ml.py — Agregasi Borda Count dari 4 Metode SPK
# ============================================================

import uuid
from flask import Blueprint, render_template, request, jsonify
from utils.ml_model import jalankan_agregasi
from utils.db import execute_many

ml_bp = Blueprint('ml', __name__)


# ------------------------------------------------------------
# GET /ml — Halaman prediksi ML
# ------------------------------------------------------------
@ml_bp.route('/')
def index():
    return render_template('prediksi_ml.html')


# ------------------------------------------------------------
# POST /ml/prediksi — Jalankan agregasi Borda Count
# ------------------------------------------------------------
@ml_bp.route('/prediksi', methods=['POST'])
def prediksi():
    try:
        hasil, info = jalankan_agregasi(min_metode=4)
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error agregasi: {str(e)}'}), 500

    # Simpan hasil ke tabel prediksi_ml
    # Mapping: Sangat Layak & Layak → 'Layak', Tidak Layak → 'Tidak Layak'
    sesi_id = str(uuid.uuid4())
    params  = [
        (
            sesi_id,
            h['project_id'],
            'Layak' if h['kategori'] in ('Sangat Layak', 'Layak') else 'Tidak Layak',
            round(h['skor_borda'] / 100, 4),   # simpan sebagai 0–1
        )
        for h in hasil
    ]
    execute_many(
        "INSERT INTO prediksi_ml (sesi_id, project_id, prediksi, probabilitas) "
        "VALUES (%s, %s, %s, %s)",
        params
    )

    return jsonify({
        'success' : True,
        'sesi_id' : sesi_id,
        'hasil'   : hasil,
        'info'    : info,
        'message' : f'Agregasi Borda Count selesai untuk {len(hasil)} project',
    })