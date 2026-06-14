# PLAN - Kelompok 14: IT Service Analytics (OSEMN)

> Ghazy Achmed Movlech Urbayani - 18223093 - Preprocessing Lead  
> M Azizdzaki Khrisnanurmuflih - 18223128 - Visualization Developer  
> Aziz - Modeler (mengambil alih dari Daffa)  
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
| M - Model | Aziz | IMPLEMENTASI SELESAI — 3 model (RF+DT klasifikasi, K-Means clustering, LDA NLP), semua PKL tersimpan di reports/models/ |
| N - iNterpret | Aziz + Adam | MENUNGGU — semua artefak model tersedia di reports/models/ |

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

> **PIC:** M Azizdzaki Khrisnanurmuflih (18223128)  
> **File kerja:** `notebooks/04_model.ipynb`  
> **Input:** file clean di `data/processed/` (lihat tabel di bawah)  
> **Target rubrik skor 4:** minimal 2 model berbeda, preprocessing lengkap, evaluasi metrik (accuracy/F1/silhouette), interpretasi hasil dikaitkan ke PA-1 s/d PA-5

### Input Dataset yang Tersedia

| File | Baris | Kolom | Digunakan untuk |
|------|-------|-------|-----------------|
| `ds1Clean.csv` | 100.000 | 22 | Klasifikasi priority + regresi durasi |
| `ds2IssuesClean.csv` | 66.691 | 57 | Clustering + klasifikasi speed |
| `ds2UtterancesClean.csv` | 14.455 | 12 | NLP/topic modeling |
| `ds2ScoredClean.csv` | 747 | 21 | Validasi saja (n=360 valid score) |
| `ds2SnapshotClean.csv` | 90.904 | 45 | Opsional — per-assignee analysis |

**Path yang benar di notebook:**
```python
DS1_PATH       = '../data/processed/ds1Clean.csv'
DS2_PATH       = '../data/processed/ds2IssuesClean.csv'
UTT_PATH       = '../data/processed/ds2UtterancesClean.csv'
SCORED_PATH    = '../data/processed/ds2ScoredClean.csv'
FIGURES_DIR    = '../reports/figures/'
```

### Checklist Tugas Aziz (M-Model) — SELESAI

**Model 1 — Klasifikasi Prioritas Tiket DS1 (PA-1, PA-4)**
- [x] Fitur: `severityLevel`, `seniorityLevel`, `resolutionDurationDays`, `isLongTicket`, `isHighPriority`, `FiledAgainst`, `TicketType`
- [x] Target: `priorityLabel` (4 kelas: high/medium/low/unassigned)
- [x] Split: `train_test_split` stratified (test_size=0.2, random_state=42)
- [x] Handle imbalance: SMOTE **hanya pada X_train** — X_train: 80.000 → 116.792 setelah SMOTE
- [x] 2 algoritma dibandingkan: Random Forest (acc=0.6493) + Decision Tree (acc=0.6504)
- [x] Evaluasi: classification_report (precision/recall/F1 per kelas), confusion matrix, accuracy
- [x] Simpan confusion matrix → `reports/figures/viz10_confusion_matrix_ds1.png`
- [x] Simpan feature importance → `reports/figures/viz11_feature_importance_ds1.png`
- [x] Model disimpan → `reports/models/rf_priority_ds1.pkl`, `dt_priority_ds1.pkl`

**Model 2 — Clustering Tiket DS2 (PA-2, PA-5)**
- [x] Fitur: `resolutionDurationHours`, `processing_steps`, `issue_comments_count`, `isComplex`, `timePerStepHours`, `wfe_reopened`
- [x] Preprocessing: StandardScaler sebelum K-Means
- [x] k optimal: k=5 dipilih otomatis dari silhouette tertinggi (0.5903) pada k=2–8
- [x] Evaluasi: silhouette score=0.5903, profil tiap cluster (avg durasi, % SLA, steps)
- [x] Simpan elbow + silhouette → `reports/figures/viz12_elbow_cluster.png`
- [x] Simpan profil cluster → `reports/figures/viz13_cluster_profile_ds2.png`
- [x] Model disimpan → `reports/models/kmeans_ds2.pkl`, `scaler_ds2.pkl`
- [x] Output cluster disimpan → `reports/models/ds2_with_clusters.csv`

**Model 3 — NLP Topic Modeling DS2 Utterances (opsional)**
- [x] Input: kolom `messageClean` dari `ds2UtterancesClean.csv` (14.455 teks)
- [x] LDA topic modeling — 6 topik teridentifikasi
- [x] Simpan distribusi topik → `reports/figures/viz14_topic_distribution_nlp.png`
- [x] Model disimpan → `reports/models/lda_utterances_ds2.pkl`, `tfidf_utterances_ds2.pkl`

**Evaluasi & Interpretasi**
- [x] Tabel perbandingan semua model dengan nilai aktual (di `04_model.ipynb`)
- [x] Interpretasi setiap model dikaitkan ke PA-1 s/d PA-5
- [x] Laporan Sementara M-Model di akhir notebook (7 temuan + profil 5 cluster + handoff)
- [ ] `git add + git commit + git push` (Aziz lakukan sendiri)

### Peringatan & Batasan Data (dari Ghazy + Aziz)

| Isu | Detail | Tindakan yang Disarankan |
|-----|--------|--------------------------|
| DS1 severity imbalanced | `severityLabel` "normal" 90.9% | Jangan pakai severityLabel sebagai target — pakai `priorityLabel` |
| SMOTE hanya training | Data leakage jika SMOTE sebelum split | SMOTE setelah split, hanya pada X_train |
| totalTimeHours redundan | r ≈ 1.0 dengan resolutionDurationHours | Drop `totalTimeHours` dari fitur model |
| DS2 priority 50.9% unknown | `priorityNormalized` lebih bersih | Gunakan `priorityNormalized` bukan kolom priority asli |
| Scored sample kecil | ds2ScoredClean hanya 360 valid score | Jangan pakai untuk supervised — gunakan untuk validasi saja |
| performanceBinary 99.5% NaN | Tidak layak sebagai target supervised | Abaikan `performanceBinary` sebagai target |
| DS1 tidak punya timestamp | Tidak bisa analisis tren waktu | Gunakan `resolutionDurationDays` sebagai proxy waktu |

---

## N - iNterpret

- [ ] Interpretasi hasil model dikaitkan ke PA-1 s/d PA-5 - Aziz + Adam
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
