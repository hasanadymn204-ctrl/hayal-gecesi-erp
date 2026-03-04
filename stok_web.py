import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- 1. GÜVENLİK VE AYARLAR ---
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

st.set_page_config(page_title="Hayal Gecesi ERP", layout="wide", page_icon="🌙")

def giris_kontrol():
    if "authed" not in st.session_state: st.session_state.authed = False
    if not st.session_state.authed:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.title("🌙 Hayal Gecesi Giriş")
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
                if user == ADMIN_USER and pw == ADMIN_PASS:
                    st.session_state.authed = True
                    st.rerun()
                else: st.error("Hatalı Giriş!")
        return False
    return True

if giris_kontrol():
    # --- 2. VERİ YÖNETİMİ ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STOK_FILE = os.path.join(BASE_DIR, "stok_verisi.csv")
    SATIS_FILE = os.path.join(BASE_DIR, "satis_gecmisi.csv")
    MUSTERI_FILE = os.path.join(BASE_DIR, "musteri_verisi.csv")

    def verileri_yukle(dosya, sutunlar):
        if not os.path.exists(dosya) or os.stat(dosya).st_size == 0:
            return pd.DataFrame(columns=sutunlar)
        try:
            df = pd.read_csv(dosya)
            for col in sutunlar:
                if col not in df.columns: df[col] = 0
            return df
        except: return pd.DataFrame(columns=sutunlar)

    stok_df = verileri_yukle(STOK_FILE, ["Stok Kodu", "Kategori", "Ürün", "Beden", "Adet", "Alış Fiyatı", "Satış Fiyatı"])
    gecmis_df = verileri_yukle(SATIS_FILE, ["Tarih", "Müşteri", "Ürünler", "Toplam Tutar", "Toplam Kâr"])
    musteri_df = verileri_yukle(MUSTERI_FILE, ["Müşteri Adı", "Telefon", "Adres", "Kayıt Tarihi"])

    if "sepet" not in st.session_state: st.session_state.sepet = []
    if "son_siparis" not in st.session_state: st.session_state.son_siparis = None

    # --- 3. SIDEBAR ---
    with st.sidebar:
        for ad in ["logo.jpeg", "logo.jpg", "logo.png"]:
            yol = os.path.join(BASE_DIR, ad)
            if os.path.exists(yol):
                st.image(Image.open(yol), use_container_width=True)
                break
        sayfa = st.radio("MENÜ", ["🏠 Ana Panel", "🛒 Sipariş Oluştur", "📦 Ürün & Stok", "👥 Müşteri Yönetimi"])
        st.markdown("---")
        if st.button("🚪 Güvenli Çıkış", use_container_width=True):
            st.session_state.authed = False
            st.rerun()

    # --- SAYFA 1: ANA PANEL ---
    if sayfa == "🏠 Ana Panel":
        st.title("📊 İşletme Özeti")
        c1, c2, c3, c4 = st.columns(4)
        ciro = pd.to_numeric(gecmis_df["Toplam Tutar"]).sum() if not gecmis_df.empty else 0
        kar = pd.to_numeric(gecmis_df["Toplam Kâr"]).sum() if not gecmis_df.empty else 0
        c1.metric("💰 Ciro", f"{ciro:,.2f} TL")
        c2.metric("📈 Kâr", f"{kar:,.2f} TL")
        c3.metric("👥 Müşteri", len(musteri_df))
        c4.metric("📦 Stok", int(stok_df["Adet"].sum()))
        st.markdown("---")
        st.subheader("📋 Son Satışlar")
        st.dataframe(gecmis_df.tail(10), use_container_width=True)

    # --- SAYFA 2: SİPARİŞ OLUŞTUR ---
    elif sayfa == "🛒 Sipariş Oluştur":
        st.title("🛒 Satış ve Fiş Ekranı")
        
        # SADECE FİŞİ YAZDIRAN ÖZEL CSS (Butonları gizler)
        st.markdown("""
            <style>
            @media print {
                [data-testid="stSidebar"], .stButton, .stSuccess, .stInfo, .stAlert, header, footer, [data-testid="stHeader"] {
                    display: none !important;
                }
                .main .block-container { padding: 0 !important; margin: 0 !important; }
                .print-receipt { display: block !important; width: 100% !important; border: none !important; }
            }
            .print-receipt {
                font-family: 'Courier New', Courier, monospace;
                max-width: 380px;
                margin: 10px auto;
                padding: 15px;
                border: 1px dashed #333;
                background-color: white;
                color: black;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.son_siparis:
            sip = st.session_state.son_siparis
            st.success("✅ Satış Başarıyla Kaydedildi!")
            
            # TEMİZ FİŞ TASARIMI
            fiş_html = f"""
                <div class="print-receipt">
                    <div style="text-align: center;">
                        <h2 style="margin:0;">🌙 HAYAL GECESİ</h2>
                        <p style="font-size: 12px; margin:5px;">Sipariş Bilgi Fişi</p>
                        <hr style="border-top: 1px dashed black;">
                    </div>
                    <p><b>Tarih:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><b>Müşteri:</b> {sip['m']}</p>
                    <table width="100%" style="font-size: 14px; border-collapse: collapse;">
                        <thead>
                            <tr style="border-bottom: 1px solid black;">
                                <th align="left">Ürün</th>
                                <th align="center">Ad.</th>
                                <th align="right">Tutar</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f"<tr><td style='padding:5px 0;'>{i['Ürün']} ({i['Beden']})</td><td align='center'>{i['Adet']}</td><td align='right'>{i['Toplam']:.2f}</td></tr>" for i in sip['s']])}
                        </tbody>
                    </table>
                    <hr style="border-top: 1px dashed black;">
                    <h3 align="right" style="margin-top:10px;">TOPLAM: {sip['t']:.2f} TL</h3>
                    <div style="text-align: center; font-size: 11px; margin-top: 25px;">
                        <p>Bizi Tercih Ettiğiniz İçin Teşekkür Ederiz!</p>
                        <p>www.hayalgecesi.com</p>
                    </div>
                </div>
            """
            st.markdown(fiş_html, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🖨️ Fişi Yazdır", use_container_width=True):
                    # window.parent.print() komutu bembeyaz sayfa sorununu çözer
                    st.components.v1.html(
                        "<script>window.parent.print();</script>", 
                        height=0, width=0
                    )
            with c2:
                if st.button("🆕 Yeni Satış", use_container_width=True):
                    st.session_state.son_siparis = None
                    st.rerun()
        else:
            m_list = ["Genel Müşteri"] + musteri_df["Müşteri Adı"].tolist()
            secilen_m = st.selectbox("Müşteri Seçin", m_list)
            
            if not stok_df.empty:
                stok_df["Display"] = stok_df["Stok Kodu"].astype(str) + " - " + stok_df["Ürün"] + " (" + stok_df["Beden"] + ")"
                c1, c2, c3 = st.columns([3,1,1])
                u_sec = c1.selectbox("Ürün Seç", ["Seçiniz..."] + stok_df[stok_df["Adet"] > 0]["Display"].tolist())
                adt = c2.number_input("Adet", 1, 100, 1)
                if c3.button("➕ Sepete Ekle"):
                    if u_sec != "Seçiniz...":
                        idx = stok_df[stok_df["Display"] == u_sec].index[0]
                        u = stok_df.loc[idx]
                        st.session_state.sepet.append({"Ürün": u["Ürün"], "Beden": u["Beden"], "Adet": adt, "Fiyat": u["Satış Fiyatı"], "Alış": u["Alış Fiyatı"], "Toplam": u["Satış Fiyatı"] * adt, "idx": idx})
                        st.rerun()
            
            if st.session_state.sepet:
                st.table(pd.DataFrame(st.session_state.sepet)[["Ürün", "Beden", "Adet", "Fiyat", "Toplam"]])
                if st.button("✅ Satışı Tamamla ve Fiş Oluştur", use_container_width=True):
                    top_t = sum(i["Toplam"] for i in st.session_state.sepet)
                    top_k = sum((i["Fiyat"] - i["Alış"]) * i["Adet"] for i in st.session_state.sepet)
                    
                    for i in st.session_state.sepet: stok_df.at[i["idx"], "Adet"] -= i["Adet"]
                    stok_df.drop(columns=["Display"], errors='ignore').to_csv(STOK_FILE, index=False)
                    
                    y_s = pd.DataFrame([{"Tarih": datetime.now().strftime("%d/%m/%Y %H:%M"), "Müşteri": secilen_m, "Ürünler": "Sepet Detayı", "Toplam Tutar": top_t, "Toplam Kâr": top_k}])
                    pd.concat([gecmis_df, y_s], ignore_index=True).to_csv(SATIS_FILE, index=False)
                    
                    st.session_state.son_siparis = {"m": secilen_m, "s": list(st.session_state.sepet), "t": top_t}
                    st.session_state.sepet = []
                    st.rerun()

    # --- SAYFA 3: ÜRÜN & STOK ---
    elif sayfa == "📦 Ürün & Stok":
        st.title("📦 Ürün ve Stok Yönetimi")
        t1, t2 = st.tabs(["📋 Liste", "➕ Yeni Ürün Ekle"])
        with t2:
            with st.form("yeni_urun"):
                c1, c2, c3 = st.columns(3); skod = c1.text_input("Kod"); sad = c2.text_input("Ürün"); sbdn = c3.selectbox("Beden", ["Std","S","M","L","XL"])
                c4, c5, c6 = st.columns(3); sadt = c4.number_input("Adet", 0); sali = c5.number_input("Alış", 0.0); ssat = c6.number_input("Satış", 0.0)
                if st.form_submit_button("Ürünü Kaydet"):
                    y_u = pd.DataFrame([{"Stok Kodu": skod, "Kategori": "Genel", "Ürün": sad, "Beden": sbdn, "Adet": sadt, "Alış Fiyatı": sali, "Satış Fiyatı": ssat}])
                    pd.concat([stok_df, y_u], ignore_index=True).to_csv(STOK_FILE, index=False)
                    st.success("Ürün eklendi!"); st.rerun()
        with t1:
            ed = st.data_editor(stok_df, use_container_width=True, num_rows="dynamic")
            if st.button("💾 Stok Listesini Güncelle"): 
                ed.to_csv(STOK_FILE, index=False)
                st.success("Kaydedildi!"); st.rerun()

    # --- SAYFA 4: MÜŞTERİ YÖNETİMİ ---
    elif sayfa == "👥 Müşteri Yönetimi":
        st.title("👥 Müşteri Yönetimi")
        t1, t2 = st.tabs(["🔍 Müşteri Sorgula", "➕ Yeni Müşteri"])
        with t2:
            with st.form("yeni_musteri"):
                mad = st.text_input("Ad Soyad"); mtel = st.text_input("Telefon"); madr = st.text_area("Adres")
                if st.form_submit_button("Müşteriyi Kaydet"):
                    y_m = pd.DataFrame([{"Müşteri Adı": mad, "Telefon": mtel, "Adres": madr, "Kayıt Tarihi": datetime.now().strftime("%d/%m/%Y")}])
                    pd.concat([musteri_df, y_m], ignore_index=True).to_csv(MUSTERI_FILE, index=False)
                    st.success("Müşteri eklendi!"); st.rerun()
        with t1:
            if not musteri_df.empty:
                m_sec = st.selectbox("Müşteri Seçin", musteri_df["Müşteri Adı"].tolist())
                m_detay = musteri_df[musteri_df["Müşteri Adı"] == m_sec].iloc[0]
                m_siparisler = gecmis_df[gecmis_df["Müşteri"] == m_sec]
                col1, col2 = st.columns(2)
                col1.info(f"📞 Tel: {m_detay['Telefon']}\n\n📍 Adres: {m_detay['Adres']}")
                col2.metric("💰 Toplam Alışveriş", f"{m_siparisler['Toplam Tutar'].sum():,.2f} TL")
                st.subheader("📜 Geçmiş Siparişler")
                st.dataframe(m_siparisler[["Tarih", "Toplam Tutar"]], use_container_width=True)
            else: st.info("Henüz müşteri kaydı yok.")
