# Ringkasan Scrub & Explore
## Kelompok 14 — II4013 Data Analitik

Berikut adalah daftar lengkap seluruh aktivitas pra-pemrosesan dan eksplorasi data yang telah dilakukan:

### 1. Load & Verifikasi Dataset
- **Load Enam Dataset Utama** (IBM Watson & 5 File Mendeley Help Desk)
- **Verifikasi Struktur Awal** (Cek Baris, Kolom, Tipe Data, & Copy Immutable)

### 2. Analisis Diagnostik Awal
- **EDA Deskriptif Distribusi** (Statistik Deskriptif Numerik & Value Counts Kategori)
- **Analisis Mekanisme Missing Value** (Klasifikasi MCAR, MAR, & MNAR per Kolom)

### 3. Pembersihan Data (Scrubbing)
- **Hapus Duplikasi Baris** (Drop Duplicates pada DS1 & Utama DS2)
- **Standardisasi Teks Kategorikal** (Lowercase & Trim Whitespace Kolom Teks)
- **Imputasi Missing Value Terarah** (Nilai Unknown untuk MAR & Drop Kolom MNAR >95%)
- **Konversi Tipe Datetime Terstandar** (Parsing Timestamp ke UTC & Hitung Durasi dalam Jam)
- **Pembersihan Teks Utterances** (Regex Cleaning, Hitung Kata, & Filter Teks Pendek)
- **Penanganan Outlier Nilai Ekstrim** (Capping Nilai Maksimal P99 & Deteksi Tiket Kompleks)

### 4. Rekayasa Fitur Baru (Feature Engineering)
- **Ekstraksi Fitur Baru DS1** (Split Kategori Severity, Priority, Seniority, & Satisfaction)
- **Ekstraksi Fitur Baru DS2** (Normalisasi Prioritas, Binning Kecepatan, & Composite Score)

### 5. Integrasi & Ekspor Data
- **Integrasi Data & Enrichment** (Aggregasi Utterances & Scored ke Tabel Utama DS2)
- **Export Data Bersih Terstandar** (Simpan 5 File CSV Clean ke data/processed/)

### 6. Eksplorasi Data Lanjutan (Explore)
- **Visualisasi Distribusi Keparahan** (Bar Chart Grouped Severity vs Priority)
- **Analisis Tren Waktu Resolusi** (Line Chart Dual-Axis Volume & Durasi per Bulan)
- **Analisis Pelanggaran SLA Kategori** (Horizontal Bar Chart SLA Violated per Kategori)
- **Analisis Korelasi Hubungan Fitur** (Spearman Heatmap & Hubungan Kepuasan)
- **Penyusunan Ringkasan & Handoff Modeler** (Tabel Masalah Data, Fitur Baru, & Handoff Modeler)

---
*Laporan detail interaktif tersedia di [02_scrub.ipynb](file:///Users/ghazy/Ghazy/tubes-datnal-k14-it-service-analytics/notebooks/02_scrub.ipynb) dan [03_explore.ipynb](file:///Users/ghazy/Ghazy/tubes-datnal-k14-it-service-analytics/notebooks/03_explore.ipynb).*
*Visualisasi grafik tersimpan di [figures/](file:///Users/ghazy/Ghazy/tubes-datnal-k14-it-service-analytics/reports/figures/).*