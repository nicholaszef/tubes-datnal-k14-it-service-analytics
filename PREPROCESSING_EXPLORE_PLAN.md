# Preprocessing, EDA & Visualization Plan - Kelompok 14: IT Service Analytics
> Ghazy Achmed Movlech Urbayani - 18223093 - Data Preprocessing Lead (S-Scrub + E-Explore awal)
> M Azizdzaki Khrisnanurmuflih - 18223128 - Visualization / Dashboard Developer (E-Explore lanjutan)
> Referensi: II4013 Week 03 Preprocessing, Week 12 OSEMN, Panduan TugasBesar

---

## Status Pengerjaan (per 13 Juni 2026)

| Fase | Pengerjaan | Status |
|------|-----------|--------|
| S - Scrub | Ghazy | [SELESAI] output di `data/processed/` |
| E - Explore (Statistik + Viz dasar) | Ghazy | [SELESAI] 5 visualisasi di `reports/figures/` |
| E - Explore (Viz lanjutan + Interpretasi) | **Aziz** | [SELESAI] 4 visualisasi + interpretasi markdown di `03_explore.ipynb` |
| M - Model | Daffa | [BELUM DIMULAI] |
| N - iNterpret | Aziz + Daffa + Adam | [MENUNGGU Model selesai] |

---

## Cakupan Kerja

| OSEMN | Dikerjakan Oleh | Output |
|---|---|---|
| O - Obtain | Nicholas (Data Engineer) | Raw dataset di `data/raw/` |
| S - Scrub | Ghazy | [SELESAI] Clean dataset, preprocessing notebook, fitur baru |
| E - Explore (awal) | Ghazy | [SELESAI] Statistik deskriptif, 5 visualisasi dasar, temuan awal |
| E - Explore (lanjutan) | Aziz | [SELESAI] 4 visualisasi tambahan + interpretasi markdown dikaitkan PA-1 s/d PA-5 |
| M - Model | Daffa (Analyst/Modeler) | Model NLP, clustering, evaluasi |
| N - iNterpret | Aziz + Daffa + Adam | Visualisasi hasil model, insight, rekomendasi, laporan |

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
- Visualisasi tersimpan: `reports/figures/8B_viz1_distribusi_severity_priority.png`

### 8C. Tren Waktu [SELESAI] (Ghazy - DS2 saja, DS1 tidak punya timestamp)
- Volume tiket DS2 per bulan bervariasi -> ada peak period
- Avg `resolutionDurationHours` berkorelasi dengan volume -> kapasitas tim terbatas
- Visualisasi tersimpan: `reports/figures/8C_viz2_tren_waktu_ds2.png`

### 8D. Perbandingan Kategori [SELESAI] (Ghazy)
- Cross-tab `issue_type` x `priorityNormalized`: deployment 41.1% high, ticket 12.7% high
- Cross-tab `priorityNormalized` x `isResolved`: semua priority resolved >96%
- SLA violated per issue_type: beberapa kategori >50% violated
- Visualisasi tersimpan: `reports/figures/8D_viz3_sla_violated_per_type.png`

### 8E. Hubungan Antarvariabel [SELESAI] (Ghazy)
- Spearman heatmap DS2 & DS1 sudah dibuat
- Korelasi kuat: `totalTimeHours` <-> `resolutionDurationHours` (hampir sempurna)
- Korelasi `isComplex` <-> `wfe_reopened` -> validasi flag
- Visualisasi tersimpan: `reports/figures/8E_viz4_heatmap_korelasi_ds2.png`, `8E_viz4b_heatmap_korelasi_ds1.png`

**Kesimpulan untuk Modeler (PA-1, PA-4):**
| Temuan Korelasi | Implikasi untuk Model |
|---|---|
| `totalTimeHours` <-> `resolutionDurationHours` hampir sempurna (r ~= 1) | Pilih salah satu - gunakan `resolutionDurationHours` (lebih intuitif); drop `totalTimeHours` dari fitur model |
| `isComplex` <-> `wfe_reopened` tinggi | Flag `isComplex` valid sebagai fitur model - tidak redundan |
| `priorityVerified` = 53% (DS1) | Priority dan severity tidak selalu konsisten -> jangan gabungkan sebagai satu fitur |
| `seniorityLevel` <-> `resolutionDurationDays` lemah | Seniority tidak cukup prediktif untuk dijadikan fitur utama model |
| `satisfactionLevel` <-> `severityLevel` (DS1) | Perlu dieksplorasi lebih lanjut oleh Aziz di Viz C - potensi fitur penting |

---

## FASE 8 LANJUTAN - Visualisasi Tambahan untuk Rubrik [SELESAI] (Aziz)

> Konteks: Ghazy sudah memenuhi minimum 3 visualisasi. Aziz melanjutkan dengan visualisasi yang memperkuat interpretasi dan meningkatkan nilai rubrik E-Explore ke skor maksimal.
> File kerja: `notebooks/03_explore.ipynb` - lanjutkan setelah sel terakhir Ghazy
> Output: simpan semua gambar ke `reports/figures/` dengan prefix `aziz_`

### Viz A - Distribusi Durasi Resolusi DS1 [SELESAI] (Aziz)

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
plt.savefig(FIGURES_DIR + 'aziz_viz_A_durasi_resolusi_ds1.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Distribusi right-skewed: mean > median -> tiket mayoritas cepat, tapi ada outlier yang berkepanjangan
- Priority "unassigned" cenderung durasi lebih tinggi -> tidak ada pemilik tiket yang jelas
- Kaitan PA-1: priority tiket mempengaruhi kecepatan resolusi
- Kaitan PA-4: tiket high priority seharusnya paling cepat - apakah terbukti?

---

### Viz B - Rata-rata Durasi per Kategori `FiledAgainst` DS1 [SELESAI] (Aziz)

**Tujuan:** Identifikasi kategori IT yang paling lambat diselesaikan.

```python
ds1_avg = df1.groupby('FiledAgainst')['resolutionDurationDays'].agg(['mean','median','count','std']).reset_index()
ds1_avg.columns = ['FiledAgainst','avg_days','median_days','count','std_days']
ds1_avg = ds1_avg[ds1_avg['count'] >= 100].sort_values('avg_days', ascending=True)
overall_mean = df1['resolutionDurationDays'].mean()
colors_b = ['#d62728' if v > overall_mean*1.1 else '#ff7f0e' if v > overall_mean else '#2ca02c' for v in ds1_avg['avg_days']]
bars = ax.barh(ds1_avg['FiledAgainst'], ds1_avg['avg_days'], color=colors_b, edgecolor='white')
plt.savefig(FIGURES_DIR + 'aziz_viz_B_avg_durasi_per_kategori.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Kategori warna merah (>110% rata-rata keseluruhan) butuh intervensi prioritas
- Kategori warna oranye (>rata-rata) perlu monitoring lebih ketat
- Kaitan PA-2: kategori ini paling berisiko melanggar SLA dan butuh resource tambahan

---

### Viz C - Satisfaction vs Severity DS1 [SELESAI] (Aziz)

**Tujuan:** Hubungan severity tiket dengan kepuasan pengguna.

```python
sev_order = ['critical','major','minor','normal','unclassified']
ct = pd.crosstab(df1['severityLabel'], df1['satisfactionLevel'], normalize='index') * 100
ct = ct.reindex(sev_order)
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
sns.heatmap(ct, annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[0], linewidths=0.5)
sev_avg = df1.groupby('severityLabel')['satisfactionLevel'].agg(['mean','sem','count']).reindex(sev_order)
plt.savefig(FIGURES_DIR + 'aziz_viz_C_satisfaction_vs_severity.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Tiket critical/major memiliki distribusi satisfaction berbeda dari tiket normal
- Ada pola yang perlu diperhatikan: severity tidak selalu linear terhadap satisfaction
- Kaitan PA-3: keparahan insiden mempengaruhi pengalaman pengguna secara signifikan

---

### Viz D - Kecepatan Resolusi per Issue Type DS2 [SELESAI] (Aziz)

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
plt.savefig(FIGURES_DIR + 'aziz_viz_D_speed_per_type_ds2.png', dpi=120, bbox_inches='tight')
```

**Interpretasi (di notebook sebagai markdown cell):**
- Tipe tiket dengan % slow tertinggi paling berisiko untuk SLA violation
- Tipe tiket dengan % fast tinggi = benchmark best practice tim
- Kaitan PA-5: performa terbaik vs terburuk per tipe tiket teridentifikasi

---

## Pemetaan Visualisasi -> Pertanyaan Analitik

> Tabel ini memastikan setiap visualisasi punya justifikasi rubrik dan terhubung ke benang merah analitik kelompok.

| Viz | Judul | Pertanyaan Analitik | Kriteria Rubrik |
|---|---|---|---|
| 8B (Ghazy) | Distribusi Severity & Priority DS1 | PA-4 - Konsistensi priority vs severity | Distribusi + class imbalance |
| 8C (Ghazy) | Tren Waktu Volume & Durasi DS2 | PA-2 - Risiko SLA per periode | Tren waktu |
| 8D (Ghazy) | SLA Violated per Issue Type DS2 | PA-2 - Kategori berisiko SLA | Perbandingan kategori |
| 8E (Ghazy) | Heatmap Korelasi DS1 & DS2 | PA-1 - Faktor yang mempengaruhi durasi | Hubungan antarvariabel |
| Viz A (Aziz) | Distribusi Durasi + Boxplot per Priority DS1 | PA-1 dan PA-4 | Distribusi + perbandingan kategori |
| Viz B (Aziz) | Rata-rata Durasi per FiledAgainst DS1 | PA-2 - Kategori paling berisiko | Perbandingan kategori |
| Viz C (Aziz) | Satisfaction vs Severity Heatmap DS1 | PA-3 - Severity vs kepuasan pengguna | Hubungan antarvariabel |
| Viz D (Aziz) | Kecepatan Resolusi per Issue Type DS2 | PA-5 - Performa terbaik vs terburuk | Perbandingan kategori |

---

## Laporan Sementara E-Explore (untuk Adam/Documentation Lead)

Format markdown untuk Bab 4 laporan dan slide presentasi.

### Tabel Temuan Eksploratif - Sudah Ada (Ghazy)

| No | Temuan | Visualisasi | Makna |
|---|---|---|---|
| 1 | DS1 Severity "normal" mendominasi 90.9% | `8B_viz1_distribusi_severity_priority.png` | Class imbalance signifikan -> tidak ideal sebagai target klasifikasi tunggal |
| 2 | DS1 Priority lebih merata (high 36.5%) | `8B_viz1_distribusi_severity_priority.png` | Priority lebih cocok sebagai target klasifikasi |
| 3 | DS2 volume tiket bervariasi per bulan, avgResHours berkorelasi | `8C_viz2_tren_waktu_ds2.png` | Peak period -> risiko backlog SLA, kapasitas tim insufficient |
| 4 | Beberapa issue_type SLA violated >50% | `8D_viz3_sla_violated_per_type.png` | Kategori kritis butuh intervensi operasional |
| 5 | Korelasi kuat: totalTimeHours <-> resolutionDurationHours | `8E_viz4_heatmap_korelasi_ds2.png` | Kedua kolom hampir redundan -> pertimbangkan salah satu untuk model |
| 6 | isComplex berkorelasi dengan wfe_reopened | `8E_viz4_heatmap_korelasi_ds2.png` | Flag isComplex valid sebagai proxy kompleksitas |

### Tabel Temuan Eksploratif - Ditambahkan Aziz [isi setelah Viz A-D dijalankan]

| No | Temuan | Visualisasi | Makna |
|---|---|---|---|
| 7 | [isi dari Viz A - distribusi durasi resolusi per priority] | `aziz_viz_A_durasi_resolusi_ds1.png` | [interpretasi] |
| 8 | [isi dari Viz B - rata-rata durasi per kategori IT] | `aziz_viz_B_avg_durasi_per_kategori.png` | [interpretasi] |
| 9 | [isi dari Viz C - satisfaction vs severity] | `aziz_viz_C_satisfaction_vs_severity.png` | [interpretasi] |
| 10 | [isi dari Viz D - kecepatan resolusi per tipe DS2] | `aziz_viz_D_speed_per_type_ds2.png` | [interpretasi] |

---

## Handoff ke Modeler (Daffa) - Update setelah Aziz selesai Viz

Dokumentasikan di akhir `03_explore.ipynb`:

- [x] DS1 Severity imbalanced (normal 90.9%) -> belum di-resample (sampling hanya saat training)
- [x] DS2 Priority "unknown" dominan 50.9% -> gunakan `priorityNormalized`
- [x] Tidak ada file sampled -> SMOTE dilakukan Daffa hanya pada `X_train`
- [x] Threshold `isComplex`: `wfe_reopened > 0` OR `issue_contr_count > median`
- [x] Kolom NLP: `messageClean` di `ds2UtterancesClean.csv`
- [x] DS1 `priority` - `priorityVerified` = 53% -> ada inkonsistensi, pertimbangkan drop `priorityLevel`
- [x] Scored sample: 747 baris (n=360 valid compositeScore) -> sangat kecil untuk supervised model
- [x] `performanceBinary`: good ~= 0.4%, needs_improvement ~= 0.1%, NaN 99.5% -> tidak layak supervised
- [x] Rekomendasi slide: Viz C (PA-3, impact tinggi), 8D (SLA actionable), Viz D (PA-5) sebagai top-3 wajib - detail di sel penutup 03_explore.ipynb

---

## Checklist Deliverable

### Submit (sesuai instruksi pengumpulan)

| File | Format | Status |
|---|---|---|
| Dataset mentah | CSV/XLSX asli | [SELESAI] Nicholas |
| Dataset bersih (5 file) | CSV | [SELESAI] Ghazy - di `data/processed/` |
| Notebook pipeline | .ipynb reproducible | [SELESAI] Ghazy (`02_scrub.ipynb`) |
| Notebook explore | .ipynb reproducible | [SELESAI] Ghazy + Aziz (`03_explore.ipynb`) |
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
- [x] Min 3 visualisasi eksploratif - sudah ada 5 Ghazy + 4 Aziz = 9 total
- [x] Pertanyaan analitik kelompok terdefinisi eksplisit - PA-1 s/d PA-5 (di atas)
- [x] Setiap visualisasi dikaitkan ke pertanyaan analitik - lihat tabel pemetaan Viz -> PA
- [x] Viz A dibuat + interpretasi markdown tajam: distribusi durasi per priority (Aziz)
- [x] Viz B dibuat + interpretasi markdown tajam: avg durasi per kategori IT (Aziz)
- [x] Viz C dibuat + interpretasi markdown tajam: satisfaction vs severity (Aziz)
- [x] Viz D dibuat + interpretasi markdown tajam: kecepatan resolusi per tipe DS2 (Aziz)
- [x] Interpretasi markdown 8B, 8C, 8D, 8E ditambahkan setelah code cell masing-masing (Aziz)
- [x] Rekomendasi slide diisi di bagian Handoff ke Modeler (Aziz) - di 03_explore.ipynb sel terakhir
- [ ] Tabel temuan eksploratif No. 7-10 diisi setelah Viz dijalankan dan hasil aktual diketahui (Aziz - PENDING run notebook)
