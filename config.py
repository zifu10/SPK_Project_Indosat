# ============================================================
# config.py — Konfigurasi Aplikasi Flask
# SPK Indosat Ooredoo Hutchison
# ============================================================
import numpy as np

class Config:
    # --- Database ---
    DB_HOST     = 'localhost'
    DB_USER     = 'root'
    DB_PASSWORD = ''           # Sesuaikan dengan password MySQL XAMPP kamu
    DB_NAME     = 'spk_indosat'
    DB_PORT     = 3306

    # --- Flask ---
    SECRET_KEY  = 'spk-indosat-2024-secret'
    DEBUG       = True

    # ============================================================
    # BOBOT KRITERIA — FIXED (hasil perhitungan AHP, tidak bisa diubah user)
    # Sumber: PPT Kelompok 4 — halaman Pembobotan AHP
    # ============================================================

    # Kriteria utama: MRC, SLA, Durasi
    _M_KRITERIA = np.array([
        [1.0000, 5.0000, 3.0000],   # Monthly Recurring Charge  (benefit — semakin besar semakin baik)
        [0.2000, 1.0000, 0.3333],   # SLA Availability           (cost    — semakin kecil semakin baik)
        [0.3333, 3.0000, 1.0000],   # Contract Duration          (benefit — semakin besar semakin baik)
    ])

    # Tipe kriteria: 'benefit' = lebih besar lebih baik, 'cost' = lebih kecil lebih baik
    TIPE_KRITERIA = {
        'mrc':    'benefit',
        'sla':    'cost',
        'durasi': 'benefit',
    }

    # Sub-kriteria MRC: rendah (<100jt), sedang (100-300jt), tinggi (>300jt)
    _M_MRC = np.array([
        [1.0000, 0.3333, 0.1429],   # rendah
        [3.0000, 1.0000, 0.3333],   # sedang
        [7.0000, 3.0000, 1.0000],   # tinggi
    ])

    # Sub-kriteria SLA: baik (98-100%), kurang (<98%)
    _M_SLA = np.array([
        [1.0, 0.2],   # baik
        [5.0, 1.0],   # kurang
    ])

    # Sub-kriteria Durasi: pendek (1-3thn), sedang (4-5thn), panjang (>5thn)
    _M_DURASI = np.array([
        [1.0000, 0.3333, 0.2000],   # pendek
        [3.0000, 1.0000, 0.5000],   # sedang
        [5.0000, 2.0000, 1.0000],   # panjang
    ])

    #Jumlah tiap kolom
    _KOLOM_KRITERIA = _M_KRITERIA.sum(axis=0)
    _KOLOM_MRC      = _M_MRC.sum(axis=0)
    _KOLOM_SLA      = _M_SLA.sum(axis=0)
    _KOLOM_DURASI   = _M_DURASI.sum(axis=0)

    #Normalisasi
    _NORM_KRITERIA = _M_KRITERIA / _KOLOM_KRITERIA
    _NORM_MRC      = _M_MRC      / _KOLOM_MRC
    _NORM_SLA      = _M_SLA      / _KOLOM_SLA
    _NORM_DURASI   = _M_DURASI   / _KOLOM_DURASI

    #Bobot prioritas
    _BOBOT_KRITERIA = _NORM_KRITERIA.mean(axis=1)
    _BOBOT_MRC      = _NORM_MRC.mean(axis=1)
    _BOBOT_SLA      = _NORM_SLA.mean(axis=1)
    _BOBOT_DURASI   = _NORM_DURASI.mean(axis=1)

    #Weighted sum
    _WS_KRITERIA = _M_KRITERIA @ _BOBOT_KRITERIA
    _WS_MRC      = _M_MRC      @ _BOBOT_MRC
    _WS_SLA      = _M_SLA      @ _BOBOT_SLA
    _WS_DURASI   = _M_DURASI   @ _BOBOT_DURASI

    #Eigen value
    _EIGEN_KRITERIA = _WS_KRITERIA / _BOBOT_KRITERIA
    _EIGEN_MRC      = _WS_MRC      / _BOBOT_MRC
    _EIGEN_SLA      = _WS_SLA      / _BOBOT_SLA
    _EIGEN_DURASI   = _WS_DURASI   / _BOBOT_DURASI

    #Rata-rata eigen value (lambda max)
    _LAMBDA_KRITERIA = float(_EIGEN_KRITERIA.mean())
    _LAMBDA_MRC      = float(_EIGEN_MRC.mean())
    _LAMBDA_SLA      = float(_EIGEN_SLA.mean())
    _LAMBDA_DURASI   = float(_EIGEN_DURASI.mean())

    #CI
    _CI_KRITERIA = (_LAMBDA_KRITERIA - 3) / (3 - 1)
    _CI_MRC      = (_LAMBDA_MRC      - 3) / (3 - 1)
    _CI_SLA      = (_LAMBDA_SLA      - 2) / (2 - 1)
    _CI_DURASI   = (_LAMBDA_DURASI   - 3) / (3 - 1)

    #CR
    _RI_3 = 0.52
    _RI_2 = 0.00

    _CR_KRITERIA = _CI_KRITERIA / _RI_3
    _CR_MRC      = _CI_MRC      / _RI_3
    _CR_SLA      = 0.0                    # RI=0 untuk n=2, CR didefinisikan 0
    _CR_DURASI   = _CI_DURASI   / _RI_3

    # Konsistensi: CR <= 0.1 → konsisten
    _KONSISTEN_KRITERIA = bool(_CR_KRITERIA <= 0.1)
    _KONSISTEN_MRC      = bool(_CR_MRC      <= 0.1)
    _KONSISTEN_SLA      = True
    _KONSISTEN_DURASI   = bool(_CR_DURASI   <= 0.1)

    # BOBOT dan SUB_BOBOT hanya dihitung jika semua matriks konsisten
    if _KONSISTEN_KRITERIA and _KONSISTEN_MRC and _KONSISTEN_SLA and _KONSISTEN_DURASI:
        BOBOT = {
            'mrc'   : round(float(_BOBOT_KRITERIA[0]), 3),
            'sla'   : round(float(_BOBOT_KRITERIA[1]), 3),
            'durasi': round(float(_BOBOT_KRITERIA[2]), 3),
        }
        SUB_BOBOT = {
            'mrc': {
                'rendah': round(float(_BOBOT_MRC[0]), 3),
                'sedang': round(float(_BOBOT_MRC[1]), 3),
                'tinggi': round(float(_BOBOT_MRC[2]), 3),
            },
            'sla': {
                'baik'  : round(float(_BOBOT_SLA[0]), 3),
                'kurang': round(float(_BOBOT_SLA[1]), 3),
            },
            'durasi': {
                'pendek' : round(float(_BOBOT_DURASI[0]), 3),
                'sedang' : round(float(_BOBOT_DURASI[1]), 3),
                'panjang': round(float(_BOBOT_DURASI[2]), 3),
            },
        }
    else:
        raise ValueError(
            f"Matriks tidak konsisten! "
            f"CR Kriteria={_CR_KRITERIA:.4f} ({'OK' if _KONSISTEN_KRITERIA else 'GAGAL'}) | "
            f"CR MRC={_CR_MRC:.4f} ({'OK' if _KONSISTEN_MRC else 'GAGAL'}) | "
            f"CR SLA={_CR_SLA:.4f} ({'OK' if _KONSISTEN_SLA else 'GAGAL'}) | "
            f"CR Durasi={_CR_DURASI:.4f} ({'OK' if _KONSISTEN_DURASI else 'GAGAL'})"
        )

    # Threshold untuk label ML
    # Project dengan skor SAW >= threshold dianggap "Layak"
    ML_THRESHOLD = 0.5
