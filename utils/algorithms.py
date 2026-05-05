# ============================================================
# utils/algorithms.py — Implementasi 4 Algoritma SPK
# AHP | SAW | MOORA | Weighted Product
# ============================================================
# Bobot FIXED dari hasil perhitungan AHP (PPT Kelompok 4):
#   MRC    = 0.633 (benefit)
#   SLA    = 0.106 (cost)
#   Durasi = 0.260 (benefit)
# ============================================================

import math
from config import Config

BOBOT  = Config.BOBOT
SUB_BOBOT = Config.SUB_BOBOT
TIPE   = Config.TIPE_KRITERIA


# ------------------------------------------------------------
# HELPER: Konversi nilai raw ke skor sub-kriteria (skala AHP)
# Sesuai tabel pembobotan di PPT halaman 10
# ------------------------------------------------------------
def get_skor_mrc(mrc):
    """MRC dalam juta rupiah → skor sub-kriteria"""
    if mrc < 100:
        return 'rendah'   # rendah
    elif mrc <= 300:
        return 'sedang'   # sedang
    else:
         return 'tinggi'   # tinggi

def get_skor_sla(sla):
    """SLA dalam persen → skor sub-kriteria (cost: semakin kecil semakin baik)"""
    if sla >= 98:
        return 'baik'   # baik (SLA terpenuhi)
    else:
        return 'kurang'   # kurang (SLA tidak terpenuhi)

def get_skor_durasi(durasi):
    """Durasi dalam tahun → skor sub-kriteria"""
    if durasi <= 3:
        return 'pendek'   # pendek
    elif durasi <= 5:
        return 'sedang'   # sedang
    else:
        return 'panjang'   # panjang

# ============================================================
# METODE 1: AHP (Analytical Hierarchy Process)
# Menggunakan bobot yang sudah dihitung dari matriks perbandingan
# Skor = Σ (bobot_kriteria × skor_sub_kriteria)
# ============================================================
def hitung_ahp(projects: list) -> list:
    """
    Menghitung skor AHP untuk setiap project.
    
    Args:
        projects: list of dict {id, nama_project, mrc, sla, durasi}
    
    Returns:
        list of dict {project_id, nama_project, skor, ranking,
                      detail: {mrc_skor, sla_skor, durasi_skor}}
    """
    hasil = []

    for p in projects:
        skor_mrc    = get_skor_mrc(float(p['mrc']))
        skor_sla    = get_skor_sla(float(p['sla']))
        skor_durasi = get_skor_durasi(float(p['durasi']))

        w_mrc = SUB_BOBOT['mrc'][skor_mrc]
        w_sla = SUB_BOBOT['sla'][skor_sla]
        w_durasi = SUB_BOBOT['durasi'][skor_durasi]

        skor_akhir = (
            BOBOT['mrc']    * w_mrc    +
            BOBOT['sla']    * w_sla    +
            BOBOT['durasi'] * w_durasi
        )

        hasil.append({
            'project_id':    p['id'],
            'nama_project':  p['nama_project'],
            'skor':          round(skor_akhir, 6),
            'mrc_raw':       float(p['mrc']),
            'sla_raw':       float(p['sla']),
            'durasi_raw':    float(p['durasi']),
            'norm_mrc':      round(w_mrc, 6),
            'norm_sla':      round(w_sla, 6),
            'norm_durasi':   round(w_durasi, 6),
        })

    # Urutkan berdasarkan skor tertinggi
    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 2: SAW (Simple Additive Weighting)
# Normalisasi: benefit = xij / max(xj), cost = min(xj) / xij
# Skor = Σ (bobot × nilai_normalisasi)
# ============================================================
def hitung_saw(projects: list) -> list:
    """
    Menghitung skor SAW untuk setiap project.
    """
    if not projects:
        return []

    # Ambil nilai max/min untuk normalisasi
    max_mrc    = max(float(p['mrc'])    for p in projects)
    min_sla    = min(float(p['sla'])    for p in projects)
    max_durasi = max(float(p['durasi']) for p in projects)

    hasil = []

    for p in projects:
        mrc    = float(p['mrc'])
        sla    = float(p['sla'])
        durasi = float(p['durasi'])

        # Normalisasi
        norm_mrc    = mrc / max_mrc          if max_mrc    != 0 else 0  # benefit
        norm_sla    = min_sla / sla          if sla        != 0 else 0  # cost
        norm_durasi = durasi / max_durasi    if max_durasi != 0 else 0  # benefit

        skor_akhir = (
            BOBOT['mrc']    * norm_mrc    +
            BOBOT['sla']    * norm_sla    +
            BOBOT['durasi'] * norm_durasi
        )

        hasil.append({
            'project_id':   p['id'],
            'nama_project': p['nama_project'],
            'skor':         round(skor_akhir, 6),
            'mrc_raw':      mrc,
            'sla_raw':      sla,
            'durasi_raw':   durasi,
            'norm_mrc':     round(norm_mrc, 6),
            'norm_sla':     round(norm_sla, 6),
            'norm_durasi':  round(norm_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 3: MOORA (Multi-Objective Optimization on Basis of Ratio Analysis)
# Normalisasi: xij / sqrt(Σ xij²)
# Yi = Σ(bobot × xij_benefit) - Σ(bobot × xij_cost)
# ============================================================
def hitung_moora(projects: list) -> list:
    """
    Menghitung skor MOORA untuk setiap project.
    """
    if not projects:
        return []

    # Hitung denominator (akar jumlah kuadrat) tiap kriteria
    sum_sq_mrc    = sum(float(p['mrc'])    ** 2 for p in projects)
    sum_sq_sla    = sum(float(p['sla'])    ** 2 for p in projects)
    sum_sq_durasi = sum(float(p['durasi']) ** 2 for p in projects)

    denom_mrc    = math.sqrt(sum_sq_mrc)    if sum_sq_mrc    > 0 else 1
    denom_sla    = math.sqrt(sum_sq_sla)    if sum_sq_sla    > 0 else 1
    denom_durasi = math.sqrt(sum_sq_durasi) if sum_sq_durasi > 0 else 1

    hasil = []

    for p in projects:
        mrc    = float(p['mrc'])
        sla    = float(p['sla'])
        durasi = float(p['durasi'])

        # Normalisasi rasio
        norm_mrc    = mrc    / denom_mrc
        norm_sla    = sla    / denom_sla
        norm_durasi = durasi / denom_durasi

        # Yi = benefit - cost (dengan pembobotan)
        # MRC = benefit, SLA = cost, Durasi = benefit
        yi = (
            BOBOT['mrc']    * norm_mrc    +   # benefit (+)
            BOBOT['durasi'] * norm_durasi -   # benefit (+)
            BOBOT['sla']    * norm_sla        # cost (-)
        )

        hasil.append({
            'project_id':   p['id'],
            'nama_project': p['nama_project'],
            'skor':         round(yi, 6),
            'mrc_raw':      mrc,
            'sla_raw':      sla,
            'durasi_raw':   durasi,
            'norm_mrc':     round(norm_mrc, 6),
            'norm_sla':     round(norm_sla, 6),
            'norm_durasi':  round(norm_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 4: WP (Weighted Product)
# Si = Π (xij ^ wj)
# Untuk cost: pangkat negatif (-wj)
# Vi = Si / Σ Si
# ============================================================
def hitung_wp(projects: list) -> list:
    """
    Menghitung skor Weighted Product untuk setiap project.
    """
    if not projects:
        return []

    # Normalisasi bobot (pastikan total = 1, sudah 1.0 tapi re-check)
    total_bobot = sum(BOBOT.values())
    w_mrc    = BOBOT['mrc']    / total_bobot
    w_sla    = BOBOT['sla']    / total_bobot
    w_durasi = BOBOT['durasi'] / total_bobot

    hasil_s = []

    for p in projects:
        mrc    = float(p['mrc'])
        sla    = float(p['sla'])
        durasi = float(p['durasi'])

        # Hindari nilai 0 (log tidak bisa 0)
        mrc    = mrc    if mrc    > 0 else 0.001
        sla    = sla    if sla    > 0 else 0.001
        durasi = durasi if durasi > 0 else 0.001

        # Si = MRC^(+w) × SLA^(-w) × Durasi^(+w)
        si = (
            (mrc    ** w_mrc)    *
            (sla    ** (-w_sla)) *   # cost: pangkat negatif
            (durasi ** w_durasi)
        )

        hasil_s.append({
            'project_id':   p['id'],
            'nama_project': p['nama_project'],
            'si':           si,
            'mrc_raw':      mrc,
            'sla_raw':      sla,
            'durasi_raw':   durasi,
        })

    # Vi = Si / Σ Si
    total_si = sum(h['si'] for h in hasil_s)

    hasil = []
    for h in hasil_s:
        vi = h['si'] / total_si if total_si != 0 else 0

        # Estimasi normalisasi per kriteria untuk tampilan detail
        hasil.append({
            'project_id':   h['project_id'],
            'nama_project': h['nama_project'],
            'skor':         round(vi, 6),
            'si':           round(h['si'], 6),
            'mrc_raw':      h['mrc_raw'],
            'sla_raw':      h['sla_raw'],
            'durasi_raw':   h['durasi_raw'],
            'norm_mrc':     round(h['mrc_raw'] ** w_mrc, 6),
            'norm_sla':     round(h['sla_raw'] ** (-w_sla), 6),
            'norm_durasi':  round(h['durasi_raw'] ** w_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# DISPATCHER: Jalankan metode berdasarkan nama
# ============================================================
def jalankan_metode(metode: str, projects: list) -> list:
    """
    Memanggil algoritma yang sesuai berdasarkan nama metode.
    
    Args:
        metode  : 'AHP' | 'SAW' | 'MOORA' | 'WP'
        projects: list of dict project dari database
    
    Returns:
        list hasil ranking
    """
    dispatcher = {
        'AHP':   hitung_ahp,
        'SAW':   hitung_saw,
        'MOORA': hitung_moora,
        'WP':    hitung_wp,
    }

    func = dispatcher.get(metode.upper())
    if not func:
        raise ValueError(f"Metode '{metode}' tidak dikenal. Pilih: AHP, SAW, MOORA, WP")

    return func(projects)
