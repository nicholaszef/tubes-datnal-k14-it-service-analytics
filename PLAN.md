# PLAN - Kelompok 14: IT Service Analytics (OSEMN)

> Ghazy Achmed Movlech Urbayani - 18223093 - Preprocessing Lead  
> M Azizdzaki Khrisnanurmuflih - 18223128 - Visualization Developer  
> Daffa - Modeler  
> Adam - Documentation Lead  
> Nicholas - Data Engineer  

---

## Status Keseluruhan (per 14 Juni 2026 — update terakhir)

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
- [x] Visualisasi distribusi severity dan priority → `viz1_distribusi_severity_priority.png`
- [x] Visualisasi tren waktu volume dan durasi DS2 → `viz2_tren_waktu_ds2.png`
- [x] Visualisasi perbandingan SLA violated per issue_type → `viz3_sla_violated_per_type.png`
- [x] Visualisasi Spearman heatmap DS2 + DS1 → `viz4_heatmap_korelasi_ds2.png`, `viz4b_heatmap_korelasi_ds1.png`
- [x] Interpretasi markdown untuk viz1–viz4 di `03_explore.ipynb`

### Bagian Aziz (viz lanjutan + interpretasi)

- [x] Viz 5 (viz5): distribusi durasi resolusi + boxplot per priority DS1
- [x] Viz 6 (viz6): rata-rata durasi resolusi per kategori `FiledAgainst` DS1
- [x] Viz 7 (viz7): satisfaction vs severity heatmap DS1
- [x] Viz 8 (viz8): kecepatan resolusi per issue_type DS2
- [x] Viz 9 (viz9): re-open rate per issue_type DS2 (PA-4, eskalasi & kegagalan resolusi pertama)
- [x] Interpretasi markdown tajam untuk semua Viz (5–9) di `03_explore.ipynb`
- [x] Catatan limitasi tren satisfaction (DS1 tidak punya timestamp) di `03_explore.ipynb`
- [x] Rekomendasi slide di sel penutup `03_explore.ipynb`
- [x] Figures viz5–viz9 di `reports/figures/` (format berurutan viz1_…viz9_)
- [x] Semua nama file PNG diubah ke format berurutan (viz1_ s/d viz9_)
- [x] Tabel temuan No. 7–10 diisi dengan nilai aktual dari data (di `PREPROCESSING_EXPLORE_PLAN.md` dan `scrub_explore_summary.md`)
- [x] `git add` + `git commit` + `git push` (dilakukan Aziz sendiri)

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
