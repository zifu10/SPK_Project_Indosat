# ============================================================
# routes/data.py — Manajemen Data Project (CRUD + Upload Excel)
# ============================================================

import pandas as pd
from flask import Blueprint, render_template, request, jsonify
from utils.db import (
    get_all_projects,insert_projects_bulk, update_project,
    delete_project, clear_all_projects, execute_query
)

data_bp = Blueprint('data', __name__)


# ------------------------------------------------------------
# GET /data — Halaman tabel data project
# ------------------------------------------------------------
@data_bp.route('/')
def index():
    projects = get_all_projects()
    return render_template('data_project.html', projects=projects)


# ------------------------------------------------------------
# POST /data/upload — Upload file Excel
# ------------------------------------------------------------
@data_bp.route('/upload', methods=['POST'])
def upload_excel():
    """
    Menerima file Excel, parsing, validasi, kembalikan preview JSON.
    Belum disimpan ke DB — user konfirmasi dulu lewat /data/simpan.
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'File tidak ditemukan'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'}), 400

    allowed = {'xlsx', 'xls'}
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in allowed:
        return jsonify({'success': False, 'message': 'Format file harus .xlsx atau .xls'}), 400

    try:
        df = pd.read_excel(file)

        # Normalisasi nama kolom (case-insensitive, strip spasi)
        df.columns = [str(c).strip().lower() for c in df.columns]

        # Mapping nama kolom yang mungkin dipakai user
        col_map = {
            'nama_project': ['nama_project', 'nama project', 'project', 'nama'],
            'mrc':          ['mrc', 'monthly recurring charge', 'monthly_recurring_charge'],
            'sla':          ['sla', 'sla availability', 'sla_availability'],
            'durasi':       ['durasi', 'duration', 'contract duration', 'contract_duration'],
        }

        rename = {}
        for target, candidates in col_map.items():
            for c in candidates:
                if c in df.columns:
                    rename[c] = target
                    break

        df = df.rename(columns=rename)

        required = ['nama_project', 'mrc', 'sla', 'durasi']
        missing  = [c for c in required if c not in df.columns]

        if missing:
            return jsonify({
                'success': False,
                'message': f'Kolom tidak ditemukan: {", ".join(missing)}. '
                           f'Pastikan Excel memiliki kolom: Nama_Project, MRC, SLA, Durasi'
            }), 400

        # Validasi dan konversi tipe data
        errors  = []
        preview = []

        for idx, row in df.iterrows():
            row_num = idx + 2  # +2 karena header di baris 1

            try:
                nama   = str(row['nama_project']).strip()
                mrc    = float(row['mrc'])
                sla    = float(row['sla'])
                durasi = float(row['durasi'])
            except (ValueError, TypeError):
                errors.append(f'Baris {row_num}: nilai tidak valid (harus angka)')
                continue

            # Validasi range
            row_errors = []
            if not nama:
                row_errors.append('nama project kosong')
            if mrc <= 0:
                row_errors.append(f'MRC harus > 0 (dapat: {mrc})')
            if not (0 <= sla <= 100):
                row_errors.append(f'SLA harus 0-100% (dapat: {sla})')
            if durasi <= 0:
                row_errors.append(f'Durasi harus > 0 (dapat: {durasi})')

            if row_errors:
                errors.append(f'Baris {row_num} ({nama}): {", ".join(row_errors)}')
            else:
                preview.append({
                    'nama_project': nama,
                    'mrc':          mrc,
                    'sla':          sla,
                    'durasi':       durasi,
                })

        if not preview:
            return jsonify({
                'success': False,
                'message': 'Tidak ada data valid yang bisa diproses.',
                'errors':  errors
            }), 400

        return jsonify({
            'success':  True,
            'message':  f'{len(preview)} data berhasil dibaca.',
            'preview':  preview,
            'errors':   errors,   # baris yang bermasalah (jika ada)
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error membaca file: {str(e)}'}), 500


# ------------------------------------------------------------
# POST /data/simpan — Simpan data dari preview ke database
# ------------------------------------------------------------
@data_bp.route('/simpan', methods=['POST'])
def simpan_data():
    """
    Menerima data JSON (hasil edit preview), simpan ke database.
    """
    data = request.get_json()

    if not data or 'projects' not in data:
        return jsonify({'success': False, 'message': 'Data tidak valid'}), 400

    projects = data['projects']

    if not projects:
        return jsonify({'success': False, 'message': 'Data project kosong'}), 400

    # Validasi ulang sebelum insert
    for p in projects:
        try:
            float(p['mrc'])
            float(p['sla'])
            float(p['durasi'])
        except (ValueError, KeyError):
            return jsonify({'success': False, 'message': 'Format data tidak valid'}), 400

    mode = data.get('mode', 'tambah')  # 'tambah' atau 'ganti'

    if mode == 'ganti':
        clear_all_projects()

    success = insert_projects_bulk(projects)

    if success:
        return jsonify({
            'success': True,
            'message': f'{len(projects)} project berhasil disimpan.'
        })
    else:
        return jsonify({'success': False, 'message': 'Gagal menyimpan ke database'}), 500


# ------------------------------------------------------------
# PUT /data/update/<id> — Update satu project (inline edit)
# ------------------------------------------------------------
@data_bp.route('/update/<int:project_id>', methods=['PUT'])
def update(project_id):
    data = request.get_json()

    try:
        nama   = str(data['nama_project']).strip()
        mrc    = float(data['mrc'])
        sla    = float(data['sla'])
        durasi = float(data['durasi'])
    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'message': f'Data tidak valid: {e}'}), 400

    # Validasi
    if not nama:
        return jsonify({'success': False, 'message': 'Nama project tidak boleh kosong'}), 400
    if mrc <= 0:
        return jsonify({'success': False, 'message': 'MRC harus lebih dari 0'}), 400
    if not (0 <= sla <= 100):
        return jsonify({'success': False, 'message': 'SLA harus antara 0 dan 100'}), 400
    if durasi <= 0:
        return jsonify({'success': False, 'message': 'Durasi harus lebih dari 0'}), 400

    result = update_project(project_id, nama, mrc, sla, durasi)

    if result is not None:
        return jsonify({'success': True, 'message': 'Project berhasil diupdate'})
    else:
        return jsonify({'success': False, 'message': 'Gagal mengupdate project'}), 500


# ------------------------------------------------------------
# DELETE /data/hapus/<id> — Hapus satu project
# ------------------------------------------------------------
@data_bp.route('/hapus/<int:project_id>', methods=['DELETE'])
def hapus(project_id):
    result = delete_project(project_id)

    if result is not None:
        return jsonify({'success': True, 'message': 'Project berhasil dihapus'})
    else:
        return jsonify({'success': False, 'message': 'Gagal menghapus project'}), 500


# ------------------------------------------------------------
# DELETE /data/hapus-semua — Hapus semua project
# ------------------------------------------------------------
@data_bp.route('/hapus-semua', methods=['DELETE'])
def hapus_semua():
    result = clear_all_projects()

    if result is not None:
        return jsonify({'success': True, 'message': 'Semua project berhasil dihapus'})
    else:
        return jsonify({'success': False, 'message': 'Gagal menghapus semua project'}), 500


# ------------------------------------------------------------
# POST /data/tambah — Tambah satu project manual
# ------------------------------------------------------------
@data_bp.route('/tambah', methods=['POST'])
def tambah():
    data = request.get_json()

    try:
        nama   = str(data['nama_project']).strip()
        mrc    = float(data['mrc'])
        sla    = float(data['sla'])
        durasi = float(data['durasi'])
    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'message': f'Data tidak valid: {e}'}), 400

    if not nama:
        return jsonify({'success': False, 'message': 'Nama project tidak boleh kosong'}), 400

    result = insert_projects_bulk([{
        'nama_project': nama,
        'mrc':          mrc,
        'sla':          sla,
        'durasi':       durasi
    }])

    if result:
        return jsonify({'success': True, 'message': 'Project berhasil ditambahkan'})
    else:
        return jsonify({'success': False, 'message': 'Gagal menambahkan project'}), 500


# ------------------------------------------------------------
# GET /data/list — API: ambil semua project sebagai JSON
# ------------------------------------------------------------
@data_bp.route('/list', methods=['GET'])
def list_projects():
    projects = get_all_projects()
    cleaned = []
    for p in projects:
        cleaned.append({
            'id':           int(p['id']),
            'nama_project': str(p['nama_project']),
            'mrc':          float(p['mrc']),
            'sla':          float(p['sla']),
            'durasi':       float(p['durasi']),
            'created_at':   str(p['created_at']) if p.get('created_at') else '',
            'updated_at':   str(p['updated_at']) if p.get('updated_at') else '',
        })
    return jsonify({'success': True, 'data': cleaned})
