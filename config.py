# ============================================================
# config.py — Konfigurasi Aplikasi Flask
# SPK Indosat Ooredoo Hutchison
# ============================================================

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
    BOBOT = {
        'mrc':    0.633,   # Monthly Recurring Charge  (benefit — semakin besar semakin baik)
        'sla':    0.106,   # SLA Availability           (cost    — semakin kecil semakin baik)
        'durasi': 0.260,   # Contract Duration          (benefit — semakin besar semakin baik)
    }

    # Tipe kriteria: 'benefit' = lebih besar lebih baik, 'cost' = lebih kecil lebih baik
    TIPE_KRITERIA = {
        'mrc':    'benefit',
        'sla':    'cost',
        'durasi': 'benefit',
    }

    # Sub-bobot nilai kriteria (dari halaman Pembobotan AHP di PPT)
    SUB_BOBOT = {
        'mrc': {
            'rendah':  0.088,   # < 100 juta
            'sedang':  0.243,   # 100 - 300 juta
            'tinggi':  0.669,   # > 300 juta
        },
        'sla': {
            'baik':    0.167,   # 98 - 100%
            'kurang':  0.833,   # < 98%
        },
        'durasi': {
            'pendek':  0.110,   # 1 - 3 tahun
            'sedang':  0.309,   # 4 - 5 tahun
            'panjang': 0.581,   # > 5 tahun
        },
    }

    # Threshold untuk label ML
    # Project dengan skor SAW >= threshold dianggap "Layak"
    ML_THRESHOLD = 0.5
