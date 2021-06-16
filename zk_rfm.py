
# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.
import datetime as dt
import pandas as pd


pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
df_ = pd.read_excel(r"C:\Users\zuley\Desktop\hafta3_python/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")


#GÖREV1: Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz
df_ = pd.read_excel(r"C:\Users\zuley\Desktop\hafta3_python/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df.shape

#GÖREV2: Veri setinin betimsel istatistiklerini inceleyiniz
df.shape
df.dtypes
df.describe().T   # - değerler var bunlar iadeler bunları çıkarmalıyız

#GÖREV3:Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?

df.shape
df.isnull()    #True false döner
df.isnull().sum()   #description ve customer ıd de eksiklikler mevcut
#GÖREV4: Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)    # eksik gözlemler kalıcı olarak silindi
df.shape

#GÖREV5: Eşsiz ürün sayısı kaçtır?
df["StockCode"].nunique()
#GÖREV6: Hangi üründen kaçar tane vardır?

df("StockCode").value_counts()


#GÖREV7: En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.

df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head()

#GÖREV8: Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]
###################df[df["Quantity"]>0].head()
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)

#GÖREV9: Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz
df["TotalPrice"] = df["Quantity"] * df["Price"] # ürün adedi*birim fiyatı =toplam ücret




#Görev 2:
#RFM metriklerinin hesaplanması
#Recency, Frequency ve Monetary tanımlarını yapınız.

#Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız
# Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
# Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz

df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)

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




#Görev 3:
#RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi
#Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
#Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
#recency_score ve frequency_score’u tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
#RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi
#DİKKAT! monetary_score’u dahil etmiyoruz

# Recency skoru
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])  # hepsi için anlaşılır olsun diye skorluyoruz büyükten küçüğe doğru sırala 5 skoru küçük değere karşılık gelsin
# 0,20,40,60,80,100

rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]) #küçükten büyüğe sırala

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5]) #küçükten büyüğe sırala


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))   #anlaşılır olması için r+f yapıyoruz



#Görev 4:
#RFM skorlarının segment olarak tanımlanması
#Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapınız
#Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz


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


#Görev 5:
#Aksiyon zamanı!
#Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
#- Hem aksiyon kararları açısından,
#- Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.
# "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
# Segmentlere göre RFM ortalama ve sıklık değerlerini grupla
# Need Attention sınıfını göster

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
