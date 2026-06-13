# Ringkasan S-Scrub & E-Explore
## Kelompok 14 — II4013 Data Analitik ITB
### Topik 14: Kinerja Layanan TI Organisasi (IT Service Performance Analytics)

> **PIC:** Ghazy Achmed Movlech Urbayani (18223093) — S-Scrub + E-Explore dasar  
> **PIC:** M Azizdzaki Khrisnanurmuflih (18223128) — E-Explore lanjutan + Visualisasi tambahan  
> **Status keseluruhan:** S-Scrub [SELESAI] | E-Explore [SELESAI] | M-Model [BELUM] | N-iNterpret [MENUNGGU]  
> **Terakhir diperbarui:** 13 Juni 2026

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
- **Viz 8B — Distribusi Severity & Priority** (PA-4)  
  DS1 severity "normal" 90.9% → class imbalance; priority lebih merata → lebih cocok sebagai target model  
  → `reports/figures/8B_viz1_distribusi_severity_priority.png`

- **Viz 8C — Tren Waktu Volume & Durasi DS2** (PA-2)  
  Volume tiket bervariasi per bulan; avg `resolutionDurationHours` berkorelasi dengan volume → kapasitas tim terbatas  
  → `reports/figures/8C_viz2_tren_waktu_ds2.png`

- **Viz 8D — % SLA Violated per Issue Type DS2** (PA-2)  
  Beberapa kategori SLA violated >50% → kegagalan sistemik; kategori dengan volume tinggi paling berdampak  
  → `reports/figures/8D_viz3_sla_violated_per_type.png`

- **Viz 8E — Spearman Heatmap DS2 + DS1** (PA-1)  
  `totalTimeHours` ↔ `resolutionDurationHours` hampir sempurna (r ≈ 1.0) → drop salah satu dari model  
  `isComplex` ↔ `wfe_reopened` tinggi → flag valid sebagai fitur  
  → `reports/figures/8E_viz4_heatmap_korelasi_ds2.png`, `8E_viz4b_heatmap_korelasi_ds1.png`

### Bagian Aziz — Visualisasi Lanjutan (4 visualisasi)

- **Viz A — Distribusi Durasi Resolusi + Boxplot per Priority DS1** (PA-1, PA-4)  
  Distribusi right-skewed (mean=6.80, median=5.00, skew=1.31); priority "low" paradoks paling lambat (median 6 hari)  
  → `reports/figures/viz_A_durasi_resolusi_ds1.png`

- **Viz B — Rata-rata Durasi per Kategori FiledAgainst DS1** (PA-2)  
  "hardware" paling lambat (avg 16.94 hari, 2.49× rata-rata); "access/login" tercepat (avg 0.27 hari)  
  Hardware + systems mencakup 50% volume tiket DS1 → bottleneck SLA utama  
  → `reports/figures/viz_B_avg_durasi_per_kategori.png`

- **Viz C — Satisfaction vs Severity Heatmap DS1** (PA-3)  
  Hubungan tidak linear: "minor" satisfaction paling rendah (avg 1.33), bukan "critical" (avg 1.60)  
  Kemungkinan: insiden kecil diharapkan cepat selesai, jika tidak → ekspektasi lebih terasa  
  → `reports/figures/viz_C_satisfaction_vs_severity.png`

- **Viz D — Kecepatan Resolusi per Issue Type DS2** (PA-5)  
  "subtask" paling lambat (90.7% slow, 1.3% fast) — bergantung tiket induk  
  "deployment" dan "service" performa terbaik (<3% slow) → benchmark best practice  
  → `reports/figures/viz_D_speed_per_type_ds2.png`

---

## 7. Tabel Temuan Eksploratif Lengkap

| No | Temuan | Visualisasi | Pertanyaan Analitik |
|----|--------|-------------|---------------------|
| 1 | DS1 severity "normal" mendominasi 90.9% → class imbalance signifikan | `8B_viz1_distribusi_severity_priority.png` | PA-4 |
| 2 | DS1 priority lebih merata (high 36.5%) → lebih cocok sebagai target klasifikasi | `8B_viz1_distribusi_severity_priority.png` | PA-4 |
| 3 | DS2 volume tiket per bulan bervariasi; avg durasi berkorelasi dengan volume | `8C_viz2_tren_waktu_ds2.png` | PA-2 |
| 4 | Beberapa issue_type DS2 SLA violated >50% → kegagalan sistemik | `8D_viz3_sla_violated_per_type.png` | PA-2 |
| 5 | `totalTimeHours` ↔ `resolutionDurationHours` hampir sempurna (r ≈ 1.0) → redundan | `8E_viz4_heatmap_korelasi_ds2.png` | PA-1 |
| 6 | `isComplex` berkorelasi dengan `wfe_reopened` → flag valid untuk model | `8E_viz4_heatmap_korelasi_ds2.png` | PA-1 |
| 7 | DS1 distribusi durasi right-skewed (mean=6.80, median=5.00, skew=1.31); priority "low" paling lambat (median 6 hari) | `viz_A_durasi_resolusi_ds1.png` | PA-1, PA-4 |
| 8 | "hardware" paling lambat (avg 16.94 hari, 2.49× rata-rata); "access/login" tercepat (avg 0.27 hari) | `viz_B_avg_durasi_per_kategori.png` | PA-2 |
| 9 | Satisfaction–severity tidak linear: "minor" satisfaction paling rendah (avg 1.33), bukan "critical" (avg 1.60) | `viz_C_satisfaction_vs_severity.png` | PA-3 |
| 10 | "subtask" paling lambat (90.7% slow); "deployment" dan "service" performa terbaik (<3% slow) | `viz_D_speed_per_type_ds2.png` | PA-5 |

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

*Laporan detail interaktif tersedia di [notebooks/02_scrub.ipynb](../notebooks/02_scrub.ipynb) dan [notebooks/03_explore.ipynb](../notebooks/03_explore.ipynb).*  
*Seluruh visualisasi tersimpan di [reports/figures/](figures/).*
