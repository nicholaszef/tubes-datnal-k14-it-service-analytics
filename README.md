# Tubes Datnal Kelompok 14
**Kinerja Layanan TI Organisasi**

Mata Kuliah: II4013 Data Analitik  
Framework: OSEMN (Obtain, Scrub, Explore, Model, iNterpret)

---

## Anggota

| NIM | Nama | Peran |
|-----|------|-------|
| 18223111 | Nicholas Zefanya Lamtyo N | Data Engineer |
| 18223093 | Ghazy Achmed Movlech Urbayani | Data Preprocessing Lead |
| 18223053 | Daffa Athalla Rajasa | Data Analyst / Modeler |
| 18223128 | M Azizdzaki Khrisnanurmuflih | Visualization / Dashboard Developer |
| 18223089 | Adam Joaquin Girsang | Documentation and Insight Lead |

---

## Setup

```bash
git clone https://github.com/[username]/tubes-datnal-k14-it-service-analytics.git
cd tubes-datnal-k14-it-service-analytics
pip install -r requirements.txt
```

---

## Menjalankan Dashboard

Dashboard interaktif dibangun menggunakan **Streamlit** dan menampilkan hasil analitik secara visual.

```bash
streamlit run dashboard/app.py
```

Dashboard akan terbuka otomatis di browser pada `http://localhost:8501`.

### Halaman Dashboard

| Halaman | Isi |
|---------|-----|
| **Overview** | Volume tiket per kategori, tren bulanan, distribusi prioritas |
| **SLA Analysis** | Breach rate per kategori × prioritas, distribusi waktu resolusi, tiket terlama |
| **Agent Performance** | Jumlah tiket per agen, waktu resolusi, SLA breach, leaderboard performa |
| **Model Results** | Confusion matrix RF, feature importance, K-Means clustering, evaluasi model |

### Filter Global (sidebar)

- **Year From / Year To** — filter rentang tahun (2016–2020)
- **Category** — Software, Hardware, Network, Access
- **Priority** — High, Medium, Low

Filter berlaku di semua halaman secara bersamaan.

---

## Menjalankan Notebook

```bash
jupyter notebook
```

---

## Pembagian Notebook

| Notebook | Dikerjakan oleh | Keterangan |
|----------|-----------------|------------|
| `notebooks/01_obtain.ipynb` | Nicholas (Data Engineer) | Preparation dan Project Setup |
| `notebooks/02_scrub.ipynb` | Ghazy (Preprocessing Lead) | Cleaning dan integrasi data |
| `notebooks/03_explore.ipynb` | Ghazy dan Aziz (Preprocessing Lead dan Visualization / Dashboard Developer) | Eksplorasi dan visualisasi |
| `notebooks/04_model.ipynb` | Aziz (Visualization / Dashboard Developer) | Pemodelan dan evaluasi |
| `notebooks/05_interpret.ipynb` | Aziz (Visualization / Dashboard Developer) | Visualisasi hasil model, insight, dan rekomendasi |

---

## Pertanyaan Analitik

| Kode | Pertanyaan Analitik |
|------|---------------------|
| PA-1 | Faktor apa yang paling mempengaruhi durasi resolusi tiket IT? |
| PA-2 | Kategori/tipe tiket mana yang paling berisiko melanggar SLA? |
| PA-3 | Bagaimana keparahan insiden mempengaruhi kepuasan pengguna? |
| PA-4 | Apakah prioritas tiket yang ditetapkan konsisten dengan keparahan aktual? |
| PA-5 | Tipe tiket apa yang menunjukkan performa resolusi terbaik vs terburuk? |

---

## Struktur Folder

```
tubes-datnal-k14-it-service-analytics/
├── dashboard/
│   ├── app.py                           (entry point Streamlit)
│   └── pages/
│       ├── 01_overview.py
│       ├── 02_sla_analysis.py
│       ├── 03_agent_performance.py
│       └── 04_model_results.py
├── data/
│   ├── raw/
│   │   ├── primary/
│   │   │   └── WA_Fn-UseC_-IT-Help-Desk.csv   (100.000 baris, dataset utama)
│   │   └── supporting/
│   │       ├── issues.csv                       (66.691 baris, dataset pendukung)
│   │       ├── issues_change_history.csv
│   │       ├── issues_snapshot.csv
│   │       └── FEATURES.md
│   └── processed/                               (diisi setelah 02_scrub selesai)
├── notebooks/
│   ├── 01_obtain.ipynb
│   ├── 02_scrub.ipynb
│   ├── 03_explore.ipynb
│   ├── 04_model.ipynb
│   └── 05_interpret.ipynb
├── requirements.txt
└── README.md
```

Folder `data/raw/` jangan diubah atau dihapus isinya.  
Semua hasil preprocessing disimpan di `data/processed/`.

---

## Dataset

**Dataset Utama:** `data/raw/primary/WA_Fn-UseC_-IT-Help-Desk.csv`  
Sumber: IBM Watson Analytics Sample Dataset  
100.000 baris, 10 kolom (TicketType, Severity, Priority, daysOpen, Satisfaction)

**Dataset Pendukung:** `data/raw/supporting/issues.csv`  
Sumber: Real-world masked helpdesk system  
Periode: Januari 2016 - Maret 2023  
66.691 baris, 57 kolom (issue_priority, issue_type, issue_created, wf_total_time)
