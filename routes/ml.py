# ============================================================
# routes/ml.py — Machine Learning: Decision Tree Classifier
# ============================================================

from flask import Blueprint, render_template, request, jsonify
from utils.ml_model import prediksi_kelayakan, get_model_info

ml_bp = Blueprint('ml', __name__)


# ------------------------------------------------------------
# GET /ml — Halaman prediksi ML
# ------------------------------------------------------------
@ml_bp.route('/')
def index():
    return render_template('prediksi_ml.html')


# ------------------------------------------------------------
# POST /ml/prediksi — Jalankan prediksi ML
# ------------------------------------------------------------
@ml_bp.route('/prediksi', methods=['POST'])
def prediksi():
    """
    Menjalankan prediksi Decision Tree berdasarkan data project di DB.
    """
    from utils.db import get_all_projects, save_prediksi_ml
    import uuid

    try:
        projects = get_all_projects()
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Gagal mengambil data dari database: {str(e)}'
        }), 500

    if not projects or len(projects) < 2:
        return jsonify({
            'success': False,
            'message': 'Minimal 2 project diperlukan. Silakan upload data project terlebih dahulu.'
        }), 400

    for p in projects:
        p['mrc']    = float(p['mrc'])
        p['sla']    = float(p['sla'])
        p['durasi'] = float(p['durasi'])

    try:
        hasil_prediksi, model_info = prediksi_kelayakan(projects)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error ML: {str(e)}'}), 500

    sesi_id = str(uuid.uuid4())

    # Simpan ke database
    prediksi_db = [
        {
            'project_id':   p['project_id'],
            'prediksi':     p['prediksi'],
            'probabilitas': p['probabilitas'],
        }
        for p in hasil_prediksi
    ]
    save_prediksi_ml(sesi_id, prediksi_db)

    return jsonify({
        'success':    True,
        'sesi_id':    sesi_id,
        'hasil':      hasil_prediksi,
        'model_info': model_info,
        'message':    f'Prediksi ML selesai untuk {len(hasil_prediksi)} project'
    })


# ------------------------------------------------------------
# GET /ml/info — Info model Decision Tree
# ------------------------------------------------------------
@ml_bp.route('/info', methods=['GET'])
def info():
    info = get_model_info()
    return jsonify({'success': True, 'info': info})
