# Ringkasan S-Scrub, E-Explore, M-Model & N-iNterpret
## Kelompok 14 — II4013 Data Analitik ITB
### Topik 14: Kinerja Layanan TI Organisasi (IT Service Performance Analytics)

> **PIC:** Ghazy Achmed Movlech Urbayani (18223093) — S-Scrub + E-Explore dasar  
> **PIC:** M Azizdzaki Khrisnanurmuflih (18223128) — E-Explore lanjutan + Visualisasi tambahan + M-Model + N-iNterpret  
> **Status keseluruhan:** S-Scrub [SELESAI] | E-Explore [SELESAI] | M-Model [SELESAI] | N-iNterpret [SELESAI]  
> **Terakhir diperbarui:** 14 Juni 2026

---

## Pertanyaan Analitik Kelompok (Benang Merah EDA)

| Kode | Pertanyaan Analitik | Dataset |
|------|---------------------|---------|
| PA-1 | Faktor apa yang paling mempengaruhi durasi resolusi tiket IT? | DS1 + DS2 |
| PA-2 | Kategori atau tipe tiket mana yang paling berisiko melanggar SLA? | DS1 + DS2 |
| PA-3 | Bagaimana keparahan insiden (severity) mempengaruhi kepuasan pengguna? | DS1 |
| PA-4 | Apakah prioritas tiket yang ditetapkan konsisten dengan keparahan aktual insiden? | DS1 |
| PA-5 | Tipe tiket apa yang menunjukkan performa resolusi terbaik vs terburuk? | DS2 |

---

## 1. Load & Verifikasi Dataset [SELESAI]

- **Load 6 Dataset Utama** — IBM Watson DS1 + 5 file Mendeley Help Desk DS2
- **Verifikasi Struktur Awal** — cek baris, kolom, tipe data, dan copy immutable

| File | Baris | Kolom | Keterangan |
|------|-------|-------|------------|
| `WA_Fn-UseC_-IT-Help-Desk.csv` | 100.000 | 10 | DS1, 0% missing, simulasi |
| `issues.csv` | 66.691 | 57 | DS2 backbone |
| `issues_change_history.csv` | — | — | Referensi join |
| `issues_snapshot.csv` | 90.963 | 45 | Per-assignee, desain |
| `issues_snapshot_sample.xlsx` | 747 | 21 | Ground truth Q1/Q2/Q3 |
| `sample_utterances.csv` | 14.455 | 12 | NLP source |

---

## 2. Analisis Diagnostik Awal [SELESAI]

- **EDA Deskriptif** — statistik deskriptif numerik (mean/std/min/max) dan value counts kategorikal
- **Klasifikasi Missing Value** — identifikasi mekanisme MCAR, MAR, dan MNAR per kolom

**Temuan utama diagnostik:**
- DS1: 0% missing (dataset simulasi lengkap); `severityLabel` imbalanced — "normal" mendominasi 90.9%
- DS2: `issue_assignee` 46.6% null (MAR); 16 kolom `wf_*` null 95-100% (MNAR by design)
- DS2: `priorityNormalized` masih 50.9% "unknown" — kualitas data terbatas untuk analisis priority

---

## 3. Pembersihan Data (S-Scrub) [SELESAI] — Ghazy

- **Hapus Duplikasi** — 0 baris dihapus DS1 (sudah bersih); DS2 id unik dikonfirmasi
- **Standardisasi Teks** — lowercase + trim whitespace kolom kategorikal
- **Imputasi Missing Value Terarah:**
  - MAR: fill 'unassigned' untuk `issue_assignee`, buat flag `isResolved` untuk `issue_resolution_date`
  - MNAR: drop 16 kolom `wf_*` yang 95-100% null
  - Sisa `wf_resolved/in_progress/waiting`: fill 0 (MNAR bermakna nol aktivitas)
- **Konversi Datetime** — parsing timestamp ke `datetime64[ns, UTC]` via `pd.to_datetime()`
- **Pembersihan Teks Utterances** — regex cleaning, hitung `wordCount`, filter `wordCount < 3` → 14.455 baris bersih
- **Penanganan Outlier** — cap P99 + flag `isLongTicket` (DS1 `daysOpen`); cap P99 (DS2 `resolutionDurationHours`, `wf_total_time`)

---

## 4. Rekayasa Fitur Baru (Feature Engineering) [SELESAI] — Ghazy

### DS1 — 10 fitur baru (22 kolom total di `ds1Clean.csv`)

| Fitur | Keterangan |
|-------|------------|
| `severityLevel` / `severityLabel` | Parse dari format "N - Label" — ordinal + kategorikal |
| `priorityLevel` / `priorityLabel` | Parse dari format "N - Label" — ordinal + kategorikal |
| `seniorityLevel` | Integer dari `RequestorSeniority` |
| `satisfactionLevel` | Integer dari `Satisfaction` |
| `resolutionDurationDays` | Proxy durasi resolusi = `daysOpen` (tidak ada timestamp) |
| `isLongTicket` | Flag: `daysOpen > P95` |
| `isHighPriority` | Flag: `priorityLevel == max` |
| `priorityVerified` | Konsistensi severity–priority — 53% verified |

### DS2 — 12 fitur baru (57 kolom total di `ds2IssuesClean.csv`)

| Fitur | Keterangan |
|-------|------------|
| `isResolved` | Flag: `resolution_date.notna()` |
| `totalTimeHours` | `wf_total_time / 3600` |
| `resolutionDurationHours` | `(resolution_date - created) / 3600` — KPI utama SLA |
| `timePerStepHours` | `totalTimeHours / processing_steps` |
| `resolutionSpeedCategory` | qcut 3 bin → fast / medium / slow |
| `isComplex` | `wfe_reopened > 0` OR `issue_contr_count > median` |
| `priorityNormalized` | Normalisasi nilai priority yang inkonsisten |
| `compositeScore` | mean(Q1, Q2, Q3) dari scored sample |
| `performanceBinary` | `compositeScore >= 4` → good |
| `utteranceCountPerIssue` | Proxy intensitas komunikasi |
| `messageClean` | Teks bersih untuk NLP |
| `wordCount` | Filter utterance terlalu pendek |

---

## 5. Integrasi & Ekspor Data [SELESAI] — Ghazy

- **Keputusan integrasi: Opsi B + C** — DS1 dan DS2 tidak di-concat (skema fundamentally berbeda); DS2 enriched via `issueId` dari scored sample
- **Tidak ada** `mergedClean.csv` atau `ds1CleanBalanced.csv`

| File Output | Baris | Kolom | Lokasi |
|-------------|-------|-------|--------|
| `ds1Clean.csv` | 100.000 | 22 | `data/processed/` |
| `ds2IssuesClean.csv` | 66.691 | 57 | `data/processed/` |
| `ds2UtterancesClean.csv` | 14.455 | 12 | `data/processed/` |
| `ds2ScoredClean.csv` | 747 | 21 | `data/processed/` |
| `ds2SnapshotClean.csv` | 90.904 | 45 | `data/processed/` (59 baris rusak diskip) |

---

## 6. Eksplorasi Data (E-Explore) [SELESAI] — Ghazy + Aziz

### Bagian Ghazy — Statistik + Visualisasi Dasar (5 visualisasi)

- **Statistik Deskriptif DS1 & DS2** — mean/std/min/max variabel numerik utama; value counts kategorikal
- **Viz 1 — Distribusi Severity & Priority** (PA-4)  
  DS1 severity "normal" 90.9% → class imbalance; priority lebih merata → lebih cocok sebagai target model  
  → `reports/figures/viz1_distribusi_severity_priority.png`

- **Viz 2 — Tren Waktu Volume & Durasi DS2** (PA-2)  
  Volume tiket bervariasi per bulan; avg `resolutionDurationHours` berkorelasi dengan volume → kapasitas tim terbatas  
  → `reports/figures/viz2_tren_waktu_ds2.png`

- **Viz 3 — % SLA Violated per Issue Type DS2** (PA-2)  
  Beberapa kategori SLA violated >50% → kegagalan sistemik; kategori dengan volume tinggi paling berdampak  
  → `reports/figures/viz3_sla_violated_per_type.png`

- **Viz 4 — Spearman Heatmap DS2 + DS1** (PA-1)  
  `totalTimeHours` ↔ `resolutionDurationHours` hampir sempurna (r ≈ 1.0) → drop salah satu dari model  
  `isComplex` ↔ `wfe_reopened` tinggi → flag valid sebagai fitur  
  → `reports/figures/viz4_heatmap_korelasi_ds2.png`, `viz4b_heatmap_korelasi_ds1.png`

### Bagian Aziz — Visualisasi Lanjutan (5 visualisasi)

- **Viz 5 — Distribusi Durasi Resolusi + Boxplot per Priority DS1** (PA-1, PA-4)  
  Distribusi right-skewed (mean=6.80, median=5.00, skew=1.31); priority "low" paradoks paling lambat (median 6 hari)  
  → `reports/figures/viz5_durasi_resolusi_ds1.png`

- **Viz 6 — Rata-rata Durasi per Kategori FiledAgainst DS1** (PA-2)  
  "hardware" paling lambat (avg 16.94 hari, 2.49× rata-rata); "access/login" tercepat (avg 0.27 hari)  
  Hardware + systems mencakup 50% volume tiket DS1 → bottleneck SLA utama  
  → `reports/figures/viz6_avg_durasi_per_kategori.png`

- **Viz 7 — Satisfaction vs Severity Heatmap DS1** (PA-3)  
  Hubungan tidak linear: "minor" satisfaction paling rendah (avg 1.33), bukan "critical" (avg 1.60)  
  Kemungkinan: insiden kecil diharapkan cepat selesai, jika tidak → ekspektasi lebih terasa  
  → `reports/figures/viz7_satisfaction_vs_severity.png`

- **Viz 8 — Kecepatan Resolusi per Issue Type DS2** (PA-5)  
  "subtask" paling lambat (90.7% slow, 1.3% fast) — bergantung tiket induk  
  "deployment" dan "service" performa terbaik (<3% slow) → benchmark best practice  
  → `reports/figures/viz8_speed_per_type_ds2.png`

- **Viz 9 — Re-open Rate per Issue Type DS2** (PA-4)  
  Menunjukkan kategori tiket yang paling sering di-reopen → indikator eskalasi dan kegagalan resolusi pertama kali  
  Kategori dengan re-open rate tinggi = prioritas perbaikan SOP dan pelatihan agen  
  → `reports/figures/viz9_reopen_per_type_ds2.png`

---

## 7. Tabel Temuan Eksploratif Lengkap

| No | Temuan | Visualisasi | Pertanyaan Analitik |
|----|--------|-------------|---------------------|
| 1 | DS1 severity "normal" mendominasi 90.9% → class imbalance signifikan | `viz1_distribusi_severity_priority.png` | PA-4 |
| 2 | DS1 priority lebih merata (high 36.5%) → lebih cocok sebagai target klasifikasi | `viz1_distribusi_severity_priority.png` | PA-4 |
| 3 | DS2 volume tiket per bulan bervariasi; avg durasi berkorelasi dengan volume | `viz2_tren_waktu_ds2.png` | PA-2 |
| 4 | Beberapa issue_type DS2 SLA violated >50% → kegagalan sistemik | `viz3_sla_violated_per_type.png` | PA-2 |
| 5 | `totalTimeHours` ↔ `resolutionDurationHours` hampir sempurna (r ≈ 1.0) → redundan | `viz4_heatmap_korelasi_ds2.png` | PA-1 |
| 6 | `isComplex` berkorelasi dengan `wfe_reopened` → flag valid untuk model | `viz4_heatmap_korelasi_ds2.png` | PA-1 |
| 7 | DS1 distribusi durasi right-skewed (mean=6.80, median=5.00, skew=1.31); priority "low" paling lambat (median 6 hari) | `viz5_durasi_resolusi_ds1.png` | PA-1, PA-4 |
| 8 | "hardware" paling lambat (avg 16.94 hari, 2.49× rata-rata); "access/login" tercepat (avg 0.27 hari) | `viz6_avg_durasi_per_kategori.png` | PA-2 |
| 9 | Satisfaction–severity tidak linear: "minor" satisfaction paling rendah (avg 1.33), bukan "critical" (avg 1.60) | `viz7_satisfaction_vs_severity.png` | PA-3 |
| 10 | "subtask" paling lambat (90.7% slow); "deployment" dan "service" performa terbaik (<3% slow) | `viz8_speed_per_type_ds2.png` | PA-5 |
| 11 | Kategori tertentu DS2 memiliki re-open rate jauh di atas rata-rata → kegagalan resolusi pertama kali & eskalasi sistemik | `viz9_reopen_per_type_ds2.png` | PA-4 |

---

## 8. Handoff ke Modeler (Daffa)

- DS1 severity imbalanced (normal 90.9%) → SMOTE hanya pada `X_train`, tidak seluruh dataset
- Gunakan `priorityLabel` sebagai target DS1 (bukan `severityLabel` — terlalu imbalanced)
- Gunakan `resolutionDurationHours` (drop `totalTimeHours` — hampir redundan, r ≈ 1.0)
- `isComplex` valid sebagai fitur model (korelasi tinggi dengan `wfe_reopened`)
- `priorityVerified` = 53% DS1 → priority dan severity tidak selalu konsisten, jangan gabungkan sebagai satu fitur
- Scored sample: 747 baris (n=360 valid compositeScore) → terlalu kecil untuk supervised; `performanceBinary` 99.5% NaN
- Kolom NLP: `messageClean` di `ds2UtterancesClean.csv`
- DS2 priority 50.9% unknown → gunakan `priorityNormalized`

---

**Ringkasan visualisasi (viz1–viz14):**

| Viz | File | Fase | Pertanyaan Analitik |
|-----|------|------|---------------------|
| 1 | `viz1_distribusi_severity_priority.png` | E-Explore | PA-4 |
| 2 | `viz2_tren_waktu_ds2.png` | E-Explore | PA-2 |
| 3 | `viz3_sla_violated_per_type.png` | E-Explore | PA-2 |
| 4 | `viz4_heatmap_korelasi_ds2.png` + `viz4b_heatmap_korelasi_ds1.png` | E-Explore | PA-1 |
| 5 | `viz5_durasi_resolusi_ds1.png` | E-Explore | PA-1, PA-4 |
| 6 | `viz6_avg_durasi_per_kategori.png` | E-Explore | PA-2 |
| 7 | `viz7_satisfaction_vs_severity.png` | E-Explore | PA-3 |
| 8 | `viz8_speed_per_type_ds2.png` | E-Explore | PA-5 |
| 9 | `viz9_reopen_per_type_ds2.png` | E-Explore | PA-4 (eskalasi/re-open) |
| 10 | `viz10_confusion_matrix_ds1.png` | M-Model | PA-1, PA-4 |
| 11 | `viz11_feature_importance_ds1.png` | M-Model | PA-1 |
| 12 | `viz12_elbow_cluster.png` | M-Model | PA-2, PA-5 |
| 13 | `viz13_cluster_profile_ds2.png` | M-Model | PA-2, PA-5 |
| 14 | `viz14_topic_distribution_nlp.png` | M-Model (opsional) | PA-3 |

---

## 9. M-Model [IMPLEMENTASI SELESAI] — Aziz

> **File kerja:** `notebooks/04_model.ipynb`  
> **Semua artefak model tersedia di:** `reports/models/`

### Model yang Dibangun

| Model | Dataset | Algoritma | Metrik Utama | Nilai | PA |
|-------|---------|-----------|--------------|-------|----|
| Klasifikasi Priority | DS1 | Random Forest | Accuracy | 0.6493 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Random Forest | Weighted F1 | 0.6534 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Random Forest | Macro F1 | 0.5809 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Decision Tree | Accuracy | 0.6504 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Decision Tree | Weighted F1 | 0.6536 | PA-1, PA-4 |
| Clustering Tiket | DS2 | K-Means (k=5) | Silhouette Score | 0.5903 | PA-2, PA-5 |
| NLP Topic Modeling | DS2 Utterances | LDA (6 topik) | Distribusi topik | 6 topik teridentifikasi | PA-3 |

### Temuan Utama M-Model

| No | Temuan | Model | PA |
|----|--------|-------|----|
| 1 | `isHighPriority` adalah fitur paling dominan (importance=0.7556) — jauh melampaui `severityLevel` (0.0234) | RF DS1 | PA-1, PA-4 |
| 2 | Top-3 fitur: `isHighPriority` (75.56%) → `seniorityLevel` (15.34%) → `resolutionDurationDays` (5.15%) | RF DS1 | PA-1 |
| 3 | `severityLevel` hanya 2.3% importance → konfirmasi inkonsistensi priority-severity (hanya 53% `priorityVerified`) | RF DS1 | PA-4 |
| 4 | RF dan DT hampir identik (<0.003 perbedaan) — pola DS1 cukup linear | Klasifikasi DS1 | PA-1 |
| 5 | K-Means k=5 silhouette=0.5903 — struktur cluster cukup kuat (>0.5) | K-Means DS2 | PA-2, PA-5 |
| 6 | Cluster 1: paling berisiko SLA (100% slow, avg 59.559 jam, 17.998 tiket) | K-Means DS2 | PA-2 |
| 7 | Cluster 2: performa terbaik (1% slow, avg 865 jam, 5.69 steps, 10.729 tiket) | K-Means DS2 | PA-5 |
| 8 | Cluster 4: `wfe_reopened` tertinggi (avg 1.12) → kualitas resolusi buruk, perlu perbaikan SOP | K-Means DS2 | PA-4 |
| 9 | LDA 6 topik — topik 'access/login' dan 'password' dominan → konsisten dengan temuan viz6 | LDA DS2 | PA-3 |

### Profil 5 Cluster DS2 (K-Means k=5)

| Cluster | Jumlah Tiket | Avg Durasi (jam) | Avg Steps | % SLA Slow | Karakteristik |
|---------|-------------|-----------------|-----------|-----------|---------------|
| 0 | 34.317 | 2.723 | 3.13 | 9% | Tiket standar — volume terbesar, durasi sedang |
| **1** | 17.998 | **59.559** | 1.00 | **100%** | Tiket sangat lambat — semua melanggar SLA |
| **2** | 10.729 | 865 | 5.69 | **1%** | Performa terbaik — kompleks tapi cepat |
| 3 | 752 | 14.271 | 8.52 | 22% | Tiket kompleks banyak langkah |
| 4 | 2.041 | 14.161 | 7.43 | 26% | Paling sering di-reopen (avg 1.12×) |

### Artefak Model (untuk 05_interpret.ipynb)

| Artefak | Lokasi |
|---------|--------|
| Model RF | `reports/models/rf_priority_ds1.pkl` |
| Model DT | `reports/models/dt_priority_ds1.pkl` |
| LabelEncoder target | `reports/models/le_target_ds1.pkl` |
| LabelEncoder FiledAgainst | `reports/models/le_filed_ds1.pkl` |
| LabelEncoder TicketType | `reports/models/le_ticket_ds1.pkl` |
| Model K-Means (k=5) | `reports/models/kmeans_ds2.pkl` |
| StandardScaler DS2 | `reports/models/scaler_ds2.pkl` |
| DS2 + kolom cluster | `reports/models/ds2_with_clusters.csv` |
| Model LDA | `reports/models/lda_utterances_ds2.pkl` |
| TF-IDF Vectorizer | `reports/models/tfidf_utterances_ds2.pkl` |

---

---

## 10. N-iNterpret [SELESAI] — Aziz

> **File kerja:** `notebooks/05_interpret.ipynb` — 10 sel, diimplementasikan 14 Juni 2026  
> **Input:** Semua artefak PKL di `reports/models/` + `ds2_with_clusters.csv` + `ds1Clean.csv`

### Struktur Notebook 05_interpret.ipynb

| Sel | Isi | PA |
|-----|-----|----|
| Sel 1 | Import & Setup Path | — |
| Sel 2 | Load semua artefak model (8 PKL + 2 CSV) | — |
| Sel 3 | Feature importance RF + interpretasi markdown | PA-1 |
| Sel 4 | Confusion matrix analysis + Viz 15 (crosstab severity-priority) | PA-4 |
| Sel 5 | Profil 5 cluster + Viz 16 (heatmap dua panel) | PA-2, PA-5 |
| Sel 6 | SLA per issue_type + Viz 17 (tiga panel ringkasan) | PA-2, PA-5 |
| Sel 7 | LDA topik + interpretasi konteks kepuasan | PA-3 |
| Sel 8 | Jawaban eksplisit PA-1 s/d PA-5 (tabel + nilai aktual) | PA-1–PA-5 |
| Sel 9 | Rekomendasi operasional R-1 s/d R-5 + tabel prioritas | PA-1–PA-5 |
| Sel 10 | Narasi Bab 5 (seksi 5.1–5.5) untuk laporan PDF | — |

### Jawaban PA-1 s/d PA-5 (Nilai Aktual Terverifikasi)

| PA | Jawaban Singkat | Sumber Bukti |
|----|-----------------|--------------|
| PA-1 | `isHighPriority` (75.56%) + kurangnya workflow steps (Cluster 1 avg=1.00) | RF DS1 + K-Means DS2 |
| PA-2 | Cluster 1 (100% slow, 17.998 tiket); `subtask` (90.7% slow); `hardware` DS1 (avg 16.94 hari) | K-Means DS2 + EDA DS1 |
| PA-3 | Hubungan tidak linear: `minor`=1.33, `critical`=1.60 — ekspektasi lebih menentukan dari severity | EDA Viz 7 DS1 + LDA |
| PA-4 | `priorityVerified`=52.9%; RF acc=64.9% — triage subjektif, 47.1% tiket inkonsisten | RF DS1 + `priorityVerified` |
| PA-5 | Terbaik: Cluster 2 (1% slow) + `assistance` (0% slow); Terburuk: Cluster 1 (100% slow) + `subtask` (90.7%) | K-Means DS2 |

### Rekomendasi Operasional

| Kode | Rekomendasi | Target Terukur |
|------|-------------|----------------|
| R-1 | Eskalasi otomatis tiket tanpa aktivitas ≥24 jam (Cluster 1) | Turunkan slow Cluster 1 dari 100% ke <50% |
| R-2 | Standarisasi SOP berbasis Cluster 2 sebagai benchmark | Shift 20% tiket Cluster 0 ke pola Cluster 2 |
| R-3 | Tambah kapasitas hardware/systems (avg 16.94 hari, 2.5× rata-rata) | Turunkan avg hardware dari 16.94 ke <10 hari |
| R-4 | Triage semi-otomatis berbasis RF scoring | Tingkatkan `priorityVerified` dari 52.9% ke >75% |
| R-5 | Chain dependency tracker subtask/epic | Turunkan slow subtask dari 90.7% ke <50% |

### Visualisasi N-iNterpret

| Viz | File | PA |
|-----|------|----|
| Viz 15 | `viz15_severity_priority_consistency.png` | PA-4 |
| Viz 16 | `viz16_cluster_heatmap_interpret.png` | PA-2, PA-5 |
| Viz 17 | `viz17_rekomendasi_summary.png` | PA-2, PA-5 |

### Ringkasan Visualisasi Lengkap (viz1–viz17)

| Viz | File | Fase | PA |
|-----|------|------|----|
| 1 | `viz1_distribusi_severity_priority.png` | E-Explore | PA-4 |
| 2 | `viz2_tren_waktu_ds2.png` | E-Explore | PA-2 |
| 3 | `viz3_sla_violated_per_type.png` | E-Explore | PA-2 |
| 4 | `viz4_heatmap_korelasi_ds2.png` + `viz4b_heatmap_korelasi_ds1.png` | E-Explore | PA-1 |
| 5 | `viz5_durasi_resolusi_ds1.png` | E-Explore | PA-1, PA-4 |
| 6 | `viz6_avg_durasi_per_kategori.png` | E-Explore | PA-2 |
| 7 | `viz7_satisfaction_vs_severity.png` | E-Explore | PA-3 |
| 8 | `viz8_speed_per_type_ds2.png` | E-Explore | PA-5 |
| 9 | `viz9_reopen_per_type_ds2.png` | E-Explore | PA-4 |
| 10 | `viz10_confusion_matrix_ds1.png` | M-Model | PA-1, PA-4 |
| 11 | `viz11_feature_importance_ds1.png` | M-Model | PA-1 |
| 12 | `viz12_elbow_cluster.png` | M-Model | PA-2, PA-5 |
| 13 | `viz13_cluster_profile_ds2.png` | M-Model | PA-2, PA-5 |
| 14 | `viz14_topic_distribution_nlp.png` | M-Model | PA-3 |
| 15 | `viz15_severity_priority_consistency.png` | N-iNterpret | PA-4 |
| 16 | `viz16_cluster_heatmap_interpret.png` | N-iNterpret | PA-2, PA-5 |
| 17 | `viz17_rekomendasi_summary.png` | N-iNterpret | PA-2, PA-5 |

---

*Laporan detail interaktif tersedia di [notebooks/02_scrub.ipynb](../notebooks/02_scrub.ipynb), [notebooks/03_explore.ipynb](../notebooks/03_explore.ipynb), [notebooks/04_model.ipynb](../notebooks/04_model.ipynb), dan [notebooks/05_interpret.ipynb](../notebooks/05_interpret.ipynb).*  
*Seluruh visualisasi (viz1–viz17) tersimpan di [reports/figures/](figures/).*  
*Seluruh artefak model tersimpan di [reports/models/](models/).*
