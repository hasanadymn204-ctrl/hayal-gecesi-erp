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
            if st.button("Giriş Yap"):
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
        if st.button("🚪 Çıkış"):
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
        st.title("🛒 Satış Ekranı")
        
        if st.session_state.son_siparis:
            sip = st.session_state.son_siparis
            st.success("✅ Satış Tamamlandı!")
            # Fiş Görünümü (Yazıcı Dostu)
            st.markdown(f"""
                <div style="font-family:monospace; padding:20px; border:1px dashed #333; width:300px; background:white; color:black;">
                    <h3 align="center">HAYAL GECESİ</h3>
                    <p>Müşteri: {sip['m']}<br>Tarih: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <hr>
                    {''.join([f"<p>{i['Ürün']} ({i['Beden']}) x{i['Adet']} <span style='float:right;'>{i['Toplam']:.2f}</span></p>" for i in sip['s']])}
                    <hr>
                    <h4 align="right">TOPLAM: {sip['t']:.2f} TL</h4>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🆕 Yeni Satış"):
                st.session_state.son_siparis = None
                st.rerun()
        else:
            m_list = ["Genel Müşteri"] + musteri_df["Müşteri Adı"].tolist()
            secilen_m = st.selectbox("Müşteri", m_list)
            
            if not stok_df.empty:
                stok_df["Display"] = stok_df["Stok Kodu"].astype(str) + " - " + stok_df["Ürün"] + " (" + stok_df["Beden"] + ")"
                c1, c2, c3 = st.columns([3,1,1])
                u_sec = c1.selectbox("Ürün", ["Seçiniz..."] + stok_df[stok_df["Adet"] > 0]["Display"].tolist())
                adt = c2.number_input("Adet", 1, 100, 1)
                if c3.button("➕ Ekle"):
                    if u_sec != "Seçiniz...":
                        idx = stok_df[stok_df["Display"] == u_sec].index[0]
                        u = stok_df.loc[idx]
                        st.session_state.sepet.append({"Ürün": u["Ürün"], "Beden": u["Beden"], "Adet": adt, "Fiyat": u["Satış Fiyatı"], "Alış": u["Alış Fiyatı"], "Toplam": u["Satış Fiyatı"] * adt, "idx": idx})
                        st.rerun()
            
            if st.session_state.sepet:
                st.table(pd.DataFrame(st.session_state.sepet)[["Ürün", "Beden", "Adet", "Fiyat", "Toplam"]])
                if st.button("✅ Satışı Tamamla", use_container_width=True):
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
            if st.button("💾 Stok Listesini Güncelle"): ed.to_csv(STOK_FILE, index=False); st.success("Kaydedildi!"); st.rerun()

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
