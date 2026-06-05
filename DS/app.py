import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ============================================
# PAGE CONFIG
# ============================================

st.set_page_config(
    page_title="Wallee",
    page_icon="Wallee Logo.png",
    layout="wide"
)

# ============================================
# LOGO
# ============================================

logo = Image.open("Wallee Logo.png")

# ============================================
# LOAD DATA
# ============================================

@st.cache_data

def load_data():
    df = pd.read_csv("feature_engineered_finance_dataset.csv")
    return df


df = load_data()

# ============================================
# SIDEBAR
# ============================================

st.sidebar.image(
    logo,
    width=100
)

# ============================================
# DATE FILTER
# ============================================

df["date"] = pd.to_datetime(df["date"])

min_date = df["date"].min()
max_date = df["date"].max()

start_date = st.sidebar.date_input(
    "Start Date",
    min_date
)

end_date = st.sidebar.date_input(
    "End Date",
    max_date
)

filtered_date_df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# use filtered dataframe

df = filtered_date_df


menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Categorization",
        "Behavior Analysis"
    ]
)


# ============================================
# USER FILTER
# ============================================

selected_user = st.sidebar.selectbox(
    "👤 Select User",
    sorted(df["user_id"].unique())
)

# FILTER USER DATA

df = df[
    df["user_id"] == selected_user
]

if df.empty:
    st.warning("⚠️ Tidak ada transaksi untuk filter yang dipilih.")
    st.stop()

# ============================================
# GLOBAL METRICS
# ============================================

total_transactions = len(df)

total_spending = df["total_harga"].sum()

avg_spending = df["total_harga"].mean()

food_spending = (
    df[df["kategori"] == "makanan & minuman"]
    ["total_harga"]
    .sum()
)

food_ratio = (
    food_spending / total_spending
    if total_spending > 0
    else 0
)

# digital_ratio = (
#     df["is_digital_payment"]
#     .mean()
# )

weekend_spending = (
    df[df["is_weekend"] == 1]
    ["total_harga"]
    .sum()
)

weekday_spending = (
    df[df["is_weekend"] == 0]
    ["total_harga"]
    .sum()
)

total_transactions = len(df)
avg_spending = df["total_harga"].mean()

digital_ratio = (
    df["is_digital_payment"]
    .mean()
)

weekday_spending = (
    df[df["is_weekend"] == 0]
    ["total_harga"]
    .sum()
)

def format_rupiah(x):

    if x >= 1_000_000_000:
        return f"Rp {x/1_000_000_000:.0f} M"

    elif x >= 1_000_000:
        return f"Rp {x/1_000_000:.0f} Jt"

    elif x >= 1_000:
        return f"Rp {x/1_000:.0f} Rb"

    else:
        return f"Rp {x:,.0f}"

    # ============================================
    # FINANCIAL HEALTH SCORE
    # ============================================

score = 100

if food_ratio > 0.40:
    score -= 15

if digital_ratio > 0.80:
    score -= 10

if weekend_spending > weekday_spending:
    score -= 10

if total_spending > 3000000:
    score -= 15

# ============================================
# DASHBOARD
# ============================================

if menu == "Dashboard":

    st.title("💸 Wallee: Smart Money, Happy Life")

    left, right = st.columns([3,1])

    with left:

        st.markdown(
            f"### 👤 User: {selected_user}"
        )

    with right:

        st.metric(
            "💰 Financial Health",
            f"{score}/100"
        )

    top_category = (
        df["kategori"].value_counts().idxmax()
        if not df.empty else "-"
    )

    top_merchant = (
        df["merchant"].value_counts().idxmax()
        if not df.empty else "-"
    )

    # ====================================
    # BEHAVIOR METRICS
    # ====================================

    food_spending = (
        df[
            df["kategori"] == "makanan & minuman"
        ]["total_harga"]
        .sum()
    )

    food_ratio = (
        food_spending / total_spending
        if total_spending > 0
        else 0
    )

    digital_ratio = (
        df["is_digital_payment"]
        .mean()
    )

    weekend_spending = (
        df[df["is_weekend"] == 1]
        ["total_harga"]
        .sum()
    )

    weekday_spending = (
        df[df["is_weekend"] == 0]
        ["total_harga"]
        .sum()
    )

    # ====================================
    # FINANCIAL HEALTH SCORE
    # ====================================

    score = 100

    if food_ratio > 0.40:
        score -= 15

    if digital_ratio > 0.80:
        score -= 10

    if weekend_spending > weekday_spending:
        score -= 10

    if total_spending > 3000000:
        score -= 15

    st.divider()

    col1, col2 = st.columns([1,3])

    with col1:

        if score >= 80:

            status = "🟢 Sehat"

            recommendation = """
            Pola pengeluaran Anda tergolong sehat.
            Pertahankan kebiasaan mencatat transaksi dan mengontrol pengeluaran rutin.
            """

        elif score >= 60:

            status = "🟡 Perlu Perhatian"

            recommendation = """
            Terdapat beberapa pola pengeluaran yang perlu diperhatikan.
            Evaluasi kategori dengan pengeluaran terbesar untuk menghindari pemborosan.
            """

        else:

            status = "🔴 Risiko Overspending"

            recommendation = """
            Risiko pengeluaran berlebih cukup tinggi.
            Fokus pada pengurangan pengeluaran non-prioritas dan buat batas anggaran bulanan.
            """
            st.success(
                f"""
            ### 💰 Kesehatan Finansial

            Skor Finansial: **{score}/100**

            Status: **{status}**

            ### Rekomendasi

            {recommendation}
            """
            )
        

    # ====================================
    # KPI CARDS
    # ====================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Transactions",
        total_transactions
    )

    c2.metric(
        label="💰 Total Spending",
        value=format_rupiah(total_spending),
        help=f"Nilai asli: Rp {total_spending:,.0f}"
    )

    c3.metric(
        "Top Category",
        top_category,
        help=f" {top_category}"
    )

    c4.metric(
        "Top Merchant",
        top_merchant
    )

    # ====================================
    # MONTHLY TREND
    # ====================================


    monthly_df = (
        df
        .groupby("month")["total_harga"]
        .sum()
        .reset_index()
    )

    month_names = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
    }

    monthly_df["nama_bulan"] = (
        monthly_df["month"]
        .map(month_names)
    )

    monthly_df["label_rp"] = monthly_df["total_harga"].apply(
        format_rupiah
    )

    fig_month = px.line(
        monthly_df,
        x="nama_bulan",
        y="total_harga",
        markers=True,
        title="Monthly Spending Trend"
    )

    max_value = monthly_df["total_harga"].max()

    monthly_df["highlight"] = (
        monthly_df["total_harga"] == max_value
    )

    fig_month.add_scatter(
        x=monthly_df[
            monthly_df["highlight"]
        ]["nama_bulan"],

        y=monthly_df[
            monthly_df["highlight"]
        ]["total_harga"],

        mode="markers",

        marker=dict(
            size=18,
            color="red"
        ),

        name="Peak Spending"
    )

    fig_month.update_traces(
        line=dict(width=4),
        marker=dict(size=10),
        hovertemplate=
        "<b>%{x}</b><br>" +
        "Pengeluaran: Rp %{y:,.0f}<extra></extra>"
    )
    fig_month.update_layout(
        yaxis_title="Total Spending (Rp)",
        xaxis_title="Bulan",
        hovermode="x unified"
    )

    st.divider()

    col1, col2 = st.columns([2,1])

    with col1:

        st.plotly_chart(
            fig_month,
            use_container_width=True
        )

    with col2:

        peak_month = (
            monthly_df
            .sort_values(
                "total_harga",
                ascending=False
            )
            .iloc[0]
        )
        
        month_name = month_names[
        int(peak_month["month"])
        ]

        peak_ratio = (
        peak_month["total_harga"]
        / monthly_df["total_harga"].mean()
        )

        if peak_ratio > 1.5:
            status = "🔴 Sangat Tinggi"
        elif peak_ratio > 1.2:
            status = "🟡 Tinggi"
        else:
            status = "🟢 Normal"

        st.write("#### 💡 Pengeluaran")
        
        st.info(
                f"""

        **📅 Periode Tertinggi**

        Pengeluaran tertinggi terjadi pada **Bulan {month_name}** dengan total pengeluaran sebesar **Rp {peak_month['total_harga']:,.0f}**.
        
        **Status:** {status}
        """
        )

        st.warning(
            """
        **📌 Rekomendasi**:
        Tinjau kembali transaksi pada periode ini.
        Pertimbangkan menetapkan batas anggaran bulanan agar pengeluaran lebih terkontrol.
        """
            )
        
    # ====================================
    # WEEKEND VS WEEKDAY ANALYSIS
    # ====================================
    weekend_df = pd.DataFrame({
        "Periode": [
            "Weekday",
            "Weekend"
        ],
        "Total Spending": [
            weekday_spending,
            weekend_spending
        ]
    })

    fig_weekend = px.pie(
        weekend_df,
        names="Periode",
        values="Total Spending",
        hole=0.5,
        title="Weekend vs Weekday Spending",
        color_discrete_sequence=[
            "#0B3D91",
            "#9EC5FE"
        ]
    )

    fig_weekend.update_traces(
        hovertemplate=
        "<b>%{label}</b><br>" +
        "Total Pengeluaran: Rp %{value:,.0f}<br>" +
        "Persentase: %{percent}<extra></extra>"
    )

    st.divider()

    left, right = st.columns([2,1])

    with left:

        st.plotly_chart(
            fig_weekend,
            use_container_width=True
        )

    with right:
        weekend_ratio = (
            weekend_spending
            /
            total_spending
            * 100
        ) if total_spending > 0 else 0
        if weekend_ratio >= 50:

            status = "🔴 Tinggi"

            recommendation = """
            Sebagian besar pengeluaran terjadi pada akhir pekan.
            Pertimbangkan menetapkan batas pengeluaran untuk aktivitas rekreasi atau hiburan.
            """

        elif weekend_ratio >= 35:

            status = "🟡 Sedang"

            recommendation = """
            Pengeluaran akhir pekan cukup signifikan.
            Tetap pantau transaksi agar tidak melebihi anggaran bulanan.
            """

        else:

            status = "🟢 Normal"

            recommendation = """
            Distribusi pengeluaran antara hari kerja dan akhir pekan cukup seimbang.
            """

            st.write("### 📅 Spending Pattern")

            st.info(
                f"""
                Pengeluaran akhir pekan mencapai **{weekend_ratio:.1f}%**
                dari total pengeluaran.

                Status: **{status}**
                """
            )

            st.warning(
                f"""
                📌 Rekomendasi:

                {recommendation}
                """
            )
    # ====================================
    # CATEGORY ANALYSIS
    # ====================================

    category_df = (
        df["kategori"]
        .value_counts()
        .reset_index()
    )

    category_df.columns = [
        "kategori",
        "count"
    ]

    colors = [
        "#0B3D91"
        if x == category_df["count"].max()
        else "#9EC5FE"
        for x in category_df["count"]
    ]

    fig_category = px.bar(
        category_df,
        x="kategori",
        y="count",
        title="Distribusi Kategori",
        labels={
            "count": "Jumlah Transaksi",
            "kategori": "Kategori"
        }
    )

    fig_category.update_traces(
        marker_color=colors,
        hovertemplate=
        "<b>%{x}</b><br>" +
        "Jumlah Transaksi: %{y}<extra></extra>"
    )

    st.divider()

    left, right = st.columns([2,1])

    with left:

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    with right:

        dominant_cat = (
            category_df.iloc[0]["kategori"]
        )

        ratio = (
            category_df.iloc[0]["count"]
            /
            category_df["count"].sum()
        ) * 100

        st.write("#### 🍔 Top Kategori")

        st.info(
            f"""
        Kategori dengan transaksi terbanyak: **{dominant_cat}** dengan kontribusi sebesar **{ratio:.1f}%**.

        **Status:** {'🔴 Sangat Tinggi' if ratio >= 40 else '🟡 Tinggi' if ratio >= 25 else '🟢 Normal'}
        """
        )
        st.warning(
            """
        📌 **Rekomendasi**: Jika kategori ini termasuk kebutuhan sekunder seperti hiburan atau makanan di luar rumah, pertimbangkan untuk mengurangi frekuensi pembelian agar anggaran tetap terjaga.
        """
        )

    # ====================================
    # MERCHANT ANALYSIS
    # ====================================

    merchant_df = (
        df
        .groupby("merchant")["total_harga"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    merchant_df["persentase"] = (
        merchant_df["total_harga"]
        /
        merchant_df["total_harga"].sum()
        * 100
    ).round(1)

    colors = [
        "#0B3D91"
        if x == merchant_df["total_harga"].max()
        else "#9EC5FE"
        for x in merchant_df["total_harga"]
    ]

    fig_merchant = px.bar(
        merchant_df,
        x="merchant",
        y="total_harga",
        title="Top Spending Merchants"
    )

    fig_merchant.update_traces(
        marker_color=colors,
        customdata=merchant_df[["persentase"]],
        hovertemplate=
        "<b>%{x}</b><br>" +
        "Total Pengeluaran: Rp %{y:,.0f}<br>" +
        "Kontribusi: %{customdata[0]}%<extra></extra>"
    )

    st.divider()

    left, right = st.columns([2,1])

    with left:

        st.plotly_chart(
            fig_merchant,
            use_container_width=True
        )

    with right:

        merchant_name = (
            merchant_df.iloc[0]["merchant"]
        )

        merchant_spending = (
            merchant_df.iloc[0]["total_harga"]
        )

        st.write("### 🏪 Top Merchant")

        st.info(
            f"""

            Merchant dengan pengeluaran terbesar: **{merchant_name}**

            Total pengeluaran: **Rp {merchant_spending:,.0f}**
            """
        )

        st.warning(
            f"""
            📌 **Rekomendasi**: Merchant ini memberikan kontribusi terbesar terhadap total pengeluaran Anda.

            Periksa kembali apakah transaksi pada merchant ini merupakan kebutuhan utama atau pengeluaran yang masih dapat dioptimalkan.
            """
        )

    # ====================================
    # PAYMENT ANALYSIS
    # ====================================

    payment_df = (
        df["payment_method"]
        .value_counts()
        .reset_index()
    )

    payment_df.columns = [
        "payment_method",
        "count"
    ]

    payment_df["persentase"] = (
        payment_df["count"]
        /
        payment_df["count"].sum()
        * 100
    ).round(1)

    fig_payment = px.pie(
        payment_df,
        names="payment_method",
        values="count",
        title="Payment Method Distribution",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    fig_payment.update_traces(
        customdata=payment_df[["persentase"]],
        hovertemplate=
        "<b>%{label}</b><br>" +
        "Jumlah Transaksi: %{value}<br>" +
        "Persentase: %{customdata[0]}%<extra></extra>"
    )

    st.divider()

    left, right = st.columns([2,1])

    with left:

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )

    with right:

        top_payment = (
            payment_df.iloc[0]
            ["payment_method"]
        )

        st.write("### 💳 Top Payment")

        st.info(
            f"""
        Metode pembayaran yang paling sering digunakan: **{top_payment}**

        Persentase transaksi digital: **{digital_ratio*100:.1f}%**
        """
        )
        st.warning(
            f"""
        📌 **Rekomendasi**: Penggunaan pembayaran digital yang terlalu sering dapat membuat pengeluaran kecil terasa tidak terlihat. Pastikan tetap memantau transaksi harian secara rutin.
        """
        )

    # ====================================
    # AI SUMMARY
    # ====================================

    periode = (
    f"{start_date.strftime('%d %B %Y')} "
    f"sampai "
    f"{end_date.strftime('%d %B %Y')}"
)
    st.divider()

    st.subheader(
        "🧠 Financial Summary"
    )

    st.success(
        f"""
    Berdasarkan transaksi pada periode **{periode}**:

    • Kategori pengeluaran terbesar adalah **{top_category}**

    • Merchant yang paling sering digunakan adalah **{top_merchant}**

    • Penggunaan pembayaran digital mencapai **{digital_ratio*100:.1f}%**

    • Skor kesehatan finansial saat ini adalah **{score}/100**

    ### Kesimpulan

    Pola transaksi menunjukkan bahwa sebagian besar pengeluaran terkonsentrasi pada kategori tertentu. Dengan memantau kategori dominan dan mengendalikan pengeluaran berulang, kondisi keuangan dapat menjadi lebih sehat dan terencana.
    """
    )

# OCR CATEGORIZATION

elif menu == "Categorization":

    st.title("🧠 Transaction Categorization")

    st.markdown(
        "Simulate categorization using transaction text"
    )

    user_input = st.text_input(
        "Enter transaction text",
        placeholder="Example: gojek goride"
    )

    if st.button("Predict Category"):

        text = user_input.lower()

        # SIMPLE RULE-BASED DEMO

        knowledge_base = {}

        for _, row in df.iterrows():

            merchant = str(
                row["merchant"]
            ).lower().strip()

            item = str(
                row["item"]
            ).lower().strip()

            category = row["kategori"]

            knowledge_base[merchant] = category
            knowledge_base[item] = category

        text = user_input.lower().strip()

        prediction = "lainnya"
        matched_source = None

        for keyword, category in knowledge_base.items():

            if keyword in text:

                prediction = category
                matched_source = keyword

                break

        if prediction != "lainnya":

            st.success(
                f"""
        ✅ Predicted Category: {prediction}

        """
            )

        else:

            st.success(
                """
        ✅ Predicted Category: lainnya
        """
            )

# ============================================
# BEHAVIOR ANALYSIS
# ============================================

elif menu == "Behavior Analysis":

    st.title("👤 User Behavior Analysis")

    user_df = df[
        df["user_id"] == selected_user
    ]

    total_spending = user_df["total_harga"].sum()

    # ========================================
    # FINANCIAL HEALTH SCORE
    # ========================================

    st.divider()

    if score >= 80:

        behavior = "Healthy Spending Behaviour Detected"

    elif score >= 60:

        behavior = "Moderate Spending Behaviour Detected"

    else:

        behavior = "Risky Spending Behaviour Detected"

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "💰 Spending",
            f"Rp {total_spending:,.0f}"
        )

    with c2:
        st.metric(
            "🏥 Financial Health",
            f"{score}/100"
        )

    with c3:
        st.info(
            f""" **🤖 Behaviour**: 
            {behavior}"""
        )

    # ====================================
    # USER SPENDING BY CATEGORY
    # ====================================

    st.subheader("User Spending by Category")

    user_category = (
        user_df
        .groupby("kategori")["total_harga"]
        .sum()
        .reset_index()
        .sort_values(by="total_harga", ascending=False)
    )

    colors = [
        "#0B3D91" if x == user_category["total_harga"].max() else "#9EC5FE"
        for x in user_category["total_harga"]
    ]

    fig4 = px.bar(
        user_category,
        x="kategori",
        y="total_harga",
        text="total_harga",
        labels={
            "kategori": "Kategori",
            "total_harga": "Total Pengeluaran"
        }
    )

    fig4.update_traces(
        marker_color=colors,
        texttemplate="Rp %{y:,.0f}",
        textposition="outside",
        hovertemplate=(
            "Kategori: %{x}<br>"
            "Total Pengeluaran: Rp %{y:,.0f}<br>"
            "<extra></extra>"
        )
    )

    fig4.update_layout(
        yaxis_title="Total Pengeluaran (Rp)",
        xaxis_title="Kategori",
        showlegend=False
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    # ====================================
    # SPENDING BY DAY
    # ====================================

    user_df["day_name"] = user_df["date"].dt.day_name()

    weekday_df = (
        user_df.groupby("day_name")["total_harga"]
        .sum()
        .reset_index()
    )

    order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    weekday_df = weekday_df.set_index("day_name")
    weekday_df = weekday_df.reindex(order, fill_value=0)
    weekday_df = weekday_df.reset_index()

    weekday_df["day_name"] = pd.Categorical(
        weekday_df["day_name"],
        categories=order,
        ordered=True
    )

    weekday_df = weekday_df.sort_values("day_name")

    colors = [
        "#0B3D91" if x == weekday_df["total_harga"].max() else "#9EC5FE"
        for x in weekday_df["total_harga"]
    ]

    fig_weekday = px.bar(
        weekday_df,
        x="day_name",
        y="total_harga",
        title="Spending by Day",
        text="total_harga"
    )

    fig_weekday.update_traces(
        marker_color=colors,
        texttemplate="Rp %{y:,.0f}",
        textposition="outside",
        hovertemplate=(
            "Hari: %{x}<br>"
            "Total Spending: Rp %{y:,.0f}<br>"
            "<extra></extra>"
        )
    )

    fig_weekday.update_layout(
        xaxis_title="Day",
        yaxis_title="Total Spending (Rp)",
        showlegend=False
    )

    st.plotly_chart(
        fig_weekday,
        use_container_width=True
    )

    st.subheader("🧾 Recent Transactions")

    recent_transactions = (
        user_df[
            [
                "date",
                "merchant",
                "item",
                "kategori",
                "payment_method",
                "total_harga"
            ]
        ]
        .sort_values(
            by="date",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        recent_transactions,
        use_container_width=True
    )