
# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.
import pandas as pd

# load the dataset for 2010-2011 years
df = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")


"""
description of the dataset

* InvoiceNo: Invoice number. Nominal. A 6-digit integral number uniquely assigned to each transaction. If this code starts with the letter 'c', 
it indicates a cancellation.
* StockCode: Product (item) code. Nominal. A 5-digit integral number uniquely assigned to each distinct product.
* Description: Product (item) name. Nominal.
* Quantity: The quantities of each product (item) per transaction. Numeric.
* InvoiceDate: Invice date and time. Numeric. The day and time when a transaction was generated.
* UnitPrice: Unit price. Numeric. Product price per unit in sterling (Â£).
* CustomerID: Customer number. Nominal. A 5-digit integral number uniquely assigned to each customer.
* Country: Country name. Nominal. The name of the country where a customer resides.
"""

# describe the data
print(df.shape)
print(df.head())
print(df.info())
print(df.describe())


# is there any empty value in the dataset
df.isnull().sum().any()
# and the amount of these if any?
df.isnull().sum()

# drop out empty values in the dataset permanently
df.dropna(inplace=True)
df.isnull().sum()

# tne number unique product
df["StockCode"].nunique()

# the number of each product
df["StockCode"].value_counts()


# The top 5 most selling products in descending order
top_five_selling = df.groupby("StockCode").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
top_five_selling.reset_index()

# drop invoices starting letter 'C' in the dataset which specifies the canceled transactions
df = df[~df["Invoice"].str.contains("C", na=False)]

# create a new variable named "TotalPrice" standing for the total earning from each invoice
df["TotalPrice"] = df["Quantity"] * df["Price"]


# define the Recency, Frequency and Monetary terms
# RFM stands for Recency, Frequency, and Monetary.
# Recency means the freshness of the customer activity, transaction.
# Frequency means the density of the customer activity.
# Monetary means the revenue coming from customer activity.


# calculate recency, frequency, and monetary metrics per customers
import datetime as dt

# lets define a reference date named 'today_date' as 2 days after the last transaction
today_date = df["InvoiceDate"].max().date() + dt.timedelta(2)
today_date = dt.datetime.combine(today_date, dt.datetime.min.time())

# create rfm dataframe by aggregating some operations on groups of Customer IDs
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
# rename the columns
rfm.columns = ['recency', 'frequency', 'monetary']

# select monetary over 0
rfm = rfm[rfm["monetary"] > 0]

# reset index
rfm.reset_index(inplace=True)

# convert Customer ID from float to integer
rfm["Customer ID"] = rfm["Customer ID"].astype(int)


# plot recency, frequency and monetary distributions
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 10))
plt.subplot(3, 1, 1);
sns.histplot(rfm["recency"], bins=50)
plt.subplot(3, 1, 2);
sns.histplot(rfm["frequency"], bins=50)
plt.subplot(3, 1, 3);
sns.histplot(rfm["monetary"], bins=50)
plt.show()

# calculate recency, frequency, and monetary scores and merge them into one variable

# calculate recency score
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm.head()

# calculate frequency score
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm.head()

# calculate monetary score
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm.head()

# create one variable merging all scores
rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str) +
                    rfm["monetary_score"].astype(str))

# numeric rfm score for visualization
rfm["RFM_SCORE_"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str) +
                    rfm["monetary_score"].astype(str)).astype(int)
rfm.head()

rfm["RFM_SCORE"].nunique()

# Visualise segments using 3D plot

x = rfm["recency_score"]
y = rfm["frequency_score"]
z = rfm["monetary_score"]
c = rfm["RFM_SCORE_"]
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

scat_plot = ax.scatter(xs=x, ys=y, zs=z, c=c, s=c-100, alpha=0.5)
ax.set_title("RFM Visualisation")
ax.set_xlabel("recency score")
ax.set_ylabel("frequency score")
ax.set_zlabel("monetary score")

cb = plt.colorbar(scat_plot, pad=0.2)
cb.set_ticks([1,2,3,4,5])
cb.set_ticklabels(["1", "2", "3", "4", "5"])

plt.show()

# recency  kaç gün önce geldiği küçük olması önemli
# frequency alışveriş sıklığı  büyük olmalı
# monetary  toplam bıraktığı ücret büyük olmalı
#Not 1: recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
#Not 2: rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T
rfm = rfm[rfm["monetary"] > 0]


# Recency skoru
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])  # hepsi için anlaşılır olsun diye skorluyoruz büyükten küçüğe doğru sırala 5 skoru küçük değere karşılık gelsin
# 0,20,40,60,80,100

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]) #küçükten büyüğe sırala

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5]) #küçükten büyüğe sırala


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))   #anlaşılır olması için r+f yapıyoruz




seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)


rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])
#need_attion recency ortalaması 52
#cant lose
#at_risk recency ortalaması 153
# yukarıdaki değerleri df'e dönüştür

rfm[rfm["segment"] == "new_customers"].index  # yeni müşterilerin müşteri numaralarını listele

loyal_df = pd.DataFrame()
loyal_df["loyal_customer_id"] = rfm[rfm["segment"] == "loyal_customers"].index
loyal_df.head()

loyal_df.to_excel("loyal_customers.xlsx")
