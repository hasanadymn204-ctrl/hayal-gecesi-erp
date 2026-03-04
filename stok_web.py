import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from PIL import Image

# --- 1. GÜVENLİK AYARLARI ---
ADMIN_USER = "admin"
ADMIN_PASS = "1234" # Burayı dilediğin şifreyle değiştirebilirsin

def giris_kontrol():
    if "authed" not in st.session_state:
        st.session_state.authed = False

    if not st.session_state.authed:
        st.markdown("""
            <style>
            .login-box {
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.title("🌙 Hayal Gecesi Giriş")
            user = st.text_input("Kullanıcı Adı")
            pw = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
                if user == ADMIN_USER and pw == ADMIN_PASS:
                    st.session_state.authed = True
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- SİSTEMİ BAŞLAT ---
st.set_page_config(page_title="Hayal Gecesi ERP", layout="wide", page_icon="🌙")

if giris_kontrol():
    # --- 2. KLASÖR VE VERİ AYARLARI ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STOK_FILE = os.path.join(BASE_DIR, "stok_verisi.csv")
    SATIS_FILE = os.path.join(BASE_DIR, "satis_gecmisi.csv")
    MUSTERI_FILE = os.path.join(BASE_DIR, "musteri_verisi.csv")

    # Veri Yükleme Fonksiyonu
    def verileri_yukle(dosya, sutunlar):
        if not os.path.exists(dosya) or os.stat(dosya).st_size == 0:
            return pd.DataFrame(columns=sutunlar)
        try:
            df = pd.read_csv(dosya)
            for col in sutunlar:
                if col not in df.columns:
                    df[col] = 0 if any(x in col for x in ["Fiyat", "Tutar", "Adet"]) else "Yok"
            return df
        except: return pd.DataFrame(columns=sutunlar)

    stok_df = verileri_yukle(STOK_FILE, ["Stok Kodu", "Kategori", "Ürün", "Beden", "Adet", "Alış Fiyatı", "Satış Fiyatı"])
    gecmis_df = verileri_yukle(SATIS_FILE, ["Tarih", "Müşteri", "Ürünler", "Toplam Tutar", "Toplam Kâr"])
    musteri_df = verileri_yukle(MUSTERI_FILE, ["Müşteri Adı", "Telefon", "Adres", "Kayıt Tarihi"])

    if "sepet" not in st.session_state: st.session_state.sepet = []
    if "son_siparis" not in st.session_state: st.session_state.son_siparis = None

    # --- 3. SIDEBAR (LOGO VE ÇIKIŞ) ---
    with st.sidebar:
        # Logo Arama
        for ad in ["logo.jpeg", "IMG_7159 kopyası.jpeg", "logo.jpg"]:
            yol = os.path.join(BASE_DIR, ad)
            if os.path.exists(yol):
                st.image(Image.open(yol), use_container_width=True)
                break
        
        st.success(f"Giriş Yapıldı: {ADMIN_USER}")
        sayfa = st.radio("MENÜ", ["🏠 Ana Panel", "🛒 Sipariş Oluştur", "📦 Ürün & Stok", "👥 Müşteri Yönetimi"])
        
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.authed = False
            st.rerun()

    # --- SAYFALAR (Buradan sonrası mevcut çalışan kodun aynısı) ---
    if sayfa == "🏠 Ana Panel":
        st.title("📊 İşletme Özeti")
        c1, c2, c3, c4 = st.columns(4)
        ciro = pd.to_numeric(gecmis_df["Toplam Tutar"]).sum() if not gecmis_df.empty else 0
        kar = pd.to_numeric(gecmis_df["Toplam Kâr"]).sum() if not gecmis_df.empty else 0
        c1.metric("💰 Ciro", f"{ciro:,.2f} TL")
        c2.metric("📈 Kâr", f"{kar:,.2f} TL")
        c3.metric("👥 Müşteri", len(musteri_df))
        c4.metric("📦 Stok", int(stok_df["Adet"].sum()))
        st.dataframe(gecmis_df.tail(10), use_container_width=True)

    elif sayfa == "🛒 Sipariş Oluştur":
        # ... (Önceki fixli sipariş oluşturma ve yazdırma kodların buraya gelecek)
        st.write("Sipariş ekranı aktif.")
        # [Önceki kodundaki Sipariş Oluştur kısmını buraya yapıştır]

    # ... (Stok ve Müşteri yönetimi bloklarını buraya ekle)
