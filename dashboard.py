import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Analitik Logistik E-Commerce", page_icon="📊", layout="wide")
sns.set(style='darkgrid')


def create_sla_breach_df(df):
    weekly_risk = df.groupby('weekly_data').agg(
        total_orders=('order_id', 'count'),
        late_orders=('is_late', 'sum')
    ).reset_index()
    weekly_risk['sla_breach_rate (%)'] = (weekly_risk['late_orders'] / weekly_risk['total_orders']) * 100
    return weekly_risk.sort_values('weekly_data')

def create_root_cause_df(df):
    root_cause = df.groupby('weekly_data').agg(
        total_orders=('order_id', 'count'),
        seller_late_count=('is_seller_late', 'sum'),
        carrier_late_count=('is_carrier_late', 'sum')
    ).reset_index()
    root_cause['seller_late_rate (%)'] = (root_cause['seller_late_count'] / root_cause['total_orders']) * 100
    root_cause['carrier_late_rate (%)'] = (root_cause['carrier_late_count'] / root_cause['total_orders']) * 100
    
    df_melted = pd.melt(
        root_cause, 
        id_vars=['weekly_data'], 
        value_vars=['seller_late_rate (%)', 'carrier_late_rate (%)'], 
        var_name='Akar_Masalah', 
        value_name='Persentase_Telat'
    )
    df_melted['Akar_Masalah'] = df_melted['Akar_Masalah'].replace({
        'seller_late_rate (%)': 'Seller Telat (Proses Packing)', 
        'carrier_late_rate (%)': 'Kurir Telat (Logistik Eksternal)'
    })
    return df_melted

def create_severity_table(df):
    # Isolasi hanya pesanan yang gagal SLA
    late_df = df[df['is_late'] == True].copy()
    
    # Konversi ke datetime untuk kalkulasi durasi matematis
    late_df['order_delivered_customer_date'] = pd.to_datetime(late_df['order_delivered_customer_date'])
    late_df['order_estimated_delivery_date'] = pd.to_datetime(late_df['order_estimated_delivery_date'])
    
    # Kalkulasi delta hari (Keterlambatan aktual vs Estimasi)
    late_df['durasi_telat_hari'] = (late_df['order_delivered_customer_date'] - late_df['order_estimated_delivery_date']).dt.days
    
    severity_table = late_df.groupby('weekly_data').agg(
        total_pesanan_telat=('order_id', 'count'),
        rata_rata_keterlambatan_hari=('durasi_telat_hari', 'mean'),
        keterlambatan_maksimal_hari=('durasi_telat_hari', 'max')
    ).reset_index()
    
    severity_table.rename(columns={
        'weekly_data': 'Periode (Time Frame)',
        'total_pesanan_telat': 'Volume Pesanan Telat',
        'rata_rata_keterlambatan_hari': 'Rata-rata Telat (Hari)',
        'keterlambatan_maksimal_hari': 'Telat Maksimal (Hari)'
    }, inplace=True)
    
    return severity_table.sort_values('Periode (Time Frame)')


try:
    all_df = pd.read_csv("all_data_logistics.csv")
except FileNotFoundError:
    st.error("FATAL ERROR: File 'all_data_logistics.csv' tidak ditemukan di direktori lokal.")
    st.stop()

# Konversi timestamp utama
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Mengunci parameter observasi murni pada rentang dataset yang tersedia
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

with st.sidebar:
    st.markdown("## ⚙️ Parameter Analisis")
    st.markdown("Manipulasi rentang waktu observasi untuk melihat elastisitas sistem logistik:")
    
    date_range = st.date_input(
        label='Batas Waktu Observasi',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Proteksi sistem jika user hanya mengklik satu tanggal (mencegah ValueError unpacking)
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.warning("⚠️ Mohon pilih tanggal awal DAN tanggal akhir untuk merender data.")
        st.stop()

# Terapkan filter ke dataframe
main_df = all_df[(all_df["order_purchase_timestamp"].dt.date >= start_date) & 
                 (all_df["order_purchase_timestamp"].dt.date <= end_date)]

if main_df.empty:
    st.warning("Data observasi kosong pada rentang tanggal yang Anda pilih.")
    st.stop()

# Eksekusi Transformasi Data
sla_breach_df = create_sla_breach_df(main_df)
root_cause_df = create_root_cause_df(main_df)
severity_df = create_severity_table(main_df)


st.title('Analisa Pengaruh Black Friday 2017 terhadap Keterlambatan Pengiriman pada Dataset E-Commerce 2017')
st.markdown("---")

# METRIK KINERJA MAKRO
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan Diproses", value=f"{main_df['order_id'].nunique():,}")
with col2:
    total_late = main_df['is_late'].sum()
    st.metric("Total Gagal SLA (Pesanan Telat)", value=f"{total_late:,}")
with col3:
    avg_breach = (total_late / main_df['order_id'].nunique()) * 100 if main_df['order_id'].nunique() > 0 else 0
    st.metric("Rata-rata Breach Rate (Risiko)", value=f"{avg_breach:.1f}%")

st.markdown("---")


st.subheader("1. Skala Kelumpuhan Sistem Logistik (SLA Breach Rate)")

fig1, ax1 = plt.subplots(figsize=(16, 6))
colors = ['#8b0000' if 'BLACK FRIDAY' in str(label).upper() else '#e74c3c' if 'Post-BF' in str(label) else '#f39c12' if 'Dec' in str(label) else '#3498db' for label in sla_breach_df['weekly_data']]

sns.barplot(data=sla_breach_df, x='weekly_data', y='sla_breach_rate (%)', palette=colors, ax=ax1)
sns.lineplot(data=sla_breach_df, x=range(len(sla_breach_df)), y='sla_breach_rate (%)', marker='o', color='black', linewidth=2, alpha=0.5, ax=ax1)

for i, val in enumerate(sla_breach_df['sla_breach_rate (%)']):
    ax1.text(i, val + 0.5, f'{val:.1f}%', ha='center', fontweight='bold', fontsize=11, color='black')

ax1.set_ylabel('Persentase Telat Pengiriman (%)', fontsize=12, fontweight='bold')
ax1.set_xlabel('TIME FRAME', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig1)

with st.expander("Buka Interpretasi Data: Skala Kelumpuhan"):
    st.markdown("""
    Frekuensi kegagalan estimasi pengiriman meroket secara tidak proporsional selama minggu Black Friday. Grafik komparasi ini membuktikan secara fundamental bahwa infrastruktur jaringan logistik tidak memiliki elastisitas untuk menampung *volume shock* (lonjakan transaksi).
    """)

st.subheader("2. Analisis Akar Masalah (Root Cause): Seller vs Kurir")

fig2, ax2 = plt.subplots(figsize=(16, 6))
sns.barplot(data=root_cause_df, x='weekly_data', y='Persentase_Telat', hue='Akar_Masalah', palette=['#3498db', '#e74c3c'], ax=ax2)

for p in ax2.patches:
    height = p.get_height()
    if pd.notnull(height) and height > 0: 
        ax2.annotate(f'{height:.1f}%', (p.get_x() + p.get_width() / 2., height), ha='center', va='bottom', fontsize=10, fontweight='bold', xytext=(0, 5), textcoords='offset points')

ax2.set_ylabel('Tingkat Keterlambatan (%)', fontsize=12, fontweight='bold')
ax2.set_xlabel('TIME FRAME', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Sumber Tanggung Jawab (Liability):', loc='upper left')
st.pyplot(fig2)

with st.expander("Buka Interpretasi Data: Akar Masalah"):
    st.markdown("""
    Kehancuran metrik pengiriman murni dipicu oleh kelumpuhan logistik eksternal (Kurir). Terlihat kontras bahwa laju kegagalan kurir (warna merah) meningkat eksponensial jauh melampaui kelalaian internal penjual. Ini merupakan indikasi adanya fenomena *handover illusion*, di mana barang sudah diproses *seller* namun menumpuk di gudang sortir ekspedisi akibat keterbatasan armada jemput.
    """)


st.subheader("3. Matriks Keparahan Keterlambatan (Severity Analysis)")
st.markdown("Tabel berikut membedah seberapa parah durasi penundaan paket (*delay in days*) pada pesanan yang melanggar batas waktu estimasi.")

# Tampilkan dataframe dengan style formatting agar rapi
st.dataframe(
    severity_df.style.format({
        'Rata-rata Telat (Hari)': '{:.1f} Hari',
        'Telat Maksimal (Hari)': '{:.0f} Hari',
        'Volume Pesanan Telat': '{:,} Pesanan'
    }),
    use_container_width=True,
    hide_index=True
)

with st.expander("Buka Interpretasi Data: Matriks Keparahan"):
    st.markdown("""
    Manajemen tidak bisa hanya melihat probabilitas telat (20% saat Black Friday). Analisis keparahan (Severity) di atas membuktikan bahwa **kualitas** keterlambatan memburuk drastis pasca-Black Friday. Antrean paket (*backlog*) tidak berhasil diurai hingga berminggu-minggu setelah event usai, memvalidasi hipotesis hilangnya kapabilitas *First-In-First-Out* (FIFO) pada sistem gudang logistik.
    """)

