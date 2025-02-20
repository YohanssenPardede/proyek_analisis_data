import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px

# Mengatur layout menjadi full-width
st.set_page_config(layout="wide")

# Menyiapkan halaman Streamlit
st.title("Dashboard Analisis Data Penjualan E-Commerce")

# Memuat dataset
merged_data = pd.read_csv('dashboard/merged_data.csv')
 
# Pastikan data sudah dimuat dan kolom tanggal berada dalam format datetime
merged_data['order_purchase_timestamp'] = pd.to_datetime(merged_data['order_purchase_timestamp'])

# Menghitung total order dan total revenue
total_orders = merged_data['order_id'].nunique()  # Total order_id
total_revenue = merged_data['price'].sum()  # Total revenue berdasarkan kolom 'price'


# Membuat tabs di dashboard
tab1, tab2 = st.tabs(["Dashboard Utama", "Analisis RFM"])

with tab1:
    st.title("Dashboard Utama")

    # Membagi layout menjadi dua kolom untuk menampilkan metriks
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Order", value=total_orders)
    with col2:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

    # Memastikan bahwa tanggal pembelian dalam format datetime
    merged_data['order_purchase_timestamp'] = pd.to_datetime(merged_data['order_purchase_timestamp'])

    # Membagi layout menjadi dua kolom
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tren Penjualan Berdasarkan Waktu")
        # Membuat tab untuk tampilan analisis waktu tahunan, mingguan, dan waktu dalam sehari
        time_tab1, time_tab2, time_tab3 = st.tabs(["Tahunan", "Mingguan", "Waktu dalam Sehari"])

        # --- Tab Tahunan ---
        with time_tab1:
            # Menghitung jumlah pesanan per bulan
            merged_data['order_month'] = merged_data['order_purchase_timestamp'].dt.to_period("M")  # Format bulan dalam "YYYY-MM"
            monthly_order_trend = merged_data.groupby('order_month').size().reset_index(name='Jumlah Order')

            # Konversi 'order_month' ke format string untuk visualisasi
            monthly_order_trend['order_month'] = monthly_order_trend['order_month'].astype(str)

            # Visualisasi tren penjualan bulanan menggunakan Plotly
            fig1 = px.line(monthly_order_trend, x='order_month', y='Jumlah Order', markers=True,
                        title="Tren Total Order Berdasarkan Bulan")
            fig1.update_layout(xaxis_title="Bulan", yaxis_title="Jumlah Order", xaxis_tickformat='%Y-%m')
            fig1.update_xaxes(tickangle=45)  # Mengatur rotasi label bulan agar lebih terbaca
            st.plotly_chart(fig1)

        # --- Tab Mingguan ---
        with time_tab2:
            # Mengambil nama hari dari kolom tanggal
            merged_data['day_of_week'] = merged_data['order_purchase_timestamp'].dt.day_name()

            # Menghitung jumlah pesanan berdasarkan hari dalam seminggu
            daily_order_trend_weekday = merged_data.groupby('day_of_week')['order_id'].count().reset_index(name='Jumlah Order')

            # Urutkan hari dalam seminggu agar Senin muncul duluan
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_order_trend_weekday['day_of_week'] = pd.Categorical(daily_order_trend_weekday['day_of_week'], categories=days_order, ordered=True)
            daily_order_trend_weekday = daily_order_trend_weekday.sort_values('day_of_week')

            # Plot interaktif menggunakan Plotly untuk hari dalam seminggu
            fig2 = px.bar(daily_order_trend_weekday, x='day_of_week', y='Jumlah Order', title="Tren Total Order Berdasarkan Hari dalam Seminggu")
            fig2.update_layout(xaxis_title="Hari", yaxis_title="Jumlah Order")
            st.plotly_chart(fig2)

        # --- Tab Waktu dalam Sehari ---
        with time_tab3:

            # Membuat kolom baru untuk jam dari waktu pesanan
            merged_data['order_hour'] = merged_data['order_purchase_timestamp'].dt.hour

            # Mengklasifikasikan waktu pesanan ke dalam kategori pagi, siang, sore, dan malam
            def time_of_day(hour):
                if 6 <= hour < 12:
                    return 'Pagi'
                elif 12 <= hour < 18:
                    return 'Siang'
                elif 18 <= hour < 24:
                    return 'Sore'
                else:
                    return 'Malam'

            merged_data['time_of_day'] = merged_data['order_hour'].apply(time_of_day)

            # Menghitung jumlah pesanan per kategori waktu dalam sehari
            time_of_day_order_trend = merged_data['time_of_day'].value_counts().reset_index(name='Jumlah Order')
            time_of_day_order_trend.columns = ['Waktu dalam Sehari', 'Jumlah Order']

            # Plot interaktif menggunakan Plotly untuk waktu dalam sehari
            fig3 = px.bar(time_of_day_order_trend, x='Waktu dalam Sehari', y='Jumlah Order', title="Tren Total Order Berdasarkan Waktu dalam Sehari")
            fig3.update_layout(xaxis_title="Waktu dalam Sehari", yaxis_title="Jumlah Order")
            st.plotly_chart(fig3)

    with col2:
        st.subheader("Perbandingan Kategori Produk")

        # Agregasi jumlah produk terjual per kategori
        most_sold_categories = merged_data.groupby('product_category_name')['order_id'].count().sort_values(ascending=False)

        # Ambil 10 kategori dengan penjualan terbanyak
        top_10_most_sold_categories = most_sold_categories.head(10).sort_values(ascending=True)
        # Ambil 10 kategori dengan penjualan paling sedikit
        bottom_10_most_sold_categories = most_sold_categories.tail(10).sort_values(ascending=True)

        # Menghitung rata-rata harga produk per kategori
        avg_price_per_category = merged_data.groupby('product_category_name')['price'].mean().sort_values(ascending=False)

        # Menghitung rata-rata harga produk untuk kategori dengan harga tertinggi dan terendah
        top_10_categories_by_price = avg_price_per_category.head(10).sort_values(ascending=True)  # Sort untuk urutan dari besar ke kecil
        bottom_10_categories_by_price = avg_price_per_category.tail(10).sort_values(ascending=True)  # Sort untuk urutan dari besar ke kecil

        # Menghitung rata-rata biaya pengiriman per kategori
        avg_freight_per_category = merged_data.groupby('product_category_name')['freight_value'].mean().sort_values(ascending=False)

        # Mengambil 10 kategori dengan biaya pengiriman rata-rata tertinggi dan terendah
        top_10_categories_by_freight = avg_freight_per_category.head(10).sort_values(ascending=True)  # Sort untuk urutan dari besar ke kecil
        bottom_10_categories_by_freight = avg_freight_per_category.tail(10).sort_values(ascending=True)  # Sort untuk urutan dari besar ke kecil

        # Membuat tabs untuk masing-masing chart, termasuk tab baru untuk Waktu Pengiriman Terlama
        product_tab1, product_tab2, product_tab3, product_tab4 = st.tabs(["Produk Terlaris", "Harga Rata-Rata Produk", "Biaya Pengiriman Rata-Rata", "Waktu Pengiriman"])

        # --- Tab 1: Produk Paling Laku/Tidak Laku ---
        with product_tab1:
            #st.subheader("Perbandingan Produk Terlaris dan Kurang Laku")

            # Pilihan untuk memilih kategori terlaris atau kurang laku
            sold_option = st.selectbox("Pilih Kategori Produk:", ["Terlaris", "Kurang Laku"])

            if sold_option == "Terlaris":
                fig = px.bar(top_10_most_sold_categories, x=top_10_most_sold_categories.values, y=top_10_most_sold_categories.index,
                            orientation='h', title="Kategori Produk Terlaris", labels={"x": "Jumlah Terjual", "y": "Kategori Produk"})
            else:
                fig = px.bar(bottom_10_most_sold_categories, x=bottom_10_most_sold_categories.values, y=bottom_10_most_sold_categories.index,
                            orientation='h', title="Kategori Produk Kurang Laku", labels={"x": "Jumlah Terjual", "y": "Kategori Produk"})
            st.plotly_chart(fig)

        # --- Tab 2: Harga Rata-Rata Produk ---
        with product_tab2:
            # st.subheader("Perbandingan Harga Rata-Rata Produk Berdasarkan Kategori")
            
            # Pilihan untuk memilih kategori tertinggi atau terendah
            price_option = st.selectbox("Pilih Kategori Berdasarkan Harga Rata-Rata:", ["Tertinggi", "Terendah"])

            if price_option == "Tertinggi":
                fig = px.bar(top_10_categories_by_price, x=top_10_categories_by_price.values, y=top_10_categories_by_price.index,
                            orientation='h', title="Kategori Produk Berdasarkan Harga Rata-Rata Tertinggi", labels={"x": "Harga Rata-Rata", "y": "Kategori Produk"})
            else:
                fig = px.bar(bottom_10_categories_by_price, x=bottom_10_categories_by_price.values, y=bottom_10_categories_by_price.index,
                            orientation='h', title="Kategori Produk Berdasarkan Harga Rata-Rata Terendah", labels={"x": "Harga Rata-Rata", "y": "Kategori Produk"})
            st.plotly_chart(fig)

        # --- Tab 3: Biaya Pengiriman Rata-Rata ---
        with product_tab3:
            # st.subheader("Perbandingan Biaya Pengiriman Rata-Rata Berdasarkan Kategori")
            
            # Pilihan untuk memilih kategori tertinggi atau terendah
            freight_option = st.selectbox("Pilih Kategori Berdasarkan Biaya Pengiriman Rata-Rata:", ["Tertinggi", "Terendah"])

            if freight_option == "Tertinggi":
                fig = px.bar(top_10_categories_by_freight, x=top_10_categories_by_freight.values, y=top_10_categories_by_freight.index,
                            orientation='h', title="Kategori Produk Berdasarkan Biaya Pengiriman Rata-Rata Tertinggi", labels={"x": "Biaya Pengiriman Rata-Rata", "y": "Kategori Produk"})
            else:
                fig = px.bar(bottom_10_categories_by_freight, x=bottom_10_categories_by_freight.values, y=bottom_10_categories_by_freight.index,
                            orientation='h', title="Kategori Produk Berdasarkan Biaya Pengiriman Rata-Rata Terendah", labels={"x": "Biaya Pengiriman Rata-Rata", "y": "Kategori Produk"})
            st.plotly_chart(fig)

        # --- Tab 4: Waktu Pengiriman ---
        with product_tab4:
            # Pastikan kolom tanggal dalam format datetime
            merged_data['order_purchase_timestamp'] = pd.to_datetime(merged_data['order_purchase_timestamp'])
            merged_data['order_delivered_customer_date'] = pd.to_datetime(merged_data['order_delivered_customer_date'])

            # Menghitung waktu pengiriman dalam hari
            merged_data['delivery_time'] = (merged_data['order_delivered_customer_date'] - merged_data['order_purchase_timestamp']).dt.days

            # Menghitung rata-rata waktu pengiriman per kategori produk
            avg_delivery_by_category = merged_data.groupby('product_category_name')['delivery_time'].mean().sort_values(ascending=True)

            # Pilihan untuk memilih kategori dengan waktu pengiriman tercepat atau terlama
            delivery_option = st.selectbox("Pilih Kategori Berdasarkan Waktu Pengiriman:", ["Tercepat", "Terlama"])

            if delivery_option == "Tercepat":
                # Mengambil 10 kategori dengan waktu pengiriman tercepat
                top_10_fastest_delivery_categories = avg_delivery_by_category.head(10)
                fig = px.bar(top_10_fastest_delivery_categories, x=top_10_fastest_delivery_categories.values, y=top_10_fastest_delivery_categories.index,
                            orientation='h', title="Kategori Produk dengan Waktu Pengiriman Tercepat",
                            labels={"x": "Rata-Rata Waktu Pengiriman (hari)", "y": "Kategori Produk"})
            else:
                # Mengambil 10 kategori dengan waktu pengiriman terlama
                top_10_longest_delivery_categories = avg_delivery_by_category.tail(10)
                fig = px.bar(top_10_longest_delivery_categories, x=top_10_longest_delivery_categories.values, y=top_10_longest_delivery_categories.index,
                            orientation='h', title="Kategori Produk dengan Waktu Pengiriman Terlama",
                            labels={"x": "Rata-Rata Waktu Pengiriman (hari)", "y": "Kategori Produk"})

            # Menampilkan chart
            st.plotly_chart(fig)
    
    # Membagi layout menjadi dua kolom
    score_col, deliver_col = st.columns(2)

    with score_col:
        st.subheader("Faktor Mempengaruhi Skor Ulasan")
        # Hitung durasi pengiriman (jika belum ada di data)
        merged_data['delivery_time'] = (merged_data['order_delivered_customer_date'] - merged_data['order_purchase_timestamp']).dt.days

        # Menghitung frekuensi pembelian pelanggan dan skor ulasan rata-rata per pelanggan
        customer_review_freq = merged_data.groupby('customer_unique_id').agg({
            'review_score': 'mean',
            'order_id': 'count'
        }).rename(columns={'order_id': 'purchase_count'})

        # Menambahkan kolom purchase_count ke merged_data untuk kemudahan pemetaan
        merged_data = pd.merge(merged_data, customer_review_freq[['purchase_count']], on='customer_unique_id', how='left')

        # Membuat widget untuk memilih matriks yang ingin dibandingkan
        selected_metric = st.selectbox("Pilih Matriks untuk Perbandingan dengan Skor Ulasan:", 
                                    ["Harga Produk", "Biaya Pengiriman", "Durasi Pengiriman", "Metode Pembayaran", "Frekuensi Pembelian"])

        # Plot berdasarkan pilihan matriks
        if selected_metric == "Harga Produk":
            fig = px.scatter(merged_data, x='price', y='review_score', 
                            title="Harga Produk vs Skor Ulasan", labels={'price': 'Harga Produk', 'review_score': 'Skor Ulasan'},
                            opacity=0.5)
        elif selected_metric == "Biaya Pengiriman":
            fig = px.scatter(merged_data, x='freight_value', y='review_score', 
                            title="Biaya Pengiriman vs Skor Ulasan", labels={'freight_value': 'Biaya Pengiriman', 'review_score': 'Skor Ulasan'},
                            opacity=0.5, color_discrete_sequence=["green"])
        elif selected_metric == "Durasi Pengiriman":
            fig = px.scatter(merged_data, x='delivery_time', y='review_score', 
                            title="Durasi Pengiriman vs Skor Ulasan", labels={'delivery_time': 'Durasi Pengiriman (hari)', 'review_score': 'Skor Ulasan'},
                            opacity=0.5, color_discrete_sequence=["orange"])
        elif selected_metric == "Metode Pembayaran":
            fig = px.box(merged_data, x='payment_type', y='review_score', 
                        title="Metode Pembayaran vs Skor Ulasan", labels={'payment_type': 'Metode Pembayaran', 'review_score': 'Skor Ulasan'},
                        color_discrete_sequence=["#2ca02c"])
        else:
            fig = px.scatter(customer_review_freq, x='purchase_count', y='review_score', 
                            title="Frekuensi Pembelian vs Skor Ulasan", labels={'purchase_count': 'Frekuensi Pembelian', 'review_score': 'Skor Ulasan'},
                            opacity=0.5, color_discrete_sequence=["purple"])

        # Menampilkan grafik
        st.plotly_chart(fig)

    with deliver_col:
        st.subheader("Korelasi antara Waktu Pengiriman dan Rating Ulasan")
         
        # Membuat kolom review buruk (skor 1 atau 2)
        merged_data['bad_review'] = merged_data['review_score'].apply(lambda x: 1 if x <= 2 else 0)

        # Menghitung rata-rata durasi pengiriman untuk ulasan buruk dan ulasan baik
        avg_delivery_bad_review = merged_data[merged_data['bad_review'] == 1]['delivery_time'].mean()
        avg_delivery_good_review = merged_data[merged_data['bad_review'] == 0]['delivery_time'].mean()

        # Membuat box plot untuk perbandingan durasi pengiriman
        fig = px.box(merged_data, x='bad_review', y='delivery_time', 
                    color='bad_review', color_discrete_sequence=["#FF4136", "#0074D9"],
                    title="Perbandingan Durasi Pengiriman untuk Ulasan Buruk vs Ulasan Baik",
                    labels={'bad_review': 'Ulasan Buruk (1 = Ya, 0 = Tidak)', 'delivery_time': 'Durasi Pengiriman (hari)'})

        fig.update_layout(xaxis_title="Ulasan Buruk (1 = Ya, 0 = Tidak)", yaxis_title="Durasi Pengiriman (hari)")

        # Menampilkan grafik
        st.plotly_chart(fig)
        
        # Menampilkan rata-rata durasi pengiriman
        st.write(f"**Rata-rata durasi pengiriman untuk ulasan buruk:** {avg_delivery_bad_review:.2f} hari")
        st.write(f"**Rata-rata durasi pengiriman untuk ulasan baik:** {avg_delivery_good_review:.2f} hari")

with tab2:
    st.title("Analisis RFM")

    st.write("""RFM Analysis adalah metode analisis data yang digunakan untuk memahami dan mengelompokkan pelanggan berdasarkan tiga metrik utama: **Recency** (keterkinian), **Frequency** (frekuensi), dan **Monetary** (nilai moneter). Analisis ini membantu dalam mengidentifikasi pelanggan yang paling berharga, mengembangkan strategi pemasaran yang lebih efektif, dan meningkatkan loyalitas pelanggan.""")

    # Mendefinisikan tanggal terakhir berdasarkan data 'order_purchase_timestamp'
    last_date = merged_data['order_purchase_timestamp'].max() + pd.to_timedelta(1, 'D')

    # Menghitung RFM metrics
    RFM = merged_data.dropna(subset=['order_purchase_timestamp'])\
                .reset_index()\
                .groupby('customer_unique_id')\
                .agg(Recency = ('order_purchase_timestamp', lambda x: (last_date - x.max()).days),  # Recency
                     Frequency = ('order_id', 'count'),  # Frequency
                     Monetary = ('price', 'sum'))  # Monetary

    # Mengelompokkan nilai RFM
    RFM['R_score'] = pd.qcut(RFM['Recency'], 3, labels=[1, 2, 3]).astype(str)
    RFM['M_score'] = pd.qcut(RFM['Monetary'], 3, labels=[1, 2, 3]).astype(str)
    RFM['F_score'] = RFM['Frequency'].apply(lambda x: '1' if x == 1 else '2')
    RFM['RFM_score'] = RFM['R_score'] + RFM['F_score'] + RFM['M_score']

    # Segmentasi pelanggan
    def categorize_rfm_score(rfm_score):
        if rfm_score in ['333', '332', '323', '322']:
            return 'Gold'
        elif rfm_score in ['221', '222', '223', '232', '231', '233']:
            return 'Silver'
        else:
            return 'Bronze'

    RFM['segment'] = RFM['RFM_score'].apply(categorize_rfm_score)

    # Visualisasi dalam dua kolom
    rfm_col1, rfm_col2 = st.columns(2)
    # --- Kolom 1: Distribusi Pelanggan Berdasarkan Segmen ---
    # Menetapkan warna khusus untuk setiap segmen RFM
    color_map = {
        "Gold": "#FFD700",    # Warna Gold
        "Silver": "#C0C0C0",  # Warna Silver
        "Bronze": "#CD7F32"   # Warna Bronze
    }

    with rfm_col1:
        st.subheader("Distribusi Pelanggan berdasarkan Segmentasi RFM")
        if 'segment' in RFM.columns:
            # Menghitung jumlah pelanggan per segmen
            segment_counts = RFM['segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Jumlah Pelanggan']
            
            # Membuat bar chart untuk distribusi segmen pelanggan
            fig1 = px.bar(segment_counts, x='Segment', y='Jumlah Pelanggan', color='Segment', 
                        title="Distribusi Pelanggan berdasarkan Segmentasi RFM",
                        labels={'Jumlah Pelanggan': 'Jumlah Pelanggan', 'Segment': 'Segmen Pelanggan'},
                        color_discrete_map=color_map)  # Menggunakan peta warna yang ditetapkan
            
            # Menyesuaikan layout chart
            fig1.update_layout(xaxis_title="Segmen Pelanggan", yaxis_title="Jumlah Pelanggan")
            st.plotly_chart(fig1)
        else:
            st.write("Tidak ada data segmen untuk ditampilkan.")

   # --- Kolom 2: Tren Pembelian Berdasarkan Segmen Pelanggan ---
    with rfm_col2:
        st.subheader("Tren Order Berdasarkan Segmen Pelanggan")

        # Pastikan kolom 'customer_unique_id' terdapat di kedua dataframe untuk melakukan join
        RFM_with_timestamp = pd.merge(RFM, merged_data[['customer_unique_id', 'order_purchase_timestamp']], on='customer_unique_id', how='left')
        
        # Mengonversi kolom 'order_purchase_timestamp' menjadi format datetime jika belum
        RFM_with_timestamp['order_purchase_timestamp'] = pd.to_datetime(RFM_with_timestamp['order_purchase_timestamp'])
        
        # Menambahkan kolom bulan untuk analisis tren per bulan
        RFM_with_timestamp['bulan_pembelian'] = RFM_with_timestamp['order_purchase_timestamp'].dt.to_period('M')
        
        # Menghitung jumlah order per bulan per segmen
        segmen_trend = RFM_with_timestamp.groupby(['bulan_pembelian', 'segment']).size().reset_index(name='jumlah_order')
        
        # Konversi 'bulan_pembelian' ke format string untuk visualisasi
        segmen_trend['bulan_pembelian'] = segmen_trend['bulan_pembelian'].astype(str)
        
        # Membuat line chart untuk tren order per segmen
        fig2 = px.line(segmen_trend, x='bulan_pembelian', y='jumlah_order', color='segment', markers=True,
                    title='Tren Order Berdasarkan Segmen Pelanggan',
                    color_discrete_map=color_map)  # Menggunakan peta warna yang ditetapkan

        fig2.update_layout(xaxis_title='Bulan Pembelian', yaxis_title='Jumlah Order', xaxis_tickangle=45)
        st.plotly_chart(fig2)

    # Visualisasi dalam dua kolom
    product_rfm_col, paynment_rfm_col = st.columns(2)

    with product_rfm_col:
        st.subheader("Distribusi Produk berdasarkan Segmentasi RFM")
        
        # Menggabungkan data RFM dengan kategori produk
        RFM_category = pd.merge(RFM, merged_data[['customer_unique_id', 'product_category_name']],
                                left_on='customer_unique_id', right_on='customer_unique_id', how='left')

        # Menghitung jumlah produk paling banyak dibeli untuk setiap segmen
        top_categories_by_segment = RFM_category.groupby(['segment', 'product_category_name']).size().reset_index(name='count')

        # Membuat widget opsi untuk memilih segmen dan jenis produk (terlaris atau kurang laku)
        selected_segment = st.selectbox("Pilih Segmen Pelanggan:", ["Gold", "Silver", "Bronze"], key="segment_selection_unique")
        product_option = st.selectbox("Pilih Jenis Produk:", ["Produk Terlaris", "Produk Kurang Laku"], key="product_option_unique")

        # Filter data berdasarkan segmen yang dipilih
        if product_option == "Produk Terlaris":
            # Mengambil 5 produk terlaris
            filtered_data = top_categories_by_segment[top_categories_by_segment['segment'] == selected_segment].nlargest(5, 'count')
        else:
            # Mengambil 5 produk kurang laku
            filtered_data = top_categories_by_segment[top_categories_by_segment['segment'] == selected_segment].nsmallest(5, 'count')

        # Membuat plot bar menggunakan Plotly
        fig = px.bar(filtered_data, x='count', y='product_category_name', orientation='h',
                    title=f"{product_option} - Segmen {selected_segment}",
                    labels={'count': 'Jumlah Pembelian', 'product_category_name': 'Kategori Produk'},
                    color='segment',  # Menentukan segmen sebagai warna
                    color_discrete_map=color_map)  # Gunakan color_map untuk konsistensi warna

        # Mengatur urutan kategori dan label pada grafik
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Jumlah Pembelian', yaxis_title='Kategori Produk')

        # Menampilkan grafik
        st.plotly_chart(fig)

    with paynment_rfm_col:
        st.subheader("Distribusi Metode Pembayaran berdasarkan Segmentasi RFM")
        
        # Menggabungkan data RFM dengan payment_type
        RFM_payment_method = pd.merge(RFM, merged_data[['customer_unique_id', 'payment_type']],
                                    left_on='customer_unique_id', right_on='customer_unique_id', how='left')

        # Menghitung jumlah penggunaan setiap metode pembayaran per segmen
        payment_method_by_segment = RFM_payment_method.groupby(['segment', 'payment_type']).size().reset_index(name='count')

        # Membuat widget opsi untuk memilih segmen, dengan key unik
        selected_segment = st.selectbox("Pilih Segmen Pelanggan:", ["Gold", "Silver", "Bronze"], key="payment_segment_selection")

        # Filter data berdasarkan segmen yang dipilih
        filtered_data = payment_method_by_segment[payment_method_by_segment['segment'] == selected_segment]

        # Membuat plot bar menggunakan Plotly dengan color_discrete_map
        fig = px.bar(filtered_data, x='count', y='payment_type', orientation='h',
                    title=f"Metode Pembayaran - Segmen {selected_segment}",
                    labels={'count': 'Jumlah Penggunaan', 'payment_type': 'Metode Pembayaran'},
                    color='segment',  # Menentukan segmen sebagai warna
                    color_discrete_map=color_map)  # Gunakan color_map untuk konsistensi warna

        # Mengatur urutan kategori dan label pada grafik
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title='Jumlah Penggunaan', yaxis_title='Metode Pembayaran')

        # Menampilkan grafik
        st.plotly_chart(fig)
