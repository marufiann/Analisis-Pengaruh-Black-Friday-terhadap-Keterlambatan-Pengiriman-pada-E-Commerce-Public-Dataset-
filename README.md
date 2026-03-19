# Analisis-Pengaruh-Black-Friday-terhadap-Keterlambatan-Pengiriman-pada-E-Commerce-Public-Dataset-
Analisis Pengaruh Black Friday terhadap Keterlambatan Pengiriman pada E-Commerce Public Dataset 

#  E-Commerce Logistics Stress Test Q4 2017 (Black Friday 2017)

## Deskripsi Proyek
Proyek ini merupakan analisis mendalam terkait performa dan risiko operasional logistik pada *E-Commerce Public Dataset*. Fokus utama dari analisis ini adalah melakukan *stress-test* terhadap sistem pengiriman selama kuartal ke-4 tahun 2017 (Q4 2017), secara spesifik mengukur dampak ledakan volume transaksi pada periode **Black Friday** dan **Holiday Season**.

Analisis dibagi menjadi dua dimensi utama:
1. **Analisis Rate Keterlambatan Pengiriman:** Mengukur frekuensi dan skala kelumpuhan sistem logistik secara kronologis.
2. **Analisis Root Cause Keterlambatan:** Membedah asimetri kegagalan operasional antara pihak internal (Seller) dan pihak eksternal (Carrier/Kurir).

## Dashboard Interaktif
Hasil analisis telah divisualisasikan secara interaktif menggunakan Streamlit. 
Anda dapat mengakses dashboard tersebut melalui tautan berikut:
**https://brazil2017bf-logistic-dashboard.streamlit.app/**

## Key Insights
* **Kegagalan Sistemik Eksternal:** Krisis logistik Black Friday murni dipicu oleh inelastisitas kapasitas ekspedisi (Carrier), dengan tingkat kegagalan melonjak dari baseline 3% menjadi 20,23%.
* **The Handover Illusion:** Seller menunjukkan resiliensi operasional yang jauh lebih baik. Lonjakan rasio keterlambatan seller lebih banyak diakibatkan oleh *pick-up failure* dari pihak armada logistik yang mengalami *overcapacity*.

## Instalasi & Cara Menjalankan Secara Lokal

### Prasyarat
Pastikan Anda telah menginstal Python di sistem Anda. Proyek ini membutuhkan beberapa *library* utama seperti Pandas, Matplotlib, Seaborn, dan Streamlit.

## Setup Environment - Anaconda
```
conda create --name ecommerce-env python=3.14.2
conda activate ecommerce-env
```

##Install Requirements untuk Analisis Data ini
```
pip install -r requirements.txt
```

## Run Streamlit App
```
cd dashboard
streamlit run dashboard.py
```
