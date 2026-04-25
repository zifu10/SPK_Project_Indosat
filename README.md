# 🏢 SPK Indosat Ooredoo Hutchison

**Sistem Pendukung Keputusan — Penentuan Kelayakan Perpanjangan Project**

Aplikasi web berbasis Flask untuk membantu PT Indosat Ooredoo Hutchison dalam menentukan project mana yang layak diperpanjang kontraknya, menggunakan 4 metode MCDM dan Machine Learning.

---

## ✨ Fitur Utama

- 📤 **Upload data project** via file Excel (.xlsx/.xls) dengan preview sebelum disimpan
- ✏️ **Edit data inline** langsung dari tabel tanpa perlu form terpisah
- 🧮 **4 Metode SPK** — AHP, SAW, MOORA, Weighted Product
- 🤖 **Prediksi Machine Learning** — Decision Tree Classifier
- 📊 **Dashboard** dengan ringkasan data dan kriteria bobot

---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Backend | Python + Flask |
| Database | MySQL (via XAMPP) |
| Frontend | HTML + Bootstrap 5 + Vanilla JS |
| Machine Learning | scikit-learn (Decision Tree) |
| Excel Parsing | pandas + openpyxl |

---

## ⚙️ Cara Menjalankan

### Prasyarat
- Python 3.10+
- XAMPP (Apache + MySQL)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/username/spk-indosat.git
cd spk-indosat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
1. Buka XAMPP → klik **Start** pada Apache dan MySQL
2. Buka browser → `http://localhost/phpmyadmin`
3. Buat database baru bernama `spk_indosat`
4. Pilih database tersebut → tab **Import** → pilih file `database/schema.sql` → klik **Go**

### 4. Konfigurasi
Buka file `config.py` dan sesuaikan:
```python
DB_HOST     = 'localhost'
DB_USER     = 'root'
DB_PASSWORD = ''        # isi jika MySQL kamu menggunakan password
DB_NAME     = 'spk_indosat'
```

### 5. Jalankan Aplikasi
```bash
python app.py
```
Buka browser: **http://localhost:5000**

---

## 🗂️ Struktur Project

```
SPK_Project_Indosat/
│
├── app.py                  ← Entry point, register semua blueprint
├── config.py               ← Konfigurasi DB, bobot kriteria (FIXED)
├── requirements.txt        ← Daftar library Python
│
├── database/
│   └── schema.sql          ← Script DDL tabel + 10 data dummy
│
├── routes/                 ← Flask Blueprint (URL handler)
│   ├── main.py             ← Route dashboard (/)
│   ├── data.py             ← CRUD project + upload Excel (/data)
│   ├── spk.py              ← Perhitungan 4 metode SPK (/spk)
│   └── ml.py               ← Prediksi Machine Learning (/ml)
│
├── utils/                  ← Modul helper
│   ├── db.py               ← Koneksi MySQL + query helper
│   ├── algorithms.py       ← Implementasi AHP, SAW, MOORA, WP
│   └── ml_model.py         ← Decision Tree training + prediksi
│
├── static/
│   ├── css/style.css       ← Semua styling (Indosat color palette)
│   ├── js/main.js          ← Utility JS global (toast, format)
│   └── img/logo_indosat.png
│
└── templates/              ← Jinja2 HTML templates
    ├── base.html           ← Layout utama (sidebar + topbar)
    ├── index.html          ← Dashboard
    ├── data_project.html   ← Manajemen data project
    ├── perhitungan.html    ← Perhitungan & hasil SPK
    └── prediksi_ml.html    ← Prediksi Machine Learning
```

---

## 📊 Kriteria & Bobot

Bobot dihitung menggunakan metode AHP dengan **CR = 0.0532** (konsisten, CR < 0.1).

| Kriteria | Keterangan | Tipe | Bobot |
|---|---|---|---|
| MRC | Monthly Recurring Charge | Benefit | **0.633** |
| SLA | SLA Availability | Cost | **0.106** |
| Durasi | Contract Duration | Benefit | **0.260** |

> ⚠️ Bobot bersifat **FIXED** dan tidak dapat diubah melalui antarmuka. Untuk mengubah bobot, edit langsung di `config.py`.

---

## 🔢 Metode SPK

| Metode | Kepanjangan | Cara Kerja |
|---|---|---|
| **AHP** | Analytical Hierarchy Process | Skor sub-kriteria × bobot, skala ordinal |
| **SAW** | Simple Additive Weighting | Normalisasi benefit/cost, weighted sum |
| **MOORA** | Multi-Objective Optimization on Basis of Ratio Analysis | Normalisasi rasio akar kuadrat, Yi = benefit − cost |
| **WP** | Weighted Product | Si = Π(xij^wj), cost pakai pangkat negatif |

---

## 🤖 Machine Learning

- **Algoritma:** Decision Tree Classifier (scikit-learn)
- **Fitur input:** MRC, SLA Availability, Contract Duration
- **Output:** `Layak` / `Tidak Layak` + nilai probabilitas
- **Labeling:** Otomatis berdasarkan skor SAW — project dengan skor ≥ median diklasifikasikan sebagai *Layak*
- **Catatan:** Model dilatih ulang setiap kali prediksi dijalankan menggunakan data terkini di database

---

## 📋 Format Excel Upload

File Excel harus memiliki kolom berikut (nama kolom tidak case-sensitive):

| Kolom | Keterangan | Contoh |
|---|---|---|
| `Nama_Project` | Nama project/client | Project Alpha - PT Telkom |
| `MRC` | Monthly Recurring Charge dalam juta Rp | 450 |
| `SLA` | SLA Availability dalam persen | 99.5 |
| `Durasi` | Contract Duration dalam tahun | 6 |

Download template Excel tersedia langsung di halaman **Data Project**.

---

## 👥 Tim Pengembang

**Kelompok 4 — Sistem Pendukung Keputusan**

| Nama | NIM |
|---|---|
| Zaid Ilman Faqih Umar | 235150400111031 |
| Erwin Trimulya Purwono | 235150401111035 |
| Stephanie Gabriella Wijaya | 235150401111032 |
| M Brillian Rabbani | 235150407111044 |

---

## 📄 Lisensi

Project ini dibuat untuk keperluan akademik mata kuliah Sistem Pendukung Keputusan.