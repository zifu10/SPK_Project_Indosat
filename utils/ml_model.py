# ============================================================
# utils/ml_model.py — Decision Tree Classifier
# ============================================================
# Cara kerja:
# 1. Gunakan data project yang ada di DB sebagai input
# 2. Generate label "Layak/Tidak Layak" berdasarkan skor SAW
#    (project dengan skor SAW >= median = Layak)
# 3. Latih Decision Tree dengan data tersebut
# 4. Prediksi label + probabilitas untuk setiap project
# ============================================================

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from config import Config

THRESHOLD = Config.ML_THRESHOLD


def _generate_labels(projects: list) -> list:
    """
    Generate label kelayakan berdasarkan skor SAW.
    Project dengan skor SAW di atas median = Layak (1), sisanya = Tidak Layak (0).
    """
    from utils.algorithms import hitung_saw

    hasil_saw = hitung_saw(projects)

    # Buat mapping project_id → skor SAW
    skor_map = {h['project_id']: h['skor'] for h in hasil_saw}

    skor_list = list(skor_map.values())
    median    = np.median(skor_list)

    labels = {}
    for project_id, skor in skor_map.items():
        labels[project_id] = 1 if skor >= median else 0

    return labels


def prediksi_kelayakan(projects: list):
    """
    Melatih Decision Tree dan memprediksi kelayakan project.

    Args:
        projects: list of dict {id, nama_project, mrc, sla, durasi}

    Returns:
        (hasil_prediksi, model_info)
        hasil_prediksi: list of dict {project_id, nama_project, prediksi, probabilitas, label_num}
        model_info: dict berisi info model (akurasi training, kedalaman pohon, dll)
    """
    if len(projects) < 2:
        raise ValueError("Minimal 2 project untuk melatih model")

    # ---- Prepare fitur (X) ----
    X = np.array([
        [p['mrc'], p['sla'], p['durasi']]
        for p in projects
    ], dtype=float)

    # Normalisasi fitur ke skala 0-1
    scaler  = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # ---- Generate label (y) ----
    label_map = _generate_labels(projects)
    y = np.array([label_map[p['id']] for p in projects])

    # ---- Latih Decision Tree ----
    # max_depth dibatasi agar tidak overfitting pada data kecil
    model = DecisionTreeClassifier(
        max_depth        = 3,
        min_samples_leaf = 1,
        random_state     = 42,
        criterion        = 'gini'
    )
    model.fit(X_scaled, y)

    # ---- Prediksi ----
    y_pred  = model.predict(X_scaled)
    y_proba = model.predict_proba(X_scaled)

    # Indeks kelas: model.classes_ = [0, 1] atau [0] atau [1]
    # Pastikan kita ambil probabilitas untuk kelas 1 (Layak)
    classes = list(model.classes_)
    idx_layak = classes.index(1) if 1 in classes else 0

    # ---- Susun hasil ----
    hasil = []
    for i, p in enumerate(projects):
        label_num   = int(y_pred[i])
        proba_layak = float(y_proba[i][idx_layak])

        hasil.append({
            'project_id':   p['id'],
            'nama_project': p['nama_project'],
            'mrc':          p['mrc'],
            'sla':          p['sla'],
            'durasi':       p['durasi'],
            'prediksi':     'Layak' if label_num == 1 else 'Tidak Layak',
            'probabilitas': round(proba_layak, 4),
            'label_num':    label_num,
            'label_asli':   'Layak' if label_map[p['id']] == 1 else 'Tidak Layak',
        })

    # Urutkan: Layak dulu, lalu Tidak Layak, berdasarkan probabilitas
    hasil.sort(key=lambda x: x['probabilitas'], reverse=True)

    # ---- Info Model ----
    akurasi_training = float(np.mean(y_pred == y))

    # Feature importance
    feature_names   = ['MRC', 'SLA Availability', 'Contract Duration']
    importances     = model.feature_importances_

    model_info = {
        'algoritma':          'Decision Tree (CART)',
        'kriteria_split':     'Gini Impurity',
        'max_depth':          int(model.get_depth()),
        'jumlah_node':        int(model.tree_.node_count),
        'jumlah_leaf':        int(model.get_n_leaves()),
        'akurasi_training':   round(akurasi_training * 100, 2),
        'jumlah_data':        int(len(projects)),
        'jumlah_layak':       int(sum(y)),
        'jumlah_tidak_layak': int(len(y) - sum(y)),
        'feature_importance': {
            name: round(float(imp), 4)
            for name, imp in zip(feature_names, importances)
        },
        'catatan': (
            'Model dilatih menggunakan data project yang ada. '
            'Label "Layak/Tidak Layak" ditentukan berdasarkan skor SAW '
            '(project dengan skor >= median = Layak).'
        )
    }

    return hasil, model_info


def get_model_info():
    """Kembalikan info dasar model tanpa menjalankan prediksi."""
    return {
        'algoritma':      'Decision Tree Classifier (scikit-learn)',
        'fitur_input':    ['MRC (juta Rp)', 'SLA Availability (%)', 'Contract Duration (tahun)'],
        'output':         ['Layak', 'Tidak Layak'],
        'metode_label':   'Berdasarkan skor SAW (threshold = median)',
        'preprocessing':  'MinMaxScaler (normalisasi 0-1)',
        'hyperparameter': {
            'max_depth':        3,
            'criterion':        'gini',
            'min_samples_leaf': 1,
            'random_state':     42,
        }
    }
