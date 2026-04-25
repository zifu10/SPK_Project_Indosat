-- ============================================================
-- DATABASE SCHEMA: SPK Indosat Ooredoo Hutchison
-- Sistem Pendukung Keputusan - Perpanjangan Project
-- ============================================================

CREATE DATABASE IF NOT EXISTS spk_indosat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE spk_indosat;

-- ------------------------------------------------------------
-- TABLE: projects
-- Menyimpan data project yang akan dievaluasi
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nama_project    VARCHAR(255)    NOT NULL COMMENT 'Nama project/client',
    mrc             DECIMAL(15,2)   NOT NULL COMMENT 'Monthly Recurring Charge dalam juta rupiah',
    sla             DECIMAL(5,2)    NOT NULL COMMENT 'SLA Availability dalam persen (0-100)',
    durasi          DECIMAL(5,2)    NOT NULL COMMENT 'Contract Duration dalam tahun',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Validasi nilai
    CONSTRAINT chk_mrc     CHECK (mrc > 0),
    CONSTRAINT chk_sla     CHECK (sla >= 0 AND sla <= 100),
    CONSTRAINT chk_durasi  CHECK (durasi > 0)
) ENGINE=InnoDB COMMENT='Data project Indosat yang akan dievaluasi kelayakan perpanjangannya';

-- ------------------------------------------------------------
-- TABLE: hasil_perhitungan
-- Menyimpan hasil ranking dari setiap metode SPK
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS hasil_perhitungan (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sesi_id         VARCHAR(36)     NOT NULL COMMENT 'UUID sesi perhitungan (satu kali run)',
    metode          ENUM('AHP','SAW','MOORA','WP') NOT NULL COMMENT 'Metode SPK yang digunakan',
    project_id      INT             NOT NULL COMMENT 'Referensi ke tabel projects',
    skor            DECIMAL(10,6)   NOT NULL COMMENT 'Skor akhir hasil perhitungan',
    ranking         INT             NOT NULL COMMENT 'Urutan ranking (1 = terbaik)',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_sesi   (sesi_id),
    INDEX idx_metode (metode)
) ENGINE=InnoDB COMMENT='Hasil perhitungan SPK per sesi dan per metode';

-- ------------------------------------------------------------
-- TABLE: detail_normalisasi
-- Menyimpan nilai normalisasi per kriteria (untuk transparansi proses)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detail_normalisasi (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sesi_id         VARCHAR(36)     NOT NULL,
    metode          ENUM('AHP','SAW','MOORA','WP') NOT NULL,
    project_id      INT             NOT NULL,
    nilai_mrc_norm  DECIMAL(10,6)   COMMENT 'Nilai MRC setelah normalisasi',
    nilai_sla_norm  DECIMAL(10,6)   COMMENT 'Nilai SLA setelah normalisasi',
    nilai_dur_norm  DECIMAL(10,6)   COMMENT 'Nilai Durasi setelah normalisasi',
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_sesi_metode (sesi_id, metode)
) ENGINE=InnoDB COMMENT='Detail nilai normalisasi tiap kriteria per metode';

-- ------------------------------------------------------------
-- TABLE: prediksi_ml
-- Menyimpan hasil prediksi Machine Learning
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prediksi_ml (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sesi_id         VARCHAR(36)     NOT NULL,
    project_id      INT             NOT NULL,
    prediksi        ENUM('Layak','Tidak Layak') NOT NULL COMMENT 'Hasil prediksi Decision Tree',
    probabilitas    DECIMAL(5,4)    NOT NULL COMMENT 'Probabilitas confidence (0-1)',
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_sesi (sesi_id)
) ENGINE=InnoDB COMMENT='Hasil prediksi ML (Decision Tree) per sesi';

-- ------------------------------------------------------------
-- DATA DUMMY: 10 project contoh untuk testing
-- ------------------------------------------------------------
INSERT INTO projects (nama_project, mrc, sla, durasi) VALUES
    ('Project Alpha - PT Telkom',       450.00, 99.5, 6.0),
    ('Project Beta - Bank BRI',         280.00, 98.2, 4.0),
    ('Project Gamma - Pertamina',       85.00,  97.5, 2.0),
    ('Project Delta - PLN',             320.00, 99.8, 5.5),
    ('Project Epsilon - BNI',           150.00, 96.5, 3.0),
    ('Project Zeta - Mandiri',          500.00, 99.9, 7.0),
    ('Project Eta - Garuda Indonesia',  75.00,  95.0, 1.5),
    ('Project Theta - XL Axiata',       210.00, 98.7, 4.5),
    ('Project Iota - Smartfren',        95.00,  97.0, 2.5),
    ('Project Kappa - Grab Indonesia',  380.00, 99.1, 5.0);
