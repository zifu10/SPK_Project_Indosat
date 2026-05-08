# ============================================================
# utils/ml_model.py — Borda Count Rank Aggregation
# ============================================================
# Cara kerja:
# 1. Ambil ranking dari 4 metode SPK (sesi terbaru di DB)
# 2. Hitung skor Borda tiap project:
#    poin_borda = N - ranking  (ranking 1 dari N project → N-1 poin)
# 3. Jumlahkan poin dari semua metode, normalisasi ke 0–100%
# 4. Tentukan kategori:
#    ≥ 75% = Sangat Layak | 50–74% = Layak | < 50% = Tidak Layak
# 5. Hitung konsistensi antar metode per project
# ============================================================

import math
from utils.db import execute_query

METODE_SPK = ['AHP', 'SAW', 'MOORA', 'WP']


def _ambil_ranking_terbaru():
    """Ambil ranking sesi terbaru tiap metode dari database."""
    hasil         = {}
    metode_aktif  = []

    for metode in METODE_SPK:
        rows = execute_query("""
            SELECT h.project_id, p.nama_project, p.mrc, p.sla, p.durasi,
                   h.ranking, h.skor
            FROM hasil_perhitungan h
            JOIN projects p ON h.project_id = p.id
            WHERE h.metode = %s
              AND h.sesi_id = (
                  SELECT sesi_id FROM hasil_perhitungan
                  WHERE metode = %s
                  ORDER BY created_at DESC
                  LIMIT 1
              )
            ORDER BY h.ranking ASC
        """, (metode, metode), fetch=True)

        if rows:
            hasil[metode] = [
                {
                    'project_id'  : int(r['project_id']),
                    'nama_project': str(r['nama_project']),
                    'mrc'         : float(r['mrc']),
                    'sla'         : float(r['sla']),
                    'durasi'      : float(r['durasi']),
                    'ranking'     : int(r['ranking']),
                    'skor_spk'    : float(r['skor']),
                }
                for r in rows
            ]
            metode_aktif.append(metode)

    return hasil, metode_aktif


def _hitung_borda(ranking_per_metode: dict, metode_aktif: list) -> list:
    """
    Core Borda Count.
    Poin: project ranking ke-r dari N project → dapat (N - r) poin.
    Skor akhir = total_poin / max_poin × 100.
    """
    N = max(len(ranking_per_metode[m]) for m in metode_aktif)

    # Kumpulkan semua project unik
    semua_project = {}
    for metode in metode_aktif:
        for r in ranking_per_metode[metode]:
            pid = r['project_id']
            if pid not in semua_project:
                semua_project[pid] = {
                    'project_id'  : pid,
                    'nama_project': r['nama_project'],
                    'mrc'         : r['mrc'],
                    'sla'         : r['sla'],
                    'durasi'      : r['durasi'],
                }

    max_poin = (N - 1) * len(metode_aktif)   # skor teoritis tertinggi

    hasil = []
    for pid, info in semua_project.items():
        poin_per_metode    = {}
        ranking_per_project = {}

        for metode in metode_aktif:
            row = next(
                (r for r in ranking_per_metode[metode] if r['project_id'] == pid),
                None
            )
            if row:
                poin_per_metode[metode]     = N - row['ranking']
                ranking_per_project[metode] = row['ranking']
            else:
                poin_per_metode[metode]     = 0
                ranking_per_project[metode] = None

        total_poin = sum(poin_per_metode.values())
        skor_pct   = round(total_poin / max_poin * 100, 2) if max_poin > 0 else 0

        # Kategori
        if skor_pct >= 75:
            kategori = 'Sangat Layak'
        elif skor_pct >= 50:
            kategori = 'Layak'
        else:
            kategori = 'Tidak Layak'

        # Konsistensi: semakin kecil std deviasi ranking → semakin konsisten
        rankings_valid = [v for v in ranking_per_project.values() if v is not None]
        if len(rankings_valid) >= 2:
            mean_r      = sum(rankings_valid) / len(rankings_valid)
            std_r       = math.sqrt(sum((r - mean_r) ** 2 for r in rankings_valid) / len(rankings_valid))
            konsistensi = round(max(0.0, 100.0 - (std_r / N * 100)), 1)
        else:
            konsistensi = 100.0

        hasil.append({
            'project_id'        : pid,
            'nama_project'      : info['nama_project'],
            'mrc'               : info['mrc'],
            'sla'               : info['sla'],
            'durasi'            : info['durasi'],
            'skor_borda'        : skor_pct,
            'total_poin'        : total_poin,
            'max_poin'          : max_poin,
            'kategori'          : kategori,
            'konsistensi'       : konsistensi,
            'ranking_per_metode': ranking_per_project,
            'poin_per_metode'   : poin_per_metode,
        })

    hasil.sort(key=lambda x: x['skor_borda'], reverse=True)
    for i, h in enumerate(hasil):
        h['ranking_final'] = i + 1

    return hasil


def jalankan_agregasi(min_metode: int = 4):
    """
    Entry point utama. Ambil data SPK dari DB, jalankan Borda Count.

    Returns:
        (hasil, info)
    Raises:
        ValueError jika metode yang tersedia < min_metode
    """
    ranking_per_metode, metode_aktif = _ambil_ranking_terbaru()

    if len(metode_aktif) < min_metode:
        metode_kurang = [m for m in METODE_SPK if m not in metode_aktif]
        raise ValueError(
            f"Data tidak cukup. Baru ada {len(metode_aktif)} dari 4 metode. "
            f"Belum ada hasil untuk: {', '.join(metode_kurang)}. "
            f"Silakan jalankan semua metode SPK terlebih dahulu di menu Perhitungan SPK."
        )

    hasil = _hitung_borda(ranking_per_metode, metode_aktif)

    info = {
        'metode'             : 'Borda Count Rank Aggregation',
        'metode_aktif'       : metode_aktif,
        'jumlah_project'     : len(hasil),
        'jumlah_sangat_layak': sum(1 for h in hasil if h['kategori'] == 'Sangat Layak'),
        'jumlah_layak'       : sum(1 for h in hasil if h['kategori'] == 'Layak'),
        'jumlah_tidak_layak' : sum(1 for h in hasil if h['kategori'] == 'Tidak Layak'),
        'rata_konsistensi'   : round(
            sum(h['konsistensi'] for h in hasil) / len(hasil), 1
        ) if hasil else 0,
        'penjelasan': (
            'Setiap metode SPK memberikan poin Borda (N − ranking). '
            'Poin dari 4 metode dijumlahkan dan dinormalisasi ke 0–100% '
            'sebagai skor kelayakan akhir. Konsistensi menunjukkan '
            'seberapa sepakat keempat metode untuk tiap project.'
        ),
    }

    return hasil, info