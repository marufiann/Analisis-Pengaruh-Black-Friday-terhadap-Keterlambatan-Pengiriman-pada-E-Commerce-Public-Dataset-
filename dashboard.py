import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Olist Logistics Analytics", page_icon="📦", layout="wide")

# Fungsi Load Data dengan Caching untuk Efisiensi Komputasi
@st.cache_data
def load_data():
    df_q1 = pd.read_csv('dashboard_q1_clean.csv')
    df_q2 = pd.read_csv('dashboard_q2_clean.csv')
    return df_q1, df_q2

try:
    df_q1, df_q2 = load_data()
except FileNotFoundError:
    st.error("Error: File CSV tidak ditemukan. Pastikan 'dashboard_q1_clean.csv' dan 'dashboard_q2_clean.csv' ada di direktori yang sama.")
    st.stop()

# Desain Sidebar untuk Navigasi
st.sidebar.title("Navigasi Analisis")
st.sidebar.markdown("Pilih dimensi analisis metrik logistik:")
menu = st.sidebar.radio(
    "Fokus Evaluasi:",
    ("1. SLA Breach Rate (Skala Kelumpuhan)", "2. Root Cause (Seller vs Carrier)")
)

st.title("Uji Stres Logistik pada Data Set E-Commerce (Q4 2017)")
st.markdown("Dashboard ini menyajikan analisis risiko operasional terkait lonjakan keterlambatan pengiriman selama periode *Black Friday* dan *Holiday Season*.")


if menu == "1. SLA Breach Rate (Skala Kelumpuhan)":
    st.header("1. Skala Kelumpuhan Sistem Logistik")
    
    # Agregasi Data
    weekly_risk = df_q1.groupby('weekly_data').agg(
        total_orders=('order_id', 'count'),
        late_orders=('is_late', 'sum')
    ).reset_index()
    weekly_risk['rate keterlambatan (%)'] = (weekly_risk['late_orders'] / weekly_risk['total_orders']) * 100
    weekly_risk = weekly_risk.sort_values('weekly_data')

    # Kanvas Visualisasi
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.set_style("whitegrid")

    colors = ['#8b0000' if 'BLACK FRIDAY' in label else '#e74c3c' if 'Post-BF' in label else '#f39c12' if 'Dec' in label else '#3498db' for label in weekly_risk['weekly_data']]

    sns.barplot(data=weekly_risk, x='weekly_data', y='rate keterlambatan (%)', palette=colors, ax=ax)
    sns.lineplot(data=weekly_risk, x=range(len(weekly_risk)), y='rate keterlambatan (%)', marker='o', color='black', linewidth=2, alpha=0.5, ax=ax)

    oct_baseline = weekly_risk[weekly_risk['weekly_data'].str.contains('Oct')]['rate keterlambatan (%)'].mean()
    ax.axhline(oct_baseline, color='gray', linestyle='--', alpha=0.8)
    ax.text(len(weekly_risk)-1, oct_baseline + 0.5, f'Baseline Oct: {oct_baseline:.1f}%', color='gray', fontweight='bold', ha='right')

    for i, val in enumerate(weekly_risk['rate keterlambatan (%)']):
        ax.text(i, val + 0.5, f'{val:.1f}%', ha='center', fontweight='bold', fontsize=11, color='black' if val < 15 else 'red')

    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.ylabel('Persentase Telat Pengiriman (%)', fontsize=12, fontweight='bold')
    plt.xlabel('TIME FRAME Q4 2017', fontsize=12, fontweight='bold')
    sns.despine()
    
    st.pyplot(fig)

    # KESIMPULAN DARI USER
    st.markdown("### Kesimpulan Analisis")
    st.markdown("""
    Berdasarkan dari frekuensi kegagalan estimasi pengiriman dan analisis tingkat keparahan keterlambatannya, kita bisa lihat konklusi bisnis yang kritis dimana Black Friday dapat dilihat sebagai kegagalan sistemik akibat secara fundamental yang kurang baik pada kurir.

    Manajemen tidak bisa hanya melihat angka keterlambatan pengiriman (keterlambatan 20% di minggu Black Friday). Analisis severity membuktikan bahwa kualitas keterlambatan memburuk secara drastis. Pada bulan Oktober (Masa Tenang), rata-rata keterlambatan hanya berkisar 6-7 hari dengan rasio ekstrem (22%). Namun, pada masa Ripple Effect (25-30 Nov), rata-rata durasi melesat menjadi 10,2 hari, dengan 34% dari pesanan yang telat mengalami penundaan ekstrem di atas 10 hari. Ini adalah indikator hilangnya kontrol atas First-In-First-Out (FIFO) di sistem logistik.

    Hipotesis bahwa "Desember telat murni karena libur Natal" terbantahkan secara kualitas. Meskipun frekuensi pesanan telat menurun di Desember (seperti temuan di grafik pertama), tingkat keparahannya justru mencapai puncak tertinggi di akhir Desember (Dec W4+), di mana 38,7% pesanan telat mengalami extreme delay dengan rata-rata telat hampir 11 hari. Menggambarkan bahwa logistik ini tidak benar-benar pulih setelah BF, antrean paket (backlog) mengendap dan langsung ditimpa oleh Holday Season.
    """)


elif menu == "2. Root Cause (Seller vs Carrier)":
    st.header("2. Analisis Akar Masalah: Internal vs Eksternal")
    
    # Agregasi Data
    root_cause = df_q2.groupby('weekly_data').agg(
        total_orders=('order_id', 'count'),
        seller_late_count=('is_seller_late', 'sum'),
        carrier_late_count=('is_carrier_late', 'sum')
    ).reset_index()

    root_cause['seller_late_rate (%)'] = (root_cause['seller_late_count'] / root_cause['total_orders']) * 100
    root_cause['carrier_late_rate (%)'] = (root_cause['carrier_late_count'] / root_cause['total_orders']) * 100

    df_melted = pd.melt(root_cause, id_vars=['weekly_data'], value_vars=['seller_late_rate (%)', 'carrier_late_rate (%)'], var_name='Akar_Masalah', value_name='Persentase_Telat')
    df_melted['Akar_Masalah'] = df_melted['Akar_Masalah'].replace({'seller_late_rate (%)': 'Seller Telat (Proses Packing)', 'carrier_late_rate (%)': 'Kurir Telat (Logistik Eksternal)'})

    # Kanvas Visualisasi
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    sns.set_style("whitegrid")

    sns.barplot(data=df_melted, x='weekly_data', y='Persentase_Telat', hue='Akar_Masalah', palette=['#3498db', '#e74c3c'], ax=ax2)

    for p in ax2.patches:
        height = p.get_height()
        if pd.notnull(height) and height > 0: 
            ax2.annotate(f'{height:.1f}%', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, color='black', fontweight='bold', xytext=(0, 5), textcoords='offset points')

    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.ylabel('Tingkat Keterlambatan (%)', fontsize=12, fontweight='bold')
    plt.xlabel('TIME FRAME Q4 2017', fontsize=12, fontweight='bold')
    plt.legend(title='Sumber Keterlambatan:', loc='upper left')
    sns.despine()
    
    st.pyplot(fig2)


    st.markdown("### Kesimpulan Analisis")
    st.markdown("""
    Kehancuran keterlambatan estimasi pengiriman pada Black Friday 2017 murni dipicu oleh inelastisitas kapasitas logistik eksternal (Carrier), bukan kelalaian penjual (Seller). Saat sistem dihantam shock volume, tingkat kegagalan pengiriman oleh kurir meroket eksponensial dari baseline 3% menjadi 20,2%, sementara seller menunjukkan resiliensi operasional dengan kenaikan keterlambatan yang lebih tertahan di angka 16-17%. 
    
    Secara analitik, porsi kesalahan seller ini pun kemungkinan besar mengalami inflasi akibat handover illusion—sebuah kondisi di mana merchant sudah menyelesaikan packing tepat waktu, namun armada kurir gagal menjemput barang (pick-up failure) akibat kelebihan kapasitas, yang secara sistematis justru tercatat sebagai pelanggaran SLA seller. Oleh karena itu, dari kacamata manajemen risiko operasional, mitigasi pengiriman ke depan harus sepenuhnya difokuskan pada diversifikasi kontrak ekspedisi (multi-tiering logistics) untuk menyerap overflow akhir tahun seperti penambahan cabang dan armada kurir tambahan saat kondisi padat.
    """)
