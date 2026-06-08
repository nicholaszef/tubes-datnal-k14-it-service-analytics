# Preprocessing & EDA Plan — Kelompok 14: IT Service Analytics
> Ghazy Achmed Movlech Urbayani — 18223093 — Data Preprocessing Lead
> Cakupan: S-Scrub (full) + E-Explore (full) → Modeler hanya mengerjakan M-Model
> Referensi: II4013 Week 03 Preprocessing, Week 12 OSEMN, Panduan TugasBesar

---

## Cakupan Kerja

| OSEMN | Dikerjakan Oleh | Output |
|---|---|---|
| O - Obtain | Nicholas (Data Engineer) | Raw dataset di `data/raw/` |
| **S - Scrub** | **Ghazy** | Clean dataset, preprocessing notebook, fitur baru |
| **E - Explore** | **Ghazy** | Statistik deskriptif, min 3 visualisasi, temuan awal |
| M - Model | Daffa (Analyst/Modeler) | Model NLP, clustering, evaluasi |
| N - iNterpret | Adam (Documentation Lead) | Insight, rekomendasi, laporan |

---

## Dataset

### Dataset 1 — UCI Incident Management Event Log
- File: `data/raw/incidentEventLog.csv`
- 141.712 events, 36 kolom
- Satu incident (`number`) bisa punya banyak event — desain event log
- Tidak ada kolom teks deskripsi (eksplisit di dokumentasi UCI)
- Missing values = "unknown information" menurut sumber
- Kolom kunci: `number`, `incidentState`, `urgency` (1=High/2=Med/3=Low), `impact` (1=High/2=Med/3=Low), `priority` (auto-calc), `madeSla`, `openedAt`, `resolvedAt` (target), `closedAt` (target)
- **Dimensi waktu:** ada — `openedAt`, `resolvedAt`, `closedAt`, `sysUpdatedAt`

### Dataset 2 — Mendeley Help Desk Tickets
- Multi-file di `data/raw/`:

| File | Isi |
|---|---|
| `issues.csv` | Tiket utama — backbone |
| `issuesChangeHistory.csv` | Histori perubahan assignee/status |
| `issuesSnapshots.csv` | Duplikasi per assignee (DESAIN, bukan error) |
| `scoredIssuesSnapshotSample.xlsx` | Ground truth label score 1-5 |
| `sampleUtterances.csv` | Teks percakapan — sumber NLP |

---

## Alur OSEMN

```
[Scrub awal] → [EDA diagnostik] → [Scrub lanjutan] → [EDA final] → handoff ke Modeler
```

Scrub awal: tipe data, format, duplikat jelas
EDA diagnostik: distribusi, missing pattern, outlier, imbalance
Scrub lanjutan: berdasarkan temuan EDA
EDA final: visualisasi, temuan, interpretasi untuk laporan

---

## FASE 0 — Setup & Load

**Tujuan:** Dokumentasi baseline.

1. Load semua file dari `data/raw/`
2. Catat `.shape`, `.dtypes`, `.info()`, `.head(5)` tiap file
3. Simpan copy immutable

**Tabel dokumentasi (diisi setelah load):**

| File | Baris | Kolom | Tipe Dominan | Catatan |
|---|---|---|---|---|
| incidentEventLog.csv | 141712 | 36 | mixed | Multi-event per incident |
| issues.csv | TBD | TBD | mixed | Primary: ticket ID |
| issuesChangeHistory.csv | TBD | TBD | mixed | Join ke issues |
| issuesSnapshots.csv | TBD | TBD | mixed | Per assignee, bukan error |
| scoredIssuesSnapshotSample.xlsx | TBD | TBD | mixed | Ground truth label |
| sampleUtterances.csv | TBD | TBD | text | Hanya tiket di xlsx |

---

## FASE 1 — EDA Diagnostik

> Mengumpulkan bukti untuk keputusan Scrub. Semua keputusan di Fase 2-3 mereferensikan temuan di sini.

### 1A. Distribusi & Statistik Dasar

**DS1:**
- Value counts + persen: `incidentState`, `urgency`, `impact`, `priority`, `category`, `contactType`, `madeSla`
- Describe: `reassignmentCount`, `reopenCount`, `sysModCount`
- Cross-check: apakah `priority` konsisten dengan `urgency` × `impact`?

**DS2:**
- Value counts: `category`, `priority`, semua kolom kategorikal di issues.csv
- Describe: `timePerStep` (dalam detik)
- Cek ukuran scored sample — apakah cukup untuk supervised model?
- Verifikasi apakah semua issueId di sampleUtterances ada di scored sample

### 1B. Missing Value — Pola & Mekanisme

Klasifikasi tiap kolom: MCAR / MAR / MNAR

| Mekanisme | Artinya | Strategi |
|---|---|---|
| MCAR | Tidak berpola | Fill "Unknown" / median aman |
| MAR | Berkorelasi dengan kolom lain | Flag + sentinel |
| MNAR | Nilai itu sendiri yang menyebabkan kosong | Dokumentasikan, tangani hati-hati |

**Yang harus dicek:**
- DS1: null di `resolvedAt`/`closedAt` — apakah berkorelasi dengan `incidentState` ≠ Resolved?
- DS1: null di optional fields (`cmdbCi`, `problemId`, `rfc`, `vendor`, `causedBy`) — acak atau berpola?
- DS2: null di waktu resolusi/CSAT — apakah berkorelasi dengan status tiket Open/Pending?

### 1C. Duplikasi

- DS1: hitung baris 100% identik. Jangan hitung berdasarkan `number` saja
- DS2 issues.csv: cek apakah ticket ID unik
- DS2 issuesSnapshots.csv: verifikasi bahwa duplikasi per assignee adalah desain

### 1D. Tipe Data & Format

- Kolom timestamp yang masih `object`
- Angka tersimpan sebagai string (misal: "3 hours")
- Kategori dengan case/whitespace tidak konsisten
- Satuan `timePerStep` di DS2 (detik, menit, atau jam?)

### 1E. Outlier

Gunakan IQR method (referensi Week 03):
- DS1: `reassignmentCount`, `reopenCount`, `sysModCount`
- DS2: `timePerStep`, durasi resolusi setelah parsing
- Bedakan: data error (impossible value) vs genuine extreme case

### 1F. Class Imbalance

- DS1: distribusi `urgency`, `impact`, `madeSla`
- DS2: distribusi `priority`, distribusi score 1-5 di scored sample
- Hitung rasio mayoritas / minoritas
- Tentukan perlu sampling atau tidak (sampling hanya jika label dipakai sebagai target klasifikasi DAN rasio > 10:1)

**Aturan sampling:**
- SMOTE hanya pada training split, bukan seluruh dataset
- Simpan versi unsampled dan sampled terpisah
- Kalau hanya untuk EDA/clustering, tidak perlu sampling

---

## FASE 2 — Scrub Awal (Basic)

> Bisa dilakukan berdasarkan spesifikasi yang sudah diketahui sebelum EDA lengkap.

### DS1

- Drop baris 100% identik (semua kolom sama)
- Konversi kolom timestamp ke datetime: `openedAt`, `sysCreatedAt`, `sysUpdatedAt`, `resolvedAt`, `closedAt`
- Lowercase + strip: `incidentState`, `category`, `subcategory`, `uSymptom`, `contactType`, `closeCode`
- Dokumentasikan: berapa baris yang terpengaruh tiap langkah

### DS2

- Verifikasi relasi antar file — konfirmasi primary key
- Drop duplikat berdasarkan ticket ID di issues.csv
- Lowercase + strip kolom kategorikal di issues.csv

---

## FASE 3 — Scrub Lanjutan (Berdasarkan Temuan EDA)

> Setiap langkah harus menyebut temuan dari Fase 1.

### 3A. Handle Missing Value

Template per kolom:
```
Kolom [X]: [Y]% null
Mekanisme (dari 1B): [MCAR/MAR/MNAR] — [bukti dari data]
Keputusan: [fill Unknown / flag + sentinel / drop kolom]
Alasan: [justifikasi berdasarkan temuan]
```

Panduan umum:
- `resolvedAt`/`closedAt` null berkorelasi dengan state bukan Resolved → buat `isResolved` flag, pertahankan null
- Optional fields MCAR kecil → fill "Unknown" (didukung dokumentasi UCI)
- Kolom missing > 40% yang tidak esensial untuk model → drop kolom

### 3B. Hitung Durasi Resolusi (DS1)

- `resolutionDurationHours` = (`resolvedAt` - `openedAt`) dalam jam
- Hanya untuk baris yang sudah resolved
- Gunakan untuk analisis SLA dan clustering

### 3C. Parsing Waktu (DS2)

- Konversi kolom waktu di issues.csv ke datetime atau float jam
- `timePerStep` dari detik → `timePerStepHours` (bagi 3600)

### 3D. Cleaning Teks Utterances (DS2)

- Pipeline teks `sampleUtterances.csv`:
  1. Lowercase
  2. Hapus karakter non-alfabet
  3. Strip whitespace berlebih
- Buat `messageClean`
- Buat `wordCount` per utterance
- Drop baris dengan `wordCount` < 3

### 3E. Handle Outlier (Berdasarkan 1E)

- Cap di P99 untuk genuine extreme
- Set NaN + flag untuk impossible values (negatif, atau > batas domain wajar)
- `isComplex` flag: `reassignmentCount` > threshold ATAU `reopenCount` > threshold (tentukan dari distribusi 1E)

### 3F. Sampling (Berdasarkan 1F — jika diperlukan)

- Eksekusi hanya jika label target terbukti imbalanced dari 1F
- SMOTE hanya pada training split
- Simpan: `ds1CleanBalanced.csv`, `ds2IssuesCleanBalanced.csv` terpisah dari unsampled

---

## FASE 4 — Feature Engineering

> Referensi: OSEMN Week 12 — Scrub mencakup "impute and combine, document all transformations"

### DS1 — Fitur Baru

| Fitur | Cara Hitung | Alasan |
|---|---|---|
| `urgencyLabel` | Map 1→"high", 2→"medium", 3→"low" | Integer 1=High counter-intuitive — string lebih mudah diinterpretasi |
| `impactLabel` | Map 1→"high", 2→"medium", 3→"low" | Sama |
| `isResolved` | 1 jika `resolvedAt` tidak null | Flag bermakna — lebih informatif dari mengisi tanggal palsu |
| `slaMet` | Dari `madeSla` — verifikasi arah boolean | Kejelasan arah: True = SLA dipenuhi atau dilanggar? |
| `resolutionDurationHours` | `resolvedAt` - `openedAt` dalam jam | KPI utama analisis SLA dan clustering |
| `isComplex` | 1 jika `reassignmentCount` atau `reopenCount` > threshold | Segmentasi tiket kompleks — sesuai pertanyaan analitik kelompok |
| `priorityVerified` | Cross-check `priority` vs `urgency` × `impact` | Deteksi inkonsistensi — `priority` auto-calculated, bisa redundan |

### DS2 — Fitur Baru

| Fitur | Cara Hitung | Alasan |
|---|---|---|
| `timePerStepHours` | `timePerStep` / 3600 | Konsistensi unit dengan DS1 |
| `resolutionSpeedCategory` | qcut 3 bin dari `timePerStepHours` | qcut lebih robust untuk distribusi skewed vs cut yang bins tidak seimbang |
| `performanceBinary` | score ≥ 4 → "good", < 4 → "needs_improvement" | Multi-kelas score sangat imbalanced, binary lebih stabil untuk klasifikasi |
| `utteranceCountPerIssue` | Agregasi count dari sampleUtterances per issueId | Proxy kompleksitas tiket — lebih banyak komunikasi = lebih kompleks |

---

## FASE 5 — Integrasi Dataset

> Referensi: lec3_slides — `pd.concat` untuk vertical join tanpa shared key; Week 03 — "Label-Based Integration: merging based on matching keys"

DS1 dan DS2 tidak punya shared primary key → pilih opsi berdasarkan kebutuhan analitik.

**Opsi integrasi:**

| Opsi | Cara | Kapan |
|---|---|---|
| A: Schema alignment + concat | Samakan kolom semantik, tambah `source` | Analisis komparatif |
| B: Analisis terpisah | Tidak di-merge | Pertanyaan analitik bisa dijawab per dataset |
| C: Enrichment | Gunakan agregat satu dataset sebagai fitur di dataset lain | Ada dimensi yang bisa di-map (misal category) |

**Template dokumentasi integrasi:**

```
Kunci integrasi: [kolom yang di-align / kunci join]
Asumsi: [misal: priority DS2 ≈ urgency DS1 — ini asumsi, bukan fakta]
Limitasi: [misal: DS2 bersifat sintetis, perbandingan langsung kurang valid]
Alasan memilih opsi ini: [berdasarkan pertanyaan analitik]
```

---

## FASE 6 — Output (Simpan ke `data/processed/`)

| File | Isi |
|---|---|
| `ds1Clean.csv` | DS1 setelah seluruh cleaning dan fitur baru |
| `ds2IssuesClean.csv` | DS2 issues.csv setelah cleaning |
| `ds2UtterancesClean.csv` | sampleUtterances setelah cleaning teks |
| `ds2ScoredClean.csv` | Scored sample setelah preprocessing |
| `mergedClean.csv` | Hasil integrasi (jika opsi A/C dipilih) |
| `ds1CleanBalanced.csv` | Versi sampled DS1 (jika sampling dilakukan) |

---

## FASE 7 — Laporan Sementara S-Scrub (untuk Adam/Documentation Lead)

Format markdown untuk Bab 3 laporan. Isi berdasarkan eksekusi aktual.

### Tabel Scrub

| Masalah Data | Kondisi Awal | Tindakan Perbaikan | Kondisi Akhir |
|---|---|---|---|
| Missing value `resolvedAt` | X null (Y%) — MAR berkorelasi state | Buat flag `isResolved`, pertahankan null | 0 null, ada flag |
| Missing value optional fields | X null (Y%) — MCAR | Fill "Unknown" | 0 null |
| Duplikasi event DS1 | N baris 100% identik | Drop identical rows | - |
| Format timestamp | Object dtype | Parse ke datetime | datetime64 |
| Case tidak konsisten | "High", "high", " high " campur | lowercase + strip | konsisten |
| Outlier waktu resolusi | P99 > X jam | Cap P99 | distribusi wajar |
| Integrasi dataset | 2 skema berbeda | [isi opsi yang dipilih] | merged dengan kolom `source` |

### Tabel Fitur Baru

| Fitur | Dataset | Formula/Cara | Alasan |
|---|---|---|---|
| `isResolved` | DS1 | `resolvedAt` not null → 1 | Flag bermakna untuk incident belum selesai |
| `resolutionDurationHours` | DS1 | `resolvedAt` - `openedAt` / 3600 | KPI utama SLA |
| `urgencyLabel` | DS1 | Map integer ke string | Readability — 1=High counter-intuitive |
| `isComplex` | DS1 | reassignment/reopen > threshold | Segmentasi tiket kompleks |
| `timePerStepHours` | DS2 | detik / 3600 | Unit konsisten dengan DS1 |
| `resolutionSpeedCategory` | DS2 | qcut 3 bin dari durasi | Segmentasi kecepatan resolusi |
| `performanceBinary` | DS2 | score ≥ 4 → good | Label stabil untuk klasifikasi |

---

## FASE 8 — E-Explore (Full)

> Referensi: Panduan TugasBesar — E-Explore skor 4 memerlukan statistik deskriptif, distribusi, tren waktu, perbandingan wilayah/kategori, hubungan antarvariabel, min 3 visualisasi, interpretasi tajam.

### 8A. Statistik Deskriptif

- Tabel mean/median/std/min/max semua variabel numerik utama
- Value counts semua variabel kategorikal utama
- Cakup kedua dataset

### 8B. Distribusi

- Distribusi `urgency`, `impact`, `priority` — sebelum dan sesudah cleaning (jika ada perubahan)
- Distribusi `resolutionDurationHours` — apakah skewed?
- Distribusi score 1-5 di scored sample
- Distribusi `timePerStepHours`

### 8C. Tren Waktu

DS1 memiliki dimensi waktu (`openedAt`, `resolvedAt`):
- Volume incident per bulan/tahun
- Tren `resolutionDurationHours` dari waktu ke waktu
- Tren `madeSla` (% SLA met vs violated) per periode

### 8D. Perbandingan Kategori

- Rata-rata `resolutionDurationHours` per `category` dan `incidentState`
- % `slaMet` per `category` dan `priority`
- Distribusi `urgency` per `category`

### 8E. Hubungan Antarvariabel

- Pearson correlation matrix variabel numerik (Week 03: pakai jika distribusi normal)
- Spearman jika distribusi skewed (Week 03: lebih robust untuk non-parametric)
- Chi-square untuk pasangan kategorikal (Week 03: uji dependensi kategori)
- Cross-tabulation: `urgency` vs `impact` vs `priority` — verifikasi konsistensi

### 8F. Minimal 3 Visualisasi Eksploratif

Setiap visualisasi harus disertai interpretasi yang dikaitkan ke pertanyaan analitik.

**Visualisasi 1 — Distribusi Urgency & Impact**
- Tipe: Stacked bar chart atau grouped bar chart
- Sumbu: urgency/impact label vs count
- Interpretasi: apakah kelas terdistribusi merata? Imbalance akan berpengaruh ke model NLP
- Kaitan pertanyaan analitik: "Bagaimana karakteristik distribusi tiket ditinjau dari urgency dan impact?"

**Visualisasi 2 — Tren Volume & Durasi Resolusi per Waktu**
- Tipe: Line chart dual-axis
- Sumbu: periode (bulan/quarter) vs volume incident + rata-rata `resolutionDurationHours`
- Interpretasi: apakah ada periode dengan backlog tinggi? Apakah durasi meningkat seiring volume?
- Kaitan pertanyaan analitik: "Bagaimana pola waktu respons dan resolusi tiket?"

**Visualisasi 3 — % SLA Violated per Kategori**
- Tipe: Horizontal bar chart, urutkan descending
- Sumbu: category vs % SLA violated
- Interpretasi: kategori mana yang paling berisiko melanggar SLA?
- Kaitan pertanyaan analitik: "Kategori apa yang paling berisiko melanggar SLA?"

**Visualisasi 4 (opsional, perkuat skor E) — Heatmap Korelasi**
- Tipe: Heatmap Pearson/Spearman correlation matrix
- Variabel: semua numerik utama
- Interpretasi: ada fitur yang sangat berkorelasi tinggi? Kandidat redundan untuk model

**Visualisasi 5 (opsional) — Distribusi Score Appraisal**
- Tipe: Bar chart score 1-5 dari scored sample
- Interpretasi: apakah distribusi seimbang? Apakah perlu SMOTE untuk model appraisal?

---

## Laporan Sementara E-Explore (untuk Adam/Documentation Lead)

Format markdown untuk Bab 4 laporan dan slide presentasi.

### Tabel Temuan Eksploratif

| No | Temuan Eksploratif | Visualisasi Pendukung | Makna Awal |
|---|---|---|---|
| 1 | [isi dari hasil aktual] | Visualisasi 1 (distribusi urgency/impact) | [interpretasi dikaitkan pertanyaan analitik] |
| 2 | [isi dari hasil aktual] | Visualisasi 2 (tren waktu) | [interpretasi] |
| 3 | [isi dari hasil aktual] | Visualisasi 3 (SLA per kategori) | [interpretasi] |

---

## Handoff ke Modeler (Daffa)

Dokumentasikan di akhir notebook:

- [ ] Apakah urgency/impact masih imbalanced setelah cleaning? Sudah di-resample atau belum?
- [ ] File dataset mana yang sudah di-resample (jika ada)?
- [ ] Threshold yang dipakai untuk fitur `isComplex` (reassignment/reopen count)?
- [ ] Kolom teks terbaik untuk NLP: `messageClean` di `ds2UtterancesClean.csv`
- [ ] Apakah `priority` di DS1 redundan dan bisa di-drop? (dari cross-check 1A)
- [ ] Jumlah sampel di scored_issues — apakah cukup untuk supervised model?
- [ ] Distribusi `performanceBinary` di DS2 — berapa rasio good vs needs_improvement?

---

## Checklist Deliverable

### Submit (sesuai instruksi pengumpulan)

| File | Format | Status |
|---|---|---|
| Dataset mentah | Format sumber asli (CSV/XLSX) | Nicholas |
| Dataset bersih | CSV/XLSX | Ghazy |
| Notebook/script pipeline | .ipynb reproducible | Ghazy |
| Laporan akhir | PDF, struktur OSEMN | Adam |
| Slide presentasi | PPT/PDF, alur OSEMN | Adam |
| Video presentasi/demo | Link YouTube / file | Semua |
| README | cara jalankan, struktur folder | Nicholas/Ghazy |

### Rubrik S - Scrub (15 poin) — Skor 4

- [ ] Missing value ditangani per kolom dengan alasan berdasarkan pola data
- [ ] Duplikasi di-handle dengan memperhatikan konteks event log
- [ ] Tipe data dan format distandarisasi
- [ ] Outlier diidentifikasi dan ditangani (IQR method — Week 03)
- [ ] Integrasi 2 dataset dengan kunci dan alasan yang dijelaskan
- [ ] Min 1 fitur baru per dataset terdokumentasi
- [ ] Dataset bersih tersimpan di `data/processed/`
- [ ] Notebook reproducible

### Rubrik E - Explore (15 poin) — Skor 4

- [ ] Statistik deskriptif variabel utama
- [ ] Distribusi, tren waktu, perbandingan kategori
- [ ] Min 3 visualisasi eksploratif
- [ ] Interpretasi tajam per visualisasi
- [ ] Temuan dikaitkan ke pertanyaan analitik kelompok