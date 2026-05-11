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

BOBOT     = Config.BOBOT
SUB_BOBOT = Config.SUB_BOBOT


# ============================================================
# HELPER: Konversi nilai raw ke kategori sub-kriteria AHP
# ============================================================

def get_skor_mrc(mrc):
    if mrc < 100:   return 'rendah'
    if mrc <= 300:  return 'sedang'
    return 'tinggi'

def get_skor_sla(sla):
    return 'baik' if sla >= 98 else 'kurang'

def get_skor_durasi(durasi):
    if durasi <= 3:  return 'pendek'
    if durasi <= 5:  return 'sedang'
    return 'panjang'


# ============================================================
# METODE 1: AHP — Analytical Hierarchy Process
# Skor = Σ (bobot_kriteria × sub_bobot)
# ============================================================
def hitung_ahp(projects: list) -> list:
    hasil = []

    for p in projects:
        w_mrc    = SUB_BOBOT['mrc']   [get_skor_mrc   (float(p['mrc']))]
        w_sla    = SUB_BOBOT['sla']   [get_skor_sla   (float(p['sla']))]
        w_durasi = SUB_BOBOT['durasi'][get_skor_durasi(float(p['durasi']))]

        hasil.append({
            'project_id'  : p['id'],
            'nama_project': p['nama_project'],
            'skor'        : round(BOBOT['mrc'] * w_mrc + BOBOT['sla'] * w_sla + BOBOT['durasi'] * w_durasi, 6),
            'mrc_raw'     : float(p['mrc']),
            'sla_raw'     : float(p['sla']),
            'durasi_raw'  : float(p['durasi']),
            'norm_mrc'    : round(w_mrc,    6),
            'norm_sla'    : round(w_sla,    6),
            'norm_durasi' : round(w_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 2: SAW — Simple Additive Weighting
# Normalisasi: benefit = xij/max, cost = min/xij
# Skor = Σ (bobot × nilai_normalisasi)
# ============================================================
def hitung_saw(projects: list) -> list:
    if not projects:
        return []

    max_mrc    = max(float(p['mrc'])    for p in projects)
    min_sla    = min(float(p['sla'])    for p in projects)
    max_durasi = max(float(p['durasi']) for p in projects)

    hasil = []

    for p in projects:
        mrc    = float(p['mrc'])
        sla    = float(p['sla'])
        durasi = float(p['durasi'])

        norm_mrc    = mrc    / max_mrc    if max_mrc    != 0 else 0
        norm_sla    = min_sla / sla       if sla        != 0 else 0
        norm_durasi = durasi / max_durasi if max_durasi != 0 else 0

        hasil.append({
            'project_id'  : p['id'],
            'nama_project': p['nama_project'],
            'skor'        : round(BOBOT['mrc'] * norm_mrc + BOBOT['sla'] * norm_sla + BOBOT['durasi'] * norm_durasi, 6),
            'mrc_raw'     : mrc,
            'sla_raw'     : sla,
            'durasi_raw'  : durasi,
            'norm_mrc'    : round(norm_mrc,    6),
            'norm_sla'    : round(norm_sla,    6),
            'norm_durasi' : round(norm_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 3: MOORA — Multi-Objective Optimization Ratio Analysis
# Normalisasi: xij / sqrt(Σ xij²)
# Yi = Σ(bobot × benefit) − Σ(bobot × cost)
# ============================================================
def hitung_moora(projects: list) -> list:
    if not projects:
        return []

    denom_mrc    = math.sqrt(sum(float(p['mrc'])    ** 2 for p in projects)) or 1
    denom_sla    = math.sqrt(sum(float(p['sla'])    ** 2 for p in projects)) or 1
    denom_durasi = math.sqrt(sum(float(p['durasi']) ** 2 for p in projects)) or 1

    hasil = []

    for p in projects:
        mrc    = float(p['mrc'])
        sla    = float(p['sla'])
        durasi = float(p['durasi'])

        norm_mrc    = mrc    / denom_mrc
        norm_sla    = sla    / denom_sla
        norm_durasi = durasi / denom_durasi

        yi = BOBOT['mrc'] * norm_mrc + BOBOT['durasi'] * norm_durasi - BOBOT['sla'] * norm_sla

        hasil.append({
            'project_id'  : p['id'],
            'nama_project': p['nama_project'],
            'skor'        : round(yi, 6),
            'mrc_raw'     : mrc,
            'sla_raw'     : sla,
            'durasi_raw'  : durasi,
            'norm_mrc'    : round(norm_mrc,    6),
            'norm_sla'    : round(norm_sla,    6),
            'norm_durasi' : round(norm_durasi, 6),
        })

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# METODE 4: WP — Weighted Product
# Si = Π(xij^wj), cost pakai pangkat negatif
# Vi = Si / Σ Si
# ============================================================
def hitung_wp(projects: list) -> list:
    if not projects:
        return []

    total_bobot = sum(BOBOT.values())
    w_mrc    = BOBOT['mrc']    / total_bobot
    w_sla    = BOBOT['sla']    / total_bobot
    w_durasi = BOBOT['durasi'] / total_bobot

    hasil_s = []

    for p in projects:
        mrc    = float(p['mrc'])    or 0.001
        sla    = float(p['sla'])    or 0.001
        durasi = float(p['durasi']) or 0.001

        si = (mrc ** w_mrc) * (sla ** -w_sla) * (durasi ** w_durasi)

        hasil_s.append({
            'project_id'  : p['id'],
            'nama_project': p['nama_project'],
            'si'          : si,
            'mrc_raw'     : mrc,
            'sla_raw'     : sla,
            'durasi_raw'  : durasi,
        })

    total_si = sum(h['si'] for h in hasil_s)

    hasil = [
        {
            'project_id'  : h['project_id'],
            'nama_project': h['nama_project'],
            'skor'        : round(h['si'] / total_si if total_si else 0, 6),
            'si'          : round(h['si'], 6),
            'mrc_raw'     : h['mrc_raw'],
            'sla_raw'     : h['sla_raw'],
            'durasi_raw'  : h['durasi_raw'],
            'norm_mrc'    : round(h['mrc_raw']    ** w_mrc,   6),
            'norm_sla'    : round(h['sla_raw']    ** -w_sla,  6),
            'norm_durasi' : round(h['durasi_raw'] ** w_durasi, 6),
        }
        for h in hasil_s
    ]

    hasil.sort(key=lambda x: x['skor'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking'] = i + 1

    return hasil


# ============================================================
# DISPATCHER
# ============================================================
def jalankan_metode(metode: str, projects: list) -> list:
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