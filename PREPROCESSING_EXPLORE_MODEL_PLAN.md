# Preprocessing, EDA & Visualization Plan - Kelompok 14: IT Service Analytics
> Ghazy Achmed Movlech Urbayani - 18223093 - Data Preprocessing Lead (S-Scrub + E-Explore awal)
> M Azizdzaki Khrisnanurmuflih - 18223128 - Visualization / Dashboard Developer (E-Explore lanjutan)
> Referensi: II4013 Week 03 Preprocessing, Week 12 OSEMN, Panduan TugasBesar

---

## Status Pengerjaan (per 14 Juni 2026)

| Fase | Pengerjaan | Status |
|------|-----------|--------|
| S - Scrub | Ghazy | [SELESAI] output di `data/processed/` |
| E - Explore (Statistik + Viz dasar) | Ghazy | [SELESAI] 5 visualisasi di `reports/figures/` |
| E - Explore (Viz lanjutan + Interpretasi) | **Aziz** | [SELESAI] 5 visualisasi (Viz 5–9) + interpretasi markdown di `03_explore.ipynb` |
| M - Model | **Aziz** | [SELESAI - IMPLEMENTASI] — `04_model.ipynb` sudah diisi lengkap, jalankan Kernel → Restart & Run All |
| N - iNterpret | Aziz + Adam | [MENUNGGU Model selesai] |

---

## Cakupan Kerja

| OSEMN | Dikerjakan Oleh | Output |
|---|---|---|
| O - Obtain | Nicholas (Data Engineer) | Raw dataset di `data/raw/` |
| S - Scrub | Ghazy | [SELESAI] Clean dataset, preprocessing notebook, fitur baru |
| E - Explore (awal) | Ghazy | [SELESAI] Statistik deskriptif, 5 visualisasi dasar, temuan awal |
| E - Explore (lanjutan) | Aziz | [SELESAI] 5 visualisasi tambahan (Viz 5–9) + interpretasi markdown dikaitkan PA-1 s/d PA-5 |
| M - Model | Aziz (Analyst/Modeler) | Model klasifikasi, clustering, evaluasi |
| N - iNterpret | Aziz + Adam | Visualisasi hasil model, insight, rekomendasi, laporan |

---

## Dataset

### Dataset 1 - IBM Watson IT Help Desk [AKTUAL]
- File: `data/raw/primary/WA_Fn-UseC_-IT-Help-Desk.csv`
- **100.000 baris, 10 kolom** (simulasi, 0% missing)
- Kolom kunci: `FiledAgainst`, `TicketType`, `Severity`, `Priority`, `RequestorSeniority`, `daysOpen`, `Satisfaction`
- **Tidak ada kolom timestamp** -> `daysOpen` digunakan sebagai proxy durasi resolusi
- Clean output: `data/processed/ds1Clean.csv` (22 kolom setelah feature engineering)

### Dataset 2 - Mendeley Help Desk Tickets [AKTUAL]
- Multi-file di `data/raw/supporting/`:

| File | Isi | Baris | Clean Output |
|---|---|---|---|
| `issues.csv` | Tiket utama - backbone | 66.691 | `ds2IssuesClean.csv` (57 kolom) |
| `issues_change_history.csv` | Histori perubahan assignee/status | - | (referensi saja) |
| `issues_snapshot.csv` | Per-assignee/per-turn (DESAIN) | 90.963 | `ds2SnapshotClean.csv` |
| `issues_snapshot_sample.xlsx` | Ground truth label score Q1/Q2/Q3 | 747 | `ds2ScoredClean.csv` (21 kolom) |
| `sample_utterances.csv` | Teks percakapan - sumber NLP | 14.455 | `ds2UtterancesClean.csv` (12 kolom) |

---

## Alur OSEMN

```
[Scrub awal] -> [EDA diagnostik] -> [Scrub lanjutan] -> [EDA final] -> handoff ke Modeler
```

Scrub awal: tipe data, format, duplikat jelas
EDA diagnostik: distribusi, missing pattern, outlier, imbalance
Scrub lanjutan: berdasarkan temuan EDA
EDA final: visualisasi, temuan, interpretasi untuk laporan

---

## FASE 0 - Setup & Load [SELESAI] (Ghazy)

**Tabel dokumentasi aktual:**

| File | Baris | Kolom | Catatan |
|---|---|---|---|
| WA_Fn-UseC_-IT-Help-Desk.csv | 100.000 | 10 | DS1, 0% missing, simulasi |
| issues.csv | 66.691 | 57 | DS2 backbone |
| issues_change_history.csv | - | - | Referensi join |
| issues_snapshot.csv | 90.963 | 45 | Per-assignee, desain |
| issues_snapshot_sample.xlsx | 747 | 21 | Ground truth Q1/Q2/Q3 |
| sample_utterances.csv | 14.455 | 12 | NLP source |

---

## FASE 1 - EDA Diagnostik [SELESAI] (Ghazy)

**Temuan aktual:**

### 1A. Distribusi & Statistik Dasar
- DS1: `severityLabel` - "normal" mendominasi 90.9% -> class imbalance signifikan
- DS1: `priorityLabel` - lebih merata (high 36.5%, unassigned 30.1%, low 17.1%, medium 16.3%)
- DS1: `FiledAgainst` - systems 40%, access/login 29.9%, software 20.1%, hardware 10%
- DS1: `daysOpen` - mean=6.80, std=7.24, max=31 (sebelum capping)
- DS2: `priorityNormalized` - "unknown" masih dominan 50.9%
- DS2: `issue_type` - ticket 67.9%, service 7.9%, subtask 7.1%
- DS2: scored sample 747 baris -> compositeScore mean=3.80 (n=360 valid)

### 1B. Missing Value - Hasil Klasifikasi
- DS1: 0% missing (dataset simulasi lengkap)
- DS2 `issue_assignee`: ~46.6% null -> MAR -> fill 'unassigned'
- DS2 `issue_resolution_date`: ~1.3% null -> MAR berkorelasi status open -> flag `isResolved`
- DS2 16 kolom `wf_*`: 95-100% null -> MNAR by design -> drop kolom

### 1C. Duplikasi
- DS1: 0 baris 100% identik
- DS2 issues.csv: id unik (PK dikonfirmasi)
- DS2 snapshot: multi-row per issue (per-assignee/per-turn) - DESAIN, tidak di-deduplicate

### 1D. Tipe Data & Format
- DS1: kolom kategorikal plain text, tidak ada timestamp
- DS2: timestamp masih object dtype -> perlu parsing ke datetime64 UTC
- DS2: `wf_total_time` dalam detik (per FEATURES.md)

### 1E. Outlier
- DS1 `daysOpen`: genuine extreme -> cap P99, flag `isLongTicket`
- DS2 `wf_total_time`: genuine extreme -> cap P99
- DS2 `resolutionDurationHours`: genuine extreme -> cap P99

### 1F. Class Imbalance
- DS1 Severity: imbalanced (normal 90.9%) -> tidak ideal sebagai target klasifikasi
- DS1 Priority: lebih balanced -> lebih cocok sebagai target
- DS2 performanceBinary: 99.5% NaN (hanya 747 sampel scored) -> supervised terbatas
- **Keputusan sampling:** SMOTE hanya pada training split jika label dipakai sebagai target

---

## FASE 2 - Scrub Awal (Basic) [SELESAI] (Ghazy)

### DS1
- Drop baris 100% identik -> 0 baris dihapus (sudah bersih)
- Parse `Severity`/`Priority` format "N - Label" -> `severityLevel`, `severityLabel`, `priorityLevel`, `priorityLabel`
- Lowercase + strip: `FiledAgainst`, `TicketType`

### DS2
- Verifikasi relasi antar file -> id unik dikonfirmasi
- Drop duplikat by issue id (preventif) -> tidak ada yang dihapus
- Lowercase + strip kolom kategorikal issues.csv

---

## FASE 3 - Scrub Lanjutan (Berdasarkan Temuan EDA) [SELESAI] (Ghazy)

### 3A. Handle Missing Value - Hasil Aktual
| Kolom | Null % | Mekanisme | Tindakan | Hasil |
|---|---|---|---|---|
| DS2 `issue_assignee` | 46.6% | MAR | Fill 'unassigned' | 0% null |
| DS2 `issue_resolution_date` | 1.3% | MAR | Buat flag `isResolved` | Flag tersedia |
| DS2 `issue_resolution` | 1.3% | MAR | Fill 'unknown' | 0% null |
| DS2 16 kolom `wf_*` | 95-100% | MNAR | Drop kolom | Noise dieliminasi |
| DS2 `wf_resolved/in_progress/waiting` | 44-70% | MNAR | Fill 0 | 0% null |
| DS1 semua kolom | 0% | - | Tidak ada tindakan | Tetap bersih |

### 3B. Durasi Resolusi (DS1)
- DS1 **tidak punya timestamp** -> `resolutionDurationDays` = `daysOpen` (proxy)

### 3C. Parsing Waktu (DS2)
- Semua kolom timestamp -> `datetime64[ns, UTC]` via `pd.to_datetime()`
- `timePerStepHours` = `totalTimeHours / processing_steps`

### 3D. Cleaning Teks Utterances
- Pipeline: lowercase -> strip non-alfabet -> normalize whitespace -> buat `messageClean`
- Buat `wordCount`, filter `wordCount < 3` -> 14.455 baris bersih di `ds2UtterancesClean.csv`

### 3E. Handle Outlier
- DS1 `daysOpen`: cap P99, flag `isLongTicket`
- DS2 `wf_total_time`: cap P99
- DS2 `resolutionDurationHours`: cap P99
- DS2 `isComplex`: flag jika `wfe_reopened > 0` OR `issue_contr_count > median`

### 3F. Sampling
- **Tidak dilakukan** - imbalance di DS1 tidak sampai rasio 10:1 untuk target klasifikasi yang dipilih

---

## FASE 4 - Feature Engineering [SELESAI] (Ghazy)

### DS1 - Fitur Baru (22 kolom total di ds1Clean.csv)

| Fitur | Formula | Alasan |
|---|---|---|
| `severityLevel` | Integer dari "N - Label" | Ordinal numerik untuk korelasi |
| `severityLabel` | String dari "N - Label" | Kategorikal untuk visualisasi |
| `priorityLevel` | Integer dari "N - Label" | Ordinal filter & analisis |
| `priorityLabel` | String dari "N - Label" | Kategorikal untuk visualisasi |
| `seniorityLevel` | Integer dari `RequestorSeniority` | Hipotesis: seniority vs durasi tiket |
| `satisfactionLevel` | Integer dari `Satisfaction` | Target KPI kepuasan pengguna |
| `resolutionDurationDays` | `daysOpen` (proxy, tidak ada timestamp) | KPI durasi resolusi |
| `isLongTicket` | `daysOpen > P95` | Flag tiket sangat lama |
| `isHighPriority` | `priorityLevel == max` | Flag prioritas tertinggi |
| `priorityVerified` | `severityLevel & priorityLevel` konsisten | Deteksi redundansi - 53% verified |

### DS2 - Fitur Baru

| Fitur | Formula | Alasan |
|---|---|---|
| `isResolved` | `resolution_date.notna().astype(int)` | Flag bermakna (99% resolved) |
| `totalTimeHours` | `wf_total_time / 3600` | Konsistensi satuan |
| `timePerStepHours` | `totalTimeHours / processing_steps` | Efisiensi per langkah workflow |
| `resolutionDurationHours` | `(resolution_date - created).dt.total_seconds()/3600` | KPI utama SLA |
| `resolutionSpeedCategory` | qcut(resolutionDurationHours, 3) -> fast/medium/slow | Segmentasi kecepatan (qcut robust untuk skewed) |
| `isComplex` | `wfe_reopened>0` OR `issue_contr_count>median` | Proxy kompleksitas tiket (20% dari DS2) |
| `priorityNormalized` | Map blocker/highest->high, lowest->low, dll. | Normalisasi inkonsistensi nilai priority |
| `compositeScore` | mean(Q1, Q2, Q3) | Rata-rata lebih robust dari satu skor |
| `performanceBinary` | `compositeScore >= 4` -> good | Label binary stabil untuk klasifikasi |
| `utteranceCountPerIssue` | groupby(issueid).size | Proxy intensitas komunikasi |
| `messageClean` | lowercase -> strip non-alfabet -> normalize whitespace | Preprocessing NLP |
| `wordCount` | len(messageClean.split()) | Filter utterance terlalu pendek |

---

## FASE 5 - Integrasi Dataset [SELESAI] (Ghazy)

**Keputusan: Opsi B + C**
- DS1 dan DS2 **tidak di-concat** - skema fundamentally berbeda (simulasi vs real-world)
- DS2 enrichment: `compositeScore`, `performanceBinary`, `Q1/Q2/Q3` dari scored sample di-link ke issues via `issueId`

**Dokumentasi integrasi:**
- Kunci integrasi: `issueId` (scored -> issues)
- Limitasi: DS1 tidak punya timestamp -> analisis tren waktu hanya dari DS2
- Catatan: DS2 priority 50.9% unknown -> analisis priority DS2 terbatas

---

## FASE 6 - Output (Simpan ke `data/processed/`) [SELESAI] (Ghazy)

| File | Baris | Kolom | Keterangan |
|---|---|---|---|
| `ds1Clean.csv` | 100.000 | 22 | DS1 setelah cleaning + feature engineering |
| `ds2IssuesClean.csv` | 66.691 | 57 | DS2 issues + enrichment dari scored |
| `ds2UtterancesClean.csv` | 14.455 | 12 | Utterances setelah text cleaning |
| `ds2ScoredClean.csv` | 747 | 21 | Scored sample setelah preprocessing |
| `ds2SnapshotClean.csv` | 90.963 | 45 | Snapshot per-assignee |

> Tidak ada `mergedClean.csv` - keputusan integrasi adalah Opsi B+C (terpisah + enriched)
> Tidak ada `ds1CleanBalanced.csv` - sampling tidak dilakukan

---

## FASE 7 - Laporan Sementara S-Scrub [SELESAI] (Ghazy -> Adam untuk laporan)

### Tabel Scrub (Hasil Aktual)

| Masalah Data | Kondisi Awal | Tindakan | Kondisi Akhir |
|---|---|---|---|
| DS2 `issue_assignee` null | 46.6% null (MAR) | Fill 'unassigned' | 0% null |
| DS2 `issue_resolution_date` null | 1.3% null (MAR berkorelasi status) | Buat flag `isResolved` | Flag tersedia, null valid |
| DS2 16 kolom `wf_*` null | 95-100% null (MNAR) | Drop 16 kolom | Noise dieliminasi |
| DS1 duplikasi baris | 0 baris identik | Tidak ada tindakan | Tetap bersih |
| DS2 format timestamp | Object dtype | `pd.to_datetime()` UTC | datetime64[ns, UTC] |
| DS1 format kategorikal | Inconsistent case/whitespace | lowercase + strip | Uniform lowercase |
| DS1 format "N - Label" | Gabungan angka-teks | Parse terpisah | Ordinal + kategorikal tersedia |
| DS1 outlier `daysOpen` | Genuine extreme values | Cap P99 + flag `isLongTicket` | Max = P99 |
| DS2 outlier `resolutionDurationHours` | Genuine extreme values | Cap P99 | Max = P99 |
| Teks kotor utterances | Mixed case, non-alfabet | Pipeline cleaning | `messageClean` konsisten |
| Integrasi dataset | 2 skema fundamentally berbeda | Opsi B+C (terpisah + enriched) | Tidak di-concat, enriched via issueId |

### Tabel Fitur Baru (Hasil Aktual)
Lihat detail di Fase 4 di atas.

---

## PERTANYAAN ANALITIK KELOMPOK 14 - Topik: Kinerja Layanan TI Organisasi

> Semua visualisasi dan temuan EDA harus dikaitkan ke salah satu pertanyaan analitik di bawah ini. Ini adalah benang merah dari Explore hingga iNterpret.

| Kode | Pertanyaan Analitik | Dataset |
|---|---|---|
| PA-1 | Faktor apa yang paling mempengaruhi durasi resolusi tiket IT? | DS1 + DS2 |
| PA-2 | Kategori atau tipe tiket mana yang paling berisiko melanggar SLA? | DS1 + DS2 |
| PA-3 | Bagaimana keparahan insiden (severity) mempengaruhi kepuasan pengguna? | DS1 |
| PA-4 | Apakah prioritas tiket yang ditetapkan konsisten dengan keparahan aktual insiden? | DS1 |
| PA-5 | Tipe tiket apa yang menunjukkan performa resolusi terbaik vs terburuk? | DS2 |

---

## FASE 8 - E-Explore

> Referensi: Panduan TugasBesar - E-Explore skor 4 memerlukan statistik deskriptif, distribusi, tren waktu, perbandingan kategori, hubungan antarvariabel, min 3 visualisasi, interpretasi tajam.

### 8A. Statistik Deskriptif [SELESAI] (Ghazy - di `03_explore.ipynb`)

**DS1 - Temuan aktual:**
| Kolom | Mean | Std | Min | Max |
|---|---|---|---|---|
| `daysOpen` / `resolutionDurationDays` | 6.80 | 7.24 | - | 31.0 |
| `severityLevel` | 2.05 | 0.38 | 0 | 4 |
| `priorityLevel` | 1.59 | 1.25 | - | - |
| `seniorityLevel` | 2.38 | 1.02 | - | - |
| `satisfactionLevel` | 1.48 | 1.20 | - | - |
| `priorityVerified` | 0.53 | - | - | - |

**DS2 - Temuan aktual:**
| Kolom | Mean | Std | Catatan |
|---|---|---|---|
| `totalTimeHours` | 18.255 | 27.594 | Right-skewed |
| `resolutionDurationHours` | 18.444 | 27.701 | Right-skewed |
| `processing_steps` | 3.16 | 2.51 | Range 0-13 |
| `timePerStepHours` | 17.450 | 27.581 | Sangat skewed |
| `issue_comments_count` | 8.64 | 13.79 | Proxy kompleksitas |
| `isResolved` | 0.99 | - | 99% resolved |
| `isComplex` | 0.20 | - | 20% tiket kompleks |
| `compositeScore` | 3.80 | 1.97 | Hanya n=360 valid |

### 8B. Distribusi [SELESAI] (Ghazy)
- DS1 Severity: "normal" dominan 90.9% -> class imbalance signifikan
- DS1 Priority: lebih merata -> lebih cocok sebagai target klasifikasi
- DS2 priority: "unknown" masih dominan 50.9% -> kualitas data rendah
- Visualisasi tersimpan: `reports/figures/viz1_distribusi_severity_priority.png`

### 8C. Tren Waktu [SELESAI] (Ghazy - DS2 saja, DS1 tidak punya timestamp)
- Volume tiket DS2 per bulan bervariasi -> ada peak period
- Avg `resolutionDurationHours` berkorelasi dengan volume -> kapasitas tim terbatas
- Visualisasi tersimpan: `reports/figures/viz2_tren_waktu_ds2.png`

### 8D. Perbandingan Kategori [SELESAI] (Ghazy)
- Cross-tab `issue_type` x `priorityNormalized`: deployment 41.1% high, ticket 12.7% high
- Cross-tab `priorityNormalized` x `isResolved`: semua priority resolved >96%
- SLA violated per issue_type: beberapa kategori >50% violated
- Visualisasi tersimpan: `reports/figures/viz3_sla_violated_per_type.png`

### 8E. Hubungan Antarvariabel [SELESAI] (Ghazy)
- Spearman heatmap DS2 & DS1 sudah dibuat
- Korelasi kuat: `totalTimeHours` <-> `resolutionDurationHours` (hampir sempurna)
- Korelasi `isComplex` <-> `wfe_reopened` -> validasi flag
- Visualisasi tersimpan: `reports/figures/viz4_heatmap_korelasi_ds2.png`, `viz4b_heatmap_korelasi_ds1.png`

**Kesimpulan untuk Modeler (PA-1, PA-4):**
| Temuan Korelasi | Implikasi untuk Model |
|---|---|
| `totalTimeHours` <-> `resolutionDurationHours` hampir sempurna (r ~= 1) | Pilih salah satu - gunakan `resolutionDurationHours` (lebih intuitif); drop `totalTimeHours` dari fitur model |
| `isComplex` <-> `wfe_reopened` tinggi | Flag `isComplex` valid sebagai fitur model - tidak redundan |
| `priorityVerified` = 53% (DS1) | Priority dan severity tidak selalu konsisten -> jangan gabungkan sebagai satu fitur |
| `seniorityLevel` <-> `resolutionDurationDays` lemah | Seniority tidak cukup prediktif untuk dijadikan fitur utama model |
| `satisfactionLevel` <-> `severityLevel` (DS1) | Perlu dieksplorasi lebih lanjut oleh Aziz di Viz 7 - potensi fitur penting |

---

## FASE 8 LANJUTAN - Visualisasi Tambahan untuk Rubrik [SELESAI] (Aziz)

> Konteks: Ghazy sudah memenuhi minimum 3 visualisasi. Aziz melanjutkan dengan visualisasi yang memperkuat interpretasi dan meningkatkan nilai rubrik E-Explore ke skor maksimal.
> File kerja: `notebooks/03_explore.ipynb` - lanjutkan setelah sel terakhir Ghazy
> Output: simpan semua gambar ke `reports/figures/` dengan format sequential `viz5_`, `viz6_`, dst.

### Viz 5 - Distribusi Durasi Resolusi DS1 [SELESAI] (Aziz)

**Tujuan:** Menunjukkan distribusi right-skewed dan perbandingan durasi antar priority label.

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df1['resolutionDurationDays'], bins=50, ax=axes[0], color='steelblue', kde=True, edgecolor='white')
mean_val = df1['resolutionDurationDays'].mean()
median_val = df1['resolutionDurationDays'].median()
axes[0].axvline(mean_val, color='red', linestyle='--', linewidth=1.5, label='Mean {:.1f} hari'.format(mean_val))
axes[0].axvline(median_val, color='orange', linestyle='--', linewidth=1.5, label='Median {:.1f} hari'.format(median_val))
pri_order = ['high', 'medium', 'low', 'unassigned']
valid_order = [p for p in pri_order if p in df1['priorityLabel'].unique()]
sns.boxplot(data=df1, x='priorityLabel', y='resolutionDurationDays', order=valid_order, ax=axes[1], palette='Set2', flierprops={'marker': 'o', 'markersize': 2, 'alpha': 0.3})
plt.savefig(FIGURES_DIR + 'viz5_durasi_resolusi_ds1.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Distribusi right-skewed: mean > median -> tiket mayoritas cepat, tapi ada outlier yang berkepanjangan
- Priority "unassigned" cenderung durasi lebih tinggi -> tidak ada pemilik tiket yang jelas
- Kaitan PA-1: priority tiket mempengaruhi kecepatan resolusi
- Kaitan PA-4: tiket high priority seharusnya paling cepat - apakah terbukti?

---

### Viz 6 - Rata-rata Durasi per Kategori `FiledAgainst` DS1 [SELESAI] (Aziz)

**Tujuan:** Identifikasi kategori IT yang paling lambat diselesaikan.

```python
ds1_avg = df1.groupby('FiledAgainst')['resolutionDurationDays'].agg(['mean','median','count','std']).reset_index()
ds1_avg.columns = ['FiledAgainst','avg_days','median_days','count','std_days']
ds1_avg = ds1_avg[ds1_avg['count'] >= 100].sort_values('avg_days', ascending=True)
overall_mean = df1['resolutionDurationDays'].mean()
colors_b = ['#d62728' if v > overall_mean*1.1 else '#ff7f0e' if v > overall_mean else '#2ca02c' for v in ds1_avg['avg_days']]
bars = ax.barh(ds1_avg['FiledAgainst'], ds1_avg['avg_days'], color=colors_b, edgecolor='white')
plt.savefig(FIGURES_DIR + 'viz6_avg_durasi_per_kategori.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Kategori warna merah (>110% rata-rata keseluruhan) butuh intervensi prioritas
- Kategori warna oranye (>rata-rata) perlu monitoring lebih ketat
- Kaitan PA-2: kategori ini paling berisiko melanggar SLA dan butuh resource tambahan

---

### Viz 7 - Satisfaction vs Severity DS1 [SELESAI] (Aziz)

**Tujuan:** Hubungan severity tiket dengan kepuasan pengguna.

```python
sev_order = ['critical','major','minor','normal','unclassified']
ct = pd.crosstab(df1['severityLabel'], df1['satisfactionLevel'], normalize='index') * 100
ct = ct.reindex(sev_order)
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
sns.heatmap(ct, annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[0], linewidths=0.5)
sev_avg = df1.groupby('severityLabel')['satisfactionLevel'].agg(['mean','sem','count']).reindex(sev_order)
plt.savefig(FIGURES_DIR + 'viz7_satisfaction_vs_severity.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Tiket critical/major memiliki distribusi satisfaction berbeda dari tiket normal
- Ada pola yang perlu diperhatikan: severity tidak selalu linear terhadap satisfaction
- Kaitan PA-3: keparahan insiden mempengaruhi pengalaman pengguna secara signifikan

---

### Viz 8 - Kecepatan Resolusi per Issue Type DS2 [SELESAI] (Aziz)

**Tujuan:** Perbandingan kecepatan resolusi antar tipe tiket DS2.

```python
valid_types = df_issues['issue_type'].value_counts()
valid_types = valid_types[valid_types >= 100].index
ds2_filtered = df_issues[df_issues['issue_type'].isin(valid_types)].copy()
ds2_filtered = ds2_filtered[ds2_filtered['resolutionSpeedCategory'].notna()]
ct2 = pd.crosstab(ds2_filtered['issue_type'], ds2_filtered['resolutionSpeedCategory'], normalize='index') * 100
ct2 = ct2.reindex(columns=['fast','medium','slow'], fill_value=0)
ct2 = ct2.sort_values('slow', ascending=True)
ct2.plot(kind='barh', stacked=True, ax=ax, color=['#2ecc71','#f39c12','#e74c3c'])
plt.savefig(FIGURES_DIR + 'viz8_speed_per_type_ds2.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Tipe tiket dengan % slow tertinggi paling berisiko untuk SLA violation
- Tipe tiket dengan % fast tinggi = benchmark best practice tim
- Kaitan PA-5: performa terbaik vs terburuk per tipe tiket teridentifikasi

---

## Pemetaan Visualisasi -> Pertanyaan Analitik

> Tabel ini memastikan setiap visualisasi punya justifikasi rubrik dan terhubung ke benang merah analitik kelompok.

| Viz | File | Judul | Pertanyaan Analitik | Kriteria Rubrik |
|---|---|---|---|---|
| Viz 1 (Ghazy) | `viz1_distribusi_severity_priority.png` | Distribusi Severity & Priority DS1 | PA-4 | Distribusi + class imbalance |
| Viz 2 (Ghazy) | `viz2_tren_waktu_ds2.png` | Tren Waktu Volume & Durasi DS2 | PA-2 | Tren waktu |
| Viz 3 (Ghazy) | `viz3_sla_violated_per_type.png` | SLA Violated per Issue Type DS2 | PA-2 | Perbandingan kategori |
| Viz 4 (Ghazy) | `viz4_heatmap_korelasi_ds2.png` + `viz4b_heatmap_korelasi_ds1.png` | Heatmap Korelasi DS2 + DS1 | PA-1 | Hubungan antarvariabel |
| Viz 5 (Aziz) | `viz5_durasi_resolusi_ds1.png` | Distribusi Durasi + Boxplot per Priority DS1 | PA-1, PA-4 | Distribusi + perbandingan kategori |
| Viz 6 (Aziz) | `viz6_avg_durasi_per_kategori.png` | Rata-rata Durasi per FiledAgainst DS1 | PA-2 | Perbandingan kategori |
| Viz 7 (Aziz) | `viz7_satisfaction_vs_severity.png` | Satisfaction vs Severity Heatmap DS1 | PA-3 | Hubungan antarvariabel |
| Viz 8 (Aziz) | `viz8_speed_per_type_ds2.png` | Kecepatan Resolusi per Issue Type DS2 | PA-5 | Perbandingan kategori |
| Viz 9 (Aziz) | `viz9_reopen_per_type_ds2.png` | Re-open Rate per Issue Type DS2 | PA-4 (eskalasi/re-open) | Perbandingan kategori |

> Semua file PNG menggunakan format sequential `viz1_` s/d `viz9_` tersimpan di `reports/figures/`.

---

## Laporan Sementara E-Explore (untuk Adam/Documentation Lead)

Format markdown untuk Bab 4 laporan dan slide presentasi.

### Tabel Temuan Eksploratif - Sudah Ada (Ghazy)

| No | Temuan | Visualisasi | Makna |
|---|---|---|---|
| 1 | DS1 Severity "normal" mendominasi 90.9% | `viz1_distribusi_severity_priority.png` | Class imbalance signifikan -> tidak ideal sebagai target klasifikasi tunggal |
| 2 | DS1 Priority lebih merata (high 36.5%) | `viz1_distribusi_severity_priority.png` | Priority lebih cocok sebagai target klasifikasi |
| 3 | DS2 volume tiket bervariasi per bulan, avgResHours berkorelasi | `viz2_tren_waktu_ds2.png` | Peak period -> risiko backlog SLA, kapasitas tim insufficient |
| 4 | Beberapa issue_type SLA violated >50% | `viz3_sla_violated_per_type.png` | Kategori kritis butuh intervensi operasional |
| 5 | Korelasi kuat: totalTimeHours <-> resolutionDurationHours | `viz4_heatmap_korelasi_ds2.png` | Kedua kolom hampir redundan -> pertimbangkan salah satu untuk model |
| 6 | isComplex berkorelasi dengan wfe_reopened | `viz4_heatmap_korelasi_ds2.png` | Flag isComplex valid sebagai proxy kompleksitas |

### Tabel Temuan Eksploratif - Ditambahkan Aziz [SELESAI]

| No | Temuan | Visualisasi | Makna |
|---|---|---|---|
| 7 | DS1 distribusi `resolutionDurationDays` right-skewed (mean=6.80, median=5.00, skew=1.31); priority "low" paling lambat (median 6 hari), priority "high" tercepat (median 5 hari) | `viz5_durasi_resolusi_ds1.png` | Mayoritas tiket diselesaikan cepat, tapi ekor panjang kanan menunjukkan ada tiket yang berkepanjangan; priority "low" paradoks lebih lambat dari "unassigned" -> perlu review SLA per priority (PA-1, PA-4) |
| 8 | Kategori "hardware" paling lambat (avg 16.94 hari, 2.49x rata-rata keseluruhan); "systems" kedua (avg 9.51 hari); "access/login" tercepat (avg 0.27 hari); dua kategori merah (hardware, systems) mencakup 50.01% volume tiket DS1 | `viz6_avg_durasi_per_kategori.png` | Hardware dan systems adalah bottleneck utama SLA di DS1 — dua kategori paling lambat sekaligus volume tinggi; access/login sangat cepat kemungkinan karena prosedur reset password yang standar (PA-2) |
| 9 | Rata-rata `satisfactionLevel` per severity: critical=1.60, major=1.61, minor=1.33, normal=1.47, unclassified=1.40; "minor" menghasilkan satisfaction paling rendah, bukan "critical" seperti yang diperkirakan | `viz7_satisfaction_vs_severity.png` | Hubungan severity-satisfaction tidak linear — "minor" lebih mengecewakan pengguna daripada "critical", kemungkinan karena ekspektasi penyelesaian cepat pada insiden kecil tidak terpenuhi; "critical" mungkin ditangani lebih cepat sehingga satisfaction lebih tinggi (PA-3) |
| 10 | DS2 tipe "subtask" paling lambat (slow 90.7%, fast hanya 1.3%); "epic" kedua paling lambat (slow 63.8%); "assistance" dan "vacation" tercepat (0% slow); "deployment" dan "service" performa baik (slow <3%) | `viz8_speed_per_type_ds2.png` | Subtask dan epic adalah tipe dengan performa resolusi terburuk — strukturnya bergantung pada tiket induk sehingga resolusinya terlambat; tipe operasional (deployment, service, hd service) menunjukkan performa terbaik dan bisa dijadikan benchmark (PA-5) |
| 11 | Kategori tertentu DS2 memiliki re-open rate jauh di atas rata-rata keseluruhan → indikator kegagalan resolusi pertama kali dan eskalasi sistemik | `viz9_reopen_per_type_ds2.png` | Kategori dengan re-open rate tinggi membutuhkan perbaikan SOP dan pelatihan agen; merupakan proxy kualitas resolusi yang tidak terlihat dari metrik durasi saja (PA-4) |

---

## Handoff ke Modeler (Aziz) - Update setelah Aziz selesai Viz

Dokumentasikan di akhir `03_explore.ipynb`:

- [x] DS1 Severity imbalanced (normal 90.9%) -> belum di-resample (sampling hanya saat training)
- [x] DS2 Priority "unknown" dominan 50.9% -> gunakan `priorityNormalized`
- [x] Tidak ada file sampled -> SMOTE dilakukan Aziz hanya pada `X_train`
- [x] Threshold `isComplex`: `wfe_reopened > 0` OR `issue_contr_count > median`
- [x] Kolom NLP: `messageClean` di `ds2UtterancesClean.csv`
- [x] DS1 `priority` - `priorityVerified` = 53% -> ada inkonsistensi, pertimbangkan drop `priorityLevel`
- [x] Scored sample: 747 baris (n=360 valid compositeScore) -> sangat kecil untuk supervised model
- [x] `performanceBinary`: good ~= 0.4%, needs_improvement ~= 0.1%, NaN 99.5% -> tidak layak supervised
- [x] Rekomendasi slide: Viz 7 (PA-3, impact tinggi), Viz 3 (SLA actionable), Viz 8 (PA-5) sebagai top-3 wajib - detail di sel penutup 03_explore.ipynb

---

## Checklist Deliverable

### Submit (sesuai instruksi pengumpulan)

| File | Format | Status |
|---|---|---|
| Dataset mentah | CSV/XLSX asli | [SELESAI] Nicholas |
| Dataset bersih (5 file) | CSV | [SELESAI] Ghazy - di `data/processed/` |
| Notebook pipeline | .ipynb reproducible | [SELESAI] Ghazy (`02_scrub.ipynb`) |
| Notebook explore | .ipynb reproducible | [SELESAI] Ghazy + Aziz (`03_explore.ipynb`) |
| Notebook model | .ipynb reproducible | [SELESAI] Aziz (`04_model.ipynb`) — lengkap dengan nilai aktual |
| Laporan akhir | PDF, struktur OSEMN | [BELUM] Adam |
| Slide presentasi | PPT/PDF, alur OSEMN | [BELUM] Adam |
| Video presentasi/demo | Link YouTube / file | [BELUM] Semua |
| README | cara jalankan, struktur folder | [SELESAI] Nicholas/Ghazy/Aziz |

### Rubrik S - Scrub (15 poin) [SELESAI] (Ghazy)

- [x] Missing value ditangani per kolom dengan alasan berdasarkan pola data (MCAR/MAR/MNAR)
- [x] Duplikasi di-handle (0 duplikasi DS1; DS2 snapshot dipertahankan sesuai desain)
- [x] Tipe data dan format distandarisasi (datetime UTC, lowercase, parse N-Label)
- [x] Outlier diidentifikasi dan ditangani (cap P99 + flag)
- [x] Integrasi 2 dataset dengan kunci dan alasan (Opsi B+C, enriched via issueId)
- [x] Min 1 fitur baru per dataset - DS1: 10 fitur baru, DS2: 12 fitur baru
- [x] Dataset bersih tersimpan di `data/processed/` (5 file CSV)
- [x] Notebook reproducible

### Rubrik E - Explore (15 poin) [SELESAI] (Ghazy + Aziz)

**Sub-elemen skor 4 (semua wajib terpenuhi):**

- [x] Statistik deskriptif variabel utama - mean, std, min, max, distribusi (Ghazy)
- [x] Distribusi variabel kunci - severity, priority, issue_type (Ghazy)
- [x] Tren waktu - volume & durasi resolusi DS2 per bulan (Ghazy)
- [x] Perbandingan kategori - SLA violated per issue_type, cross-tab priority x type (Ghazy)
- [x] Hubungan antarvariabel - Spearman heatmap DS1 & DS2 + kesimpulan fitur (Ghazy)
- [x] Min 3 visualisasi eksploratif - sudah ada 4 Ghazy (viz1–viz4) + 5 Aziz (viz5–viz9) = 9 total
- [x] Pertanyaan analitik kelompok terdefinisi eksplisit - PA-1 s/d PA-5 (di atas)
- [x] Setiap visualisasi dikaitkan ke pertanyaan analitik - lihat tabel pemetaan Viz -> PA
- [x] Viz 5 dibuat + interpretasi markdown tajam: distribusi durasi per priority DS1 (Aziz)
- [x] Viz 6 dibuat + interpretasi markdown tajam: avg durasi per kategori FiledAgainst DS1 (Aziz)
- [x] Viz 7 dibuat + interpretasi markdown tajam: satisfaction vs severity heatmap DS1 (Aziz)
- [x] Viz 8 dibuat + interpretasi markdown tajam: kecepatan resolusi per issue_type DS2 (Aziz)
- [x] Viz 9 dibuat + interpretasi markdown tajam: re-open rate per issue_type DS2 (Aziz) - PA-4 eskalasi
- [x] Interpretasi markdown viz1, viz2, viz3, viz4 ditambahkan setelah code cell masing-masing (Ghazy)
- [x] Rekomendasi slide diisi di sel penutup 03_explore.ipynb (Aziz)
- [x] Tabel temuan eksploratif No. 7-11 diisi dengan nilai aktual dari data (Aziz - SELESAI)
- [x] Semua nama file PNG diubah ke format sequential viz1_ s/d viz9_ di `reports/figures/`

---

## FASE 9 - M-Model [SELESAI - IMPLEMENTASI] (Aziz)

> **PIC:** M Azizdzaki Khrisnanurmuflih (18223128)  
> **File kerja:** `notebooks/04_model.ipynb`  
> **Referensi rubrik:** M-Model skor 4 — minimal 2 model berbeda, preprocessing fitur lengkap, evaluasi dengan metrik yang tepat (accuracy/F1/silhouette), interpretasi hasil dikaitkan ke pertanyaan analitik

### Path Dataset (PERBAIKI dari versi lama notebook)

```python
# Path yang benar — gunakan ini, bukan clean_primary.csv / clean_supporting.csv
DS1_PATH    = '../data/processed/ds1Clean.csv'
DS2_PATH    = '../data/processed/ds2IssuesClean.csv'
UTT_PATH    = '../data/processed/ds2UtterancesClean.csv'
SCORED_PATH = '../data/processed/ds2ScoredClean.csv'
FIGURES_DIR = '../reports/figures/'
```

> ✅ **Path sudah diperbaiki di `04_model.ipynb`** — notebook menggunakan path di atas dan sudah berjalan tanpa error.

### Ringkasan Fitur Tersedia per Dataset

**DS1 — `ds1Clean.csv` (100.000 baris, 22 kolom)**

| Fitur | Tipe | Catatan |
|-------|------|---------|
| `severityLevel` | ordinal int | 0–4, imbalanced (normal 90.9%) |
| `priorityLevel` | ordinal int | lebih balanced — cocok sebagai target |
| `priorityLabel` | kategorikal | **Target klasifikasi** (high/medium/low/unassigned) |
| `seniorityLevel` | ordinal int | 1–5, korelasi lemah ke durasi |
| `satisfactionLevel` | ordinal int | 1–5, KPI kepuasan |
| `resolutionDurationDays` | float | proxy durasi (= daysOpen) |
| `isLongTicket` | bool | flag durasi > P95 |
| `isHighPriority` | bool | flag prioritas tertinggi |
| `priorityVerified` | bool | konsistensi severity-priority (53% True) |
| `FiledAgainst` | kategorikal | encode sebelum dipakai sebagai fitur |
| `TicketType` | kategorikal | encode sebelum dipakai sebagai fitur |

**DS2 — `ds2IssuesClean.csv` (66.691 baris, 57 kolom)**

| Fitur | Tipe | Catatan |
|-------|------|---------|
| `resolutionDurationHours` | float | KPI utama SLA — **jangan gunakan totalTimeHours (redundan, r≈1.0)** |
| `processing_steps` | int | 0–13 |
| `issue_comments_count` | int | proxy intensitas komunikasi |
| `isComplex` | bool | flag kompleksitas (wfe_reopened>0 OR contr>median) |
| `timePerStepHours` | float | efisiensi per langkah |
| `resolutionSpeedCategory` | kategorikal | fast/medium/slow — bisa jadi target atau fitur |
| `priorityNormalized` | kategorikal | lebih bersih dari priority asli (50.9% unknown) |
| `issue_type` | kategorikal | encode untuk clustering/klasifikasi |
| `wfe_reopened` | int | jumlah re-open — terkait PA-4 |
| `isResolved` | bool | 99% True |

### 9A. Model 1 — Klasifikasi Prioritas Tiket DS1 [SELESAI] (Aziz)

**Tujuan:** Menjawab PA-1 dan PA-4 — faktor apa yang paling mempengaruhi prioritas tiket, dan apakah severity konsisten dengan priority yang ditetapkan?

**Langkah pengerjaan:**

```
1. Load ds1Clean.csv
2. Pilih fitur: severityLevel, seniorityLevel, resolutionDurationDays, isLongTicket,
               isHighPriority, FiledAgainst (encoded), TicketType (encoded)
3. Target: priorityLabel (encode: high=3, medium=2, low=1, unassigned=0)
4. Split: train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
5. Handle imbalance: SMOTE hanya pada X_train, y_train — BUKAN seluruh dataset
6. Train minimal 2 model: misal Random Forest + Decision Tree
7. Evaluasi: classification_report per kelas, confusion matrix
8. Feature importance: tampilkan top-10 fitur paling berpengaruh
9. Simpan: viz10_confusion_matrix_ds1.png, viz11_feature_importance_ds1.png
```

**Metrik wajib:**
- Accuracy keseluruhan
- Precision, Recall, F1-score per kelas (lihat classification_report)
- Confusion matrix (heatmap)

**Interpretasi yang harus ditulis di markdown cell:**
- Fitur apa yang paling berpengaruh terhadap prioritas tiket? (PA-1)
- Apakah severityLevel menjadi prediktor kuat? Jika tidak, konfirmasi temuan EDA bahwa severity-priority tidak konsisten (PA-4)

### 9B. Model 2 — Clustering Tiket DS2 [SELESAI] (Aziz)

**Tujuan:** Menjawab PA-2 dan PA-5 — identifikasi segmen tiket berdasarkan pola durasi dan kompleksitas, temukan cluster mana yang paling berisiko SLA.

**Langkah pengerjaan:**

```
1. Load ds2IssuesClean.csv
2. Pilih fitur: resolutionDurationHours, processing_steps, issue_comments_count,
               isComplex, timePerStepHours, wfe_reopened
3. Drop baris dengan NaN pada fitur tersebut
4. Scaling: StandardScaler — WAJIB sebelum K-Means
5. Elbow method: coba k=2 sampai k=8, plot inertia
6. Pilih k optimal dari elbow + silhouette score
7. Train K-Means dengan k optimal
8. Tambah kolom 'cluster' ke dataframe
9. Interpretasi tiap cluster: avg resolutionDurationHours, avg isComplex,
   dominant issue_type, % SLA violation per cluster
10. Simpan: viz12_elbow_cluster.png, viz13_cluster_profile_ds2.png
```

**Metrik wajib:**
- Silhouette score (semakin mendekati 1.0 semakin baik)
- Tabel profil tiap cluster (mean fitur per cluster)
- Distribusi issue_type per cluster

**Interpretasi yang harus ditulis di markdown cell:**
- Cluster mana yang paling berisiko SLA? (PA-2)
- Cluster mana yang menunjukkan performa terbaik vs terburuk? (PA-5)
- Apakah `isComplex` atau `wfe_reopened` menjadi pembeda cluster? (PA-4)

### 9C. Model 3 — NLP Topic Modeling DS2 Utterances [OPSIONAL] (Aziz)

**Tujuan:** Mengidentifikasi topik/pola permintaan dari teks percakapan — nilai lebih untuk rubrik.

**Langkah pengerjaan:**

```
1. Load ds2UtterancesClean.csv
2. Kolom teks: messageClean (sudah bersih dari pipe scrub)
3. Vectorize: TfidfVectorizer(max_features=5000, ngram_range=(1,2))
4. LDA: LatentDirichletAllocation(n_components=5–10, random_state=42)
5. Tampilkan top-10 kata per topik
6. Assign dominant topic per utterance
7. Plot: distribusi topik per issue_type
8. Simpan: viz14_topic_distribution_nlp.png
```

### 9D. Evaluasi & Perbandingan Model [SELESAI] (Aziz)

| Model | Dataset | Algoritma | Metrik Utama | Nilai | Pertanyaan Analitik |
|-------|---------|-----------|--------------|-------|---------------------|
| Klasifikasi Priority | DS1 | Random Forest | Accuracy | 0.6493 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Random Forest | Weighted F1 | 0.6534 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Random Forest | Macro F1 | 0.5809 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Decision Tree | Accuracy | 0.6504 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Decision Tree | Weighted F1 | 0.6536 | PA-1, PA-4 |
| Klasifikasi Priority | DS1 | Decision Tree | Macro F1 | 0.5841 | PA-1, PA-4 |
| Clustering Tiket | DS2 | K-Means (k=5) | Silhouette Score | 0.5903 | PA-2, PA-5 |
| NLP Topic Modeling | DS2 Utterances | LDA (6 topik) | Distribusi topik | 6 topik teridentifikasi | PA-3 |

**Model terpilih:** Random Forest (klasifikasi DS1) + K-Means k=5 (clustering DS2)  
**Feature importance top-3:** `isHighPriority` (75.56%) → `seniorityLevel` (15.34%) → `resolutionDurationDays` (5.15%)

### 9E. Laporan Sementara M-Model [SELESAI] (Aziz → Adam)

Tersedia lengkap di sel markdown terakhir `04_model.ipynb` dengan:
- 7 temuan utama dengan nilai aktual
- Tabel profil 5 cluster (Cluster 0–4)
- Rekomendasi spesifik untuk iNterpret (Cluster 1 = 100% slow, Cluster 2 = benchmark terbaik)
- Tabel handoff lengkap semua artefak model beserta lokasi file

---

## Checklist Rubrik M - Model (15 poin) [SELESAI] (Aziz)

> Referensi: skor 4 = minimal 2 model berbeda + preprocessing lengkap + evaluasi metrik yang tepat + interpretasi dikaitkan ke pertanyaan analitik

- [x] Path dataset diperbaiki ke `ds1Clean.csv` dan `ds2IssuesClean.csv`
- [x] Preprocessing fitur: encoding kategorikal (LabelEncoder), scaling numerik (StandardScaler)
- [x] SMOTE hanya pada `X_train` — bukan seluruh dataset
- [x] Model 1: klasifikasi prioritas DS1 — 2 algoritma dibandingkan (Random Forest + Decision Tree)
- [x] Model 1: evaluasi classification_report (precision/recall/F1 per kelas)
- [x] Model 1: confusion matrix divisualisasikan → `viz10_confusion_matrix_ds1.png`
- [x] Model 1: feature importance → `viz11_feature_importance_ds1.png`
- [x] Model 2: clustering DS2 — elbow method + silhouette score (k=2 sampai k=8)
- [x] Model 2: profil tiap cluster (rata-rata fitur, % SLA violated per cluster)
- [x] Model 2: visualisasi cluster → `viz12_elbow_cluster.png`, `viz13_cluster_profile_ds2.png`
- [x] Tabel perbandingan semua model dengan nilai aktual (bukan placeholder)
- [x] Interpretasi setiap model dikaitkan ke PA-1 s/d PA-5
- [x] Laporan Sementara M-Model di akhir notebook (7 temuan + profil cluster + rekomendasi)
- [x] Model 3 NLP — LDA topic modeling → `viz14_topic_distribution_nlp.png`
- [x] Semua model disimpan sebagai PKL di `reports/models/` (RF, DT, K-Means, LDA, encoder, scaler)
- [x] `ds2_with_clusters.csv` tersimpan untuk digunakan di `05_interpret.ipynb`
- [ ] Notebook reproducible diverifikasi: Kernel → Restart & Run All tidak error (jalankan sendiri — Aziz)
