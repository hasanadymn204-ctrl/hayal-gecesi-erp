import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# 1. Konfigürasyon ve Klasör Ayarı
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="Hayal Gecesi ERP", layout="wide", page_icon="🌙")

# Dosya Yolları
STOK_FILE = os.path.join(BASE_DIR, "stok_verisi.csv")
SATIS_FILE = os.path.join(BASE_DIR, "satis_gecmisi.csv")
MUSTERI_FILE = os.path.join(BASE_DIR, "musteri_verisi.csv")

# 2. Veri Yükleme Fonksiyonu
def verileri_yukle(dosya, sutunlar):
    if not os.path.exists(dosya) or os.stat(dosya).st_size == 0:
        return pd.DataFrame(columns=sutunlar)
    try:
        df = pd.read_csv(dosya)
        for col in sutunlar:
            if col not in df.columns:
                df[col] = 0 if any(x in col for x in ["Fiyat", "Tutar", "Adet"]) else "Yok"
        return df
    except:
        return pd.DataFrame(columns=sutunlar)

# Verileri Çek
stok_df = verileri_yukle(STOK_FILE, ["Stok Kodu", "Kategori", "Ürün", "Beden", "Adet", "Alış Fiyatı", "Satış Fiyatı"])
gecmis_df = verileri_yukle(SATIS_FILE, ["Tarih", "Müşteri", "Ürünler", "Toplam Tutar", "Toplam Kâr"])
musteri_df = verileri_yukle(MUSTERI_FILE, ["Müşteri Adı", "Telefon", "Adres", "Kayıt Tarihi"])

if "sepet" not in st.session_state: st.session_state.sepet = []
if "son_siparis" not in st.session_state: st.session_state.son_siparis = None

# 3. Sidebar (Logo ve Menü)
with st.sidebar:
    olasi_adlar = ["logo.jpeg", "IMG_7159 kopyası.jpeg", "logo.jpg", "logo.png"]
    for ad in olasi_adlar:
        yol = os.path.join(BASE_DIR, ad)
        if os.path.exists(yol):
            st.image(Image.open(yol), use_container_width=True)
            break
    sayfa = st.radio("MENÜ", ["🏠 Ana Panel", "🛒 Sipariş Oluştur", "📦 Ürün & Stok", "👥 Müşteri Yönetimi"])

# --- SAYFA 2: SİPARİŞ OLUŞTUR (Yazıcı Dostu Fix) ---
if sayfa == "🛒 Sipariş Oluştur":
    st.title("🛒 Satış ve Fiş Ekranı")
    
    if st.session_state.son_siparis:
        sip = st.session_state.son_siparis
        st.success("✅ Satış Kaydedildi!")
        
        # SADECE FİŞİ YAZDIRAN ÖZEL CSS
        st.markdown("""
            <style>
            @media print {
                /* Sidebar, Butonlar ve Gereksiz Streamlit Alanlarını Gizle */
                [data-testid="stSidebar"], .stButton, .stSuccess, .stInfo, header, footer, [data-testid="stHeader"] {
                    display: none !important;
                }
                .main .block-container {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                .print-receipt {
                    display: block !important;
                    width: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border: none !important;
                }
            }
            .print-receipt {
                font-family: 'Courier New', Courier, monospace;
                max-width: 400px;
                margin: 20px auto;
                padding: 20px;
                border: 1px dashed #333;
                background-color: white;
                color: black;
            }
            </style>
        """, unsafe_allow_html=True)

        # Yazdırılabilir Alan (HTML)
        st.markdown(f"""
            <div class="print-receipt">
                <div style="text-align: center;">
                    <h2 style="margin:0;">🌙 HAYAL GECESİ</h2>
                    <p style="font-size: 12px; margin:5px;">Sipariş Bilgi Fişi</p>
                    <hr style="border-top: 1px dashed black;">
                </div>
                <p><b>Tarih:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                <p><b>Müşteri:</b> {sip['m']}</p>
                <table width="100%" style="font-size: 14px; border-top: 1px solid black; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid black;">
                            <th align="left">Ürün</th>
                            <th align="center">Ad.</th>
                            <th align="right">Fiyat</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f"<tr><td style='padding:5px 0;'>{i['Ürün']} ({i['Beden']})</td><td align='center'>{i['Adet']}</td><td align='right'>{i['Fiyat']:.2f} TL</td></tr>" for i in sip['s']])}
                    </tbody>
                </table>
                <hr style="border-top: 1px dashed black;">
                <h3 align="right" style="margin-top:10px;">TOPLAM: {sip['t']:.2f} TL</h3>
                <div style="text-align: center; font-size: 11px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">
                    <p>Bizi Tercih Ettiğiniz İçin Teşekkür Ederiz!</p>
                    <p><b>İyi Günlerde Kullanın</b></p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Nasıl Yazdırılır?** Klavyenizden **Ctrl + P** tuşlarına basın. Gelen ekranda sadece yukarıdaki fiş görünecektir.")
        if st.button("🆕 Yeni Satışa Başla"):
            st.session_state.son_siparis = None
            st.rerun()
            
    else:
        # Satış Giriş Ekranı
        m_list = ["Genel Müşteri"] + musteri_df["Müşteri Adı"].tolist()
        m_secimi = st.selectbox("Müşteri Seçin", m_list)
        
        if not stok_df.empty:
            stok_df["Display"] = stok_df["Stok Kodu"].astype(str) + " - " + stok_df["Ürün"] + " (" + stok_df["Beden"] + ")"
            c1, c2, c3 = st.columns([3,1,1])
            u_sec = c1.selectbox("Ürün Seç", ["Seçiniz..."] + stok_df[stok_df["Adet"] > 0]["Display"].tolist())
            adt = c2.number_input("Adet", min_value=1, value=1)
            if c3.button("➕ Sepete Ekle"):
                if u_sec != "Seçiniz...":
                    idx = stok_df[stok_df["Display"] == u_sec].index[0]
                    u = stok_df.loc[idx]
                    st.session_state.sepet.append({"Ürün": u["Ürün"], "Beden": u["Beden"], "Adet": adt, "Fiyat": u["Satış Fiyatı"], "Alış": u["Alış Fiyatı"], "Toplam": u["Satış Fiyatı"] * adt, "idx": idx})
                    st.rerun()

        if st.session_state.sepet:
            st.table(pd.DataFrame(st.session_state.sepet)[["Ürün", "Beden", "Adet", "Fiyat", "Toplam"]])
            if st.button("✅ Satışı Tamamla ve Fiş Oluştur", use_container_width=True):
                t_t = sum(i["Toplam"] for i in st.session_state.sepet)
                t_k = sum((i["Fiyat"] - i["Alış"]) * i["Adet"] for i in st.session_state.sepet)
                
                for i in st.session_state.sepet: stok_df.at[i["idx"], "Adet"] -= i["Adet"]
                stok_df.drop(columns=["Display"], errors='ignore').to_csv(STOK_FILE, index=False)
                
                y_s = pd.DataFrame([{"Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"), "Müşteri": m_secimi, "Ürünler": "Sepet Detayı", "Toplam Tutar": t_t, "Toplam Kâr": t_k}])
                pd.concat([gecmis_df, y_s], ignore_index=True).to_csv(SATIS_FILE, index=False)
                
                st.session_state.son_siparis = {"m": m_secimi, "s": list(st.session_state.sepet), "t": t_t}
                st.session_state.sepet = []
                st.rerun()

# --- DİĞER SAYFALAR (FIXED) ---
elif sayfa == "🏠 Ana Panel":
    st.title("📊 İşletme Özeti")
    c1, c2, c3, c4 = st.columns(4)
    ciro = pd.to_numeric(gecmis_df["Toplam Tutar"]).sum() if not gecmis_df.empty else 0
    kar = pd.to_numeric(gecmis_df["Toplam Kâr"]).sum() if not gecmis_df.empty else 0
    c1.metric("💰 Ciro", f"{ciro:,.2f} TL")
    c2.metric("📈 Kâr", f"{kar:,.2f} TL")
    c3.metric("👥 Müşteri", len(musteri_df))
    c4.metric("📦 Toplam Stok", int(stok_df["Adet"].sum()))
    st.dataframe(gecmis_df.tail(10), use_container_width=True)

elif sayfa == "📦 Ürün & Stok":
    st.title("📦 Stok Yönetimi")
    t1, t2 = st.tabs(["📋 Liste", "➕ Yeni Ürün"])
    with t2:
        with st.form("u_form"):
            c1, c2, c3 = st.columns(3); kod = c1.text_input("Kod"); ad = c2.text_input("Ürün"); bdn = c3.selectbox("Beden", ["Std","S","M","L","XL","2XL"])
            c4, c5, c6 = st.columns(3); adt = c4.number_input("Adet", 0); ali = c5.number_input("Alış", 0.0); sat = c6.number_input("Satış", 0.0)
            if st.form_submit_button("Sisteme Ekle"):
                y_u = pd.DataFrame([{"Stok Kodu": kod, "Ürün": ad, "Beden": bdn, "Adet": adt, "Alış Fiyatı": ali, "Satış Fiyatı": sat}])
                pd.concat([stok_df, y_u], ignore_index=True).to_csv(STOK_FILE, index=False)
                st.rerun()
    with t1:
        ed = st.data_editor(stok_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Stok Güncelle"): ed.to_csv(STOK_FILE, index=False); st.rerun()

elif sayfa == "👥 Müşteri Yönetimi":
    st.title("👥 Müşteri İlişkileri")
    t1, t2 = st.tabs(["🔍 Bakiye Sorgula", "➕ Yeni Müşteri"])
    with t2:
        with st.form("m_form"):
            ad = st.text_input("Ad Soyad"); tel = st.text_input("Telefon")
            if st.form_submit_button("Müşteri Kaydet"):
                y_m = pd.DataFrame([{"Müşteri Adı": ad, "Telefon": tel, "Kayıt Tarihi": datetime.now().strftime("%d/%m/%Y")}])
                pd.concat([musteri_df, y_m], ignore_index=True).to_csv(MUSTERI_FILE, index=False)
                st.rerun()
    with t1:
        if not musteri_df.empty:
            m = st.selectbox("Müşteri Listesi", musteri_df["Müşteri Adı"].tolist())
            m_s = gecmis_df[gecmis_df["Müşteri"] == m]
            st.metric("Toplam Alışveriş", f"{m_s['Toplam Tutar'].sum():,.2f} TL")
            st.dataframe(m_s, use_container_width=True)
