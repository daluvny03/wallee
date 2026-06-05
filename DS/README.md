# 💸 Wallee: Smart Money, Happy Life

Wallee adalah aplikasi Personal Finance Assistant berbasis Streamlit yang membantu pengguna memahami pola pengeluaran, memantau kesehatan finansial, serta memperoleh insight dari data transaksi secara interaktif.

## 📌 Project Overview

Pengelolaan keuangan pribadi sering kali menjadi tantangan karena banyaknya transaksi yang terjadi setiap hari. Wallee dikembangkan untuk membantu pengguna:

* Memantau pengeluaran secara real-time
* Menganalisis perilaku keuangan
* Mengidentifikasi kategori pengeluaran dominan
* Memahami pola transaksi berdasarkan merchant dan metode pembayaran
* Mengotomatisasi kategorisasi transaksi

## 🚀 Features

### 📊 Dashboard Analytics

Menampilkan ringkasan kondisi keuangan pengguna dalam bentuk visualisasi interaktif, meliputi:

* Total transaksi
* Total pengeluaran
* Top category
* Top merchant
* Financial health score
* Monthly spending trend
* Category analysis
* Merchant analysis
* Payment method analysis
* Financial summary
* Spending by Day
* Weekend and Weekday Spending

### 🧠 Transaction Categorization

Fitur simulasi kategorisasi transaksi.

Contoh input:

gojek goride

Output:

transportasi

### 👤 Behavior Analysis

Menganalisis perilaku transaksi pengguna berdasarkan:

* Total spending
* Financial health score
* Spending by category
* Recent transactions
* Spending behavior status

## 📂 Dataset

Dataset yang digunakan merupakan dataset transaksi keuangan pribadi yang telah melalui proses:

* Data Cleaning
* Feature Engineering
* Data Transformation

Beberapa fitur yang digunakan:

* user_id
* date
* merchant
* item
* kategori
* payment_method
* total_harga
* is_digital_payment
* is_weekend
* month

## 🏥 Financial Health Score

Skor kesehatan finansial dihitung menggunakan rule-based scoring sederhana berdasarkan:

* Proporsi pengeluaran makanan dan minuman
* Intensitas penggunaan pembayaran digital
* Perbandingan pengeluaran akhir pekan dan hari kerja
* Total pengeluaran pengguna

Skor akhir berada pada rentang:

* 80–100 : Healthy
* 60–79 : Need Attention
* <60 : Overspending Risk

## 🛠️ Technologies Used

* Python
* Streamlit
* Pandas
* Plotly
* Pillow

## 📦 Installation

Clone repository:

```bash
git clone https://github.com/Wallee-CC26-PSU167/Wallee-DataScience.git
cd Wallee-DataScience-main
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
streamlit run app.py
```

## 📁 Project Structure

```text
Wallee/
│
├── app.py
├── feature_engineered_finance_dataset.csv
├── requirements.txt
├── README.md
└── assets/
```

## 👥 Team

Capstone Project – Personal Finance AI Assistant (Wallee)

Developed as part of Data Science Capstone Project.
