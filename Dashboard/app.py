import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configurasi tampilan Streamlit
st.set_page_config(page_title="Bike Rental Dashboard", layout="wide")

#Meload dataset
df_day = pd.read_csv("day.csv")
df_hour = pd.read_csv("hour.csv")

#Membersihkan data
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

df_day.rename(columns={'mnth':'month', 'yr':'year','temp':'temperature', 'cnt':'count', 'hum':'humidity'}, inplace=True)
df_hour.rename(columns={'hr':'hour', 'mnth':'month', 'yr':'year','temp':'temperature', 'cnt':'count', 'hum':'humidity'}, inplace=True)

df_day['year'].replace({0: '2011', 1: '2012'}, inplace=True)
df_hour['year'].replace({0: '2011', 1: '2012'}, inplace=True)

df_day.drop(['instant'],axis=1, inplace=True)
df_hour.drop(['instant'],axis=1, inplace=True)

# Normalisasi nilai temperature, atemp, humidity, dan windspeed
df_day['temperature'] = df_hour['temperature'] * 41
df_day['atemp'] = df_hour['atemp'] * 50
df_day['humidity'] = df_day['humidity'] * 100
df_day['windspeed'] = df_day['windspeed'] * 67
df_hour['temperature'] = df_hour['temperature'] * 41  
df_hour['atemp'] = df_hour['atemp'] * 50  
df_hour['humidity'] = df_hour['humidity'] * 100  
df_hour['windspeed'] = df_hour['windspeed'] * 67

st.title("Bike Sharing Anlaysis")
# Sidebar untuk navigasi halaman
st.sidebar.title("Navigasi")
page = st.sidebar.selectbox("Pilih Visualisasi", ["Halaman Utama", "Total Rental Berdasarkan Hari",
                                                   "Kelompok Penyewa Berdasarkan Jam", "Pengaruh Musim Terhadap Peminjaman Sepeda",
                                                   "Pengaruh Cuaca Dengan Jumlah Peminjam", "Perbedaan Jumlah Peminjaman Berdasarkan Jenis Pengguna",
                                                   "RFM Analisis Pengguna"])

# Halaman Utama
if page == "Halaman Utama":
    st.title("Selamat Datang di Bike Rental Dashboard")
    st.write("""
    Dashboard ini menyediakan visualisasi yang interaktif untuk melihat data peminjaman sepeda berdasarkan:
    
    1. **Jumlah Total Rental Sepeda Berdasarkan Hari dalam Seminggu**
    2. **Kelompok Penyewa Sepeda Berdasarkan Jam Penggunaannya**
    3. **Pengaruh Musim Dengan Tingkat Peminjaman Sepeda**
    4. **Pengaruh Keadaan Cuaca Dengan Jumlah Peminjaman Sepeda**
    5. **Perbedaan Jumlah Peminjaman Berdasarkan Jenis Pengguna**
    6. **RFM Analysis Pengguna Registered**
    
    Silakan pilih visualisasi yang ingin Anda lihat melalui panel sebelah kiri.
    """)

# Visualisasi pertama: Total Rental Berdasarkan Hari
elif page == "Total Rental Berdasarkan Hari":
    st.header("Pada hari apa saja rental sepeda meninggkat?")

    # Mengelompokkan data berdasarkan weekday
    weekday_rental = df_day.groupby('weekday').agg({'count': 'sum'}).reset_index()

    # Menambahkan nama hari
    weekday_rental['weekday_name'] = weekday_rental['weekday'].map({
        0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
        4: 'Friday', 5: 'Saturday', 6: 'Sunday'
    })

    weekday_rental = weekday_rental.sort_values('weekday')

    # Membuat barplot
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weekday_name', y='count', data=weekday_rental, palette='Reds', ax=ax1)
    ax1.set_title('Jumlah Total Rental Sepeda Berdasarkan Hari dalam Seminggu')
    ax1.set_xlabel('Hari Dalam Seminggu')
    ax1.set_ylabel('Total Rental Sepeda')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
    st.pyplot(fig1)

# Visualisasi kedua: Kelompok Penyewa Berdasarkan Jam
elif page == "Kelompok Penyewa Berdasarkan Jam":
    st.header("Pada jam berapa saja rental sepeda meningkat?")

    # Menghitung rata-rata penyewaan per jam
    avg_hour = df_hour.groupby('hour')['count'].mean().reset_index()

    # Menghitung Q1, Q3, dan IQR
    Q1 = avg_hour['count'].quantile(0.25)
    Q3 = avg_hour['count'].quantile(0.75)
    IQR = Q3 - Q1

    # Menentukan cluster berdasarkan rata-rata peminjaman
    avg_hour['cluster'] = ['High' if x >= Q3 else 'Low' if x <= Q1 else 'Medium' for x in avg_hour['count']]

    # Membuat barplot clustering
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    sns.barplot(x='hour', y='count', hue='cluster', data=avg_hour, palette='Reds', dodge=False, width=0.8, ax=ax2)
    ax2.set_title('Kelompok Penyewa Sepeda Berdasarkan Jam Penggunaannya')
    ax2.set_xlabel('Jam Dalam Sehari')
    ax2.set_ylabel('Rata-rata Jumlah Penyewa Sepeda')
    ax2.legend(title='Cluster')
    st.pyplot(fig2)

# Visualisasi ketiga: Pengaruh Musim Terhadap Peminjaman Sepeda
elif page == "Pengaruh Musim Terhadap Peminjaman Sepeda":
    st.header("Bagaimana pengaruh musim terhadap tingkat peminjaman sepeda?")

    # Memetakan season dengan nama musim
    df_day['season'] = df_day['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})

    # Menghitung statistik deskriptif dari peminjaman sepeda berdasarkan musim
    weather_stats = df_day.groupby('season')['count'].describe()

    #Membuat Boxplot
    #Plot peminjaman rental permusim dengan boxplot
    fig3, ax3= plt.subplots(figsize=(10, 6))
    sns.boxplot(x='season', y='count', data=df_day, palette='Reds', ax=ax3)
    # Menambahkan judul dan label sumbu
    ax3.set_title('Boxplot Peminjalam Sepeda Permusim')
    ax3.set_xlabel('Season')
    ax3.set_ylabel('Bike Rentals')
    st.pyplot(fig3)

#Viasualisasi keempat : Bagaimana pengaruh musim dengan tingkat peminjaman sepeda
elif page == "Pengaruh Cuaca Dengan Jumlah Peminjam":
    st.header("Bagaimanan Pengaruh Keadaan Cuaca Dengan Jumlah Peminjaman Sepeda?")
    # Menghitung rata-rata peminjaman sepeda berdasarkan musim
    weather_avg = df_day.groupby('weathersit')['count'].mean().reset_index()

    # Memetakan nama musim
    weather_avg['weathersit'] = weather_avg['weathersit'].map({1: 'Clear', 2: 'Mist', 3: 'Light Snow', 4: 'Heavy Rain'})
    
    # Plot peminjaman sepeda berdasarkan cuaca
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='weathersit', y='count', data=weather_avg, palette='Reds', ax=ax4)
    ax4.set_title('Rata-rata Peminjaman Sepeda Berdasarkan Cuaca')
    ax4.set_xlabel('Season')
    ax4.set_ylabel('Average Rentals')
    st.pyplot(fig4)

#Visualisasi kelima : Bagimanan Perbedaan Jumlah Peminjaman Berdasarkan Jenis Pengguna
elif page == "Perbedaan Jumlah Peminjaman Berdasarkan Jenis Pengguna":
    st.header("Bagimana Perbedaan Jumlah Peminjaman Berdasarkan Jenis Pengguna?")

    # Menghitung rata-rata peminjaman berdasarkan pengguna casual dan registered
    user_type = df_day[['casual', 'registered']].mean().reset_index()
    user_type.columns = ['user_type', 'avg_rentals']

    # Membuat barplot untuk membandingkan rata-rata peminjaman sepeda
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.barplot(x='user_type', y='avg_rentals', data=user_type, palette='Reds', ax=ax5)
    ax5.set_title('Perbandingan Peminjaman Sepeda antara Pengguna Casual dan Registered')
    ax5.set_xlabel('Tipe Pengguna')
    ax5.set_ylabel('Rata-rata Peminjaman Sepeda')
    st.pyplot(fig5)

#Visualasasi keenam: Analisis RFM untuk pengguna registered
elif page == "RFM Analisis Pengguna":
    st.header("Analisis RFM untuk pengguna registered")

    # Dapatkan tanggal terakhir untuk menghitung Recency
    last_date = df_hour['dteday'].max()

    # RFM Analysis berdasarkan 'registered' users
    rfm_regis = df_hour.groupby('registered').agg(
        Recency=('dteday', lambda x: (last_date - x.max()).days),  # Recency: Jarak hari sejak transaksi terakhir
        Frequency=('dteday', 'count'),  # Frequency: Total jumlah transaksi
        Monetary=('count', 'sum')  # Monetary: Total peminjaman sepeda
    ).reset_index()

    # Membuat list RFM features dan judul dari plot
    rfm_features = ['Recency', 'Frequency', 'Monetary']
    plot_titles = ['Distribusi Recency Pengguna Registered', 'Distribusi Frequency Pengguna Registered', 'Distribusi Monetary Pengguna Registered']
    x_labels = ['Recency (days)', 'Frequency (jumlah transaksi)', 'Monetary (total peminjaman)']

    for feature, title, xlabel in zip(rfm_features, plot_titles, x_labels):
        fig6, ax6 = plt.subplots(figsize=(10, 6))
        sns.histplot(rfm_regis[feature], bins=20, color='red', ax=ax6)
        ax6.set_title(title)
        ax6.set_xlabel(xlabel)
        ax6.set_ylabel('Jumlah Pengguna')
        st.pyplot(fig6)


