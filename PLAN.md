# PLAN - Kelompok 14: IT Service Analytics (OSEMN)

> Ghazy Achmed Movlech Urbayani - 18223093 - Preprocessing Lead  
> M Azizdzaki Khrisnanurmuflih - 18223128 - Visualization Developer  
> Daffa - Modeler  
> Adam - Documentation Lead  
> Nicholas - Data Engineer  

---

## Status Keseluruhan (per 13 Juni 2026)

| Fase OSEMN | PIC | Status |
|---|---|---|
| O - Obtain | Nicholas | SELESAI |
| S - Scrub | Ghazy | SELESAI |
| E - Explore (statistik + viz dasar) | Ghazy | SELESAI |
| E - Explore (viz lanjutan + interpretasi) | Aziz | SELESAI |
| M - Model | Daffa | BELUM DIMULAI |
| N - iNterpret | Aziz + Daffa + Adam | MENUNGGU Model selesai |

---

## O - Obtain

- [x] Raw dataset tersedia di `data/raw/` (Nicholas)
- [x] DS1: `WA_Fn-UseC_-IT-Help-Desk.csv` - 100.000 baris, 10 kolom
- [x] DS2: `issues.csv`, `issues_change_history.csv`, `issues_snapshot.csv`, `issues_snapshot_sample.xlsx`, `sample_utterances.csv`

---

## S - Scrub

- [x] EDA diagnostik: distribusi, missing, outlier, class imbalance
- [x] Handle missing value per kolom sesuai pola MCAR/MAR/MNAR
- [x] Handle duplikasi
- [x] Standarisasi tipe data dan format
- [x] Handle outlier (cap P99 + flag)
- [x] Feature engineering DS1: 10 fitur baru
- [x] Feature engineering DS2: 12 fitur baru
- [x] Integrasi dataset (Opsi B+C: terpisah + enriched via issueId)
- [x] Simpan 5 file clean ke `data/processed/`
- [x] Notebook scrub reproducible: `02_scrub.ipynb`

---

## E - Explore

### Bagian Ghazy (statistik + viz dasar)

- [x] Statistik deskriptif variabel utama DS1 dan DS2
- [x] Visualisasi distribusi severity dan priority (8B)
- [x] Visualisasi tren waktu volume dan durasi DS2 (8C)
- [x] Visualisasi perbandingan SLA violated per issue_type (8D)
- [x] Visualisasi Spearman heatmap DS1 dan DS2 (8E)
- [x] Interpretasi markdown untuk 8B, 8C, 8D, 8E di `03_explore.ipynb`

### Bagian Aziz (viz lanjutan + interpretasi)

- [x] Viz A: distribusi durasi resolusi + boxplot per priority DS1
- [x] Viz B: rata-rata durasi resolusi per kategori `FiledAgainst` DS1
- [x] Viz C: satisfaction vs severity heatmap DS1
- [x] Viz D: kecepatan resolusi per issue_type DS2
- [x] Interpretasi markdown tajam untuk Viz A, B, C, D di `03_explore.ipynb`
- [x] Rekomendasi slide di sel penutup `03_explore.ipynb`
- [ ] **PENDING:** Jalankan `03_explore.ipynb` (Kernel > Restart & Run All) untuk generate output dan figures
- [ ] **PENDING:** Isi tabel temuan No. 7-10 di `03_explore.ipynb` dengan hasil aktual setelah notebook dijalankan
- [ ] **PENDING:** `git add` + `git commit` + `git push` (dilakukan Aziz sendiri)

---

## M - Model

- [ ] Klasifikasi prioritas tiket DS1 (target: `priorityLabel`) - Daffa
- [ ] Clustering tiket berdasarkan pola durasi dan kompleksitas - Daffa
- [ ] Model NLP pada `ds2UtterancesClean.csv` - Daffa
- [ ] Evaluasi model - Daffa
- [ ] Notebook model: `04_model.ipynb`

**Catatan untuk Daffa:**
- SMOTE hanya pada `X_train`, bukan seluruh dataset
- Gunakan `resolutionDurationHours` (bukan `totalTimeHours` - hampir redundan)
- Target DS1: `priorityLabel` (bukan `severityLabel` - terlalu imbalanced)
- `ds2ScoredClean.csv` hanya 747 baris (n=360 valid) - terlalu kecil untuk supervised

---

## N - iNterpret

- [ ] Interpretasi hasil model dikaitkan ke PA-1 s/d PA-5 - Aziz + Daffa + Adam
- [ ] Visualisasi hasil model - Aziz
- [ ] Notebook interpret: `05_interpret.ipynb`

---

## Laporan dan Presentasi

- [ ] Laporan akhir PDF (struktur OSEMN) - Adam
- [ ] Slide presentasi - Adam
- [ ] Video presentasi/demo - Semua

---

## Pertanyaan Analitik Kelompok (PA-1 s/d PA-5)

| Kode | Pertanyaan | Dataset |
|---|---|---|
| PA-1 | Faktor apa yang paling mempengaruhi durasi resolusi tiket IT? | DS1 + DS2 |
| PA-2 | Kategori atau tipe tiket mana yang paling berisiko melanggar SLA? | DS1 + DS2 |
| PA-3 | Bagaimana keparahan insiden mempengaruhi kepuasan pengguna? | DS1 |
| PA-4 | Apakah prioritas tiket konsisten dengan keparahan aktual? | DS1 |
| PA-5 | Tipe tiket apa yang menunjukkan performa resolusi terbaik vs terburuk? | DS2 |
