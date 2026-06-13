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
jupyter notebook
```

---

## Pembagian Notebook

| Notebook | Dikerjakan oleh | Keterangan |
|----------|-----------------|------------|
| `notebooks/01_obtain.ipynb` | Nicholas (Data Engineer) | Preparation dan Project Setup |
| `notebooks/02_scrub.ipynb` | Ghazy (Preprocessing Lead) | Cleaning dan integrasi data |
| `notebooks/03_explore.ipynb` | Daffa dan Aziz (Data Analyst dan Visualization / Dashboard Developer) | Eksplorasi dan visualisasi |
| `notebooks/04_model.ipynb` | Daffa (Data Analyst) | Pemodelan dan evaluasi |
| `notebooks/05_interpret.ipynb` | Aziz (Visualization / Dashboard Developer) | Visualisasi hasil model, insight, dan rekomendasi |


---

## Struktur Folder

```
tubes-datnal-k14-it-service-analytics/
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
