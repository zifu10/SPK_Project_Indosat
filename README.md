# SPK Indosat Ooredoo Hutchison
## Sistem Pendukung Keputusan — Perpanjangan Project

---

## 📁 Struktur Project

```
spk_indosat/
│
├── app.py                  ← Entry point Flask
├── config.py               ← Konfigurasi (DB, bobot, dll)
├── requirements.txt        ← Library yang dibutuhkan
│
├── database/
│   └── schema.sql          ← Script buat tabel + data dummy
│
├── routes/                 ← Blueprint Flask (dibuat di Step 2)
│   ├── main.py             ← Halaman utama
│   ├── data.py             ← CRUD data project + upload Excel
│   ├── spk.py              ← Perhitungan 4 metode SPK
│   └── ml.py               ← Prediksi Machine Learning
│
├── utils/
│   ├── db.py               ← Koneksi & helper database
│   ├── algorithms.py       ← AHP, SAW, MOORA, WP (dibuat di Step 2)
│   └── ml_model.py         ← Decision Tree model (dibuat di Step 4)
│
├── static/
│   ├── css/
│   │   └── style.css       ← Custom CSS (dibuat di Step 3)
│   ├── js/
│   │   └── main.js         ← JavaScript (dibuat di Step 3)
│   └── img/
│       └── logo_indosat.png
│
└── templates/              ← HTML Templates (dibuat di Step 3)
    ├── base.html
    ├── index.html
    ├── data_project.html
    ├── perhitungan.html
    ├── hasil.html
    └── prediksi_ml.html
```

---

## 🚀 Cara Menjalankan

### 1. Persiapan Database
1. Buka XAMPP → Start **Apache** dan **MySQL**
2. Buka phpMyAdmin → `http://localhost/phpmyadmin`
3. Import file `database/schema.sql`

### 2. Install Library Python
```bash
pip install -r requirements.txt
```

### 3. Sesuaikan Konfigurasi
Buka `config.py`, sesuaikan:
```python
DB_PASSWORD = ''   # isi password MySQL kamu jika ada
```

### 4. Jalankan Aplikasi
```bash
python app.py
```
Buka browser: `http://localhost:5000`

---

## 📊 Kriteria & Bobot (FIXED — hasil AHP)

| Kriteria | Tipe | Bobot |
|---|---|---|
| MRC (Monthly Recurring Charge) | Benefit | 0.633 |
| SLA Availability | Cost | 0.106 |
| Contract Duration | Benefit | 0.260 |

## 🔢 Metode SPK
- **AHP** — Analytical Hierarchy Process
- **SAW** — Simple Additive Weighting
- **MOORA** — Multi-Objective Optimization on Basis of Ratio Analysis
- **WP** — Weighted Product

## 🤖 Machine Learning
- **Algoritma:** Decision Tree Classifier
- **Input:** MRC, SLA, Durasi
- **Output:** Layak / Tidak Layak + Probabilitas
