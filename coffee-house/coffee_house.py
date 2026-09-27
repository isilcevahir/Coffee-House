# Coffee House

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

def musteri_bul(ad):
    cur.execute(
        "SELECT id, ad, puan, toplam_kahve FROM musteriler WHERE ad = %s;",
        (ad,)
    )
    return cur.fetchone()

def menuyu_goster():
    cur.execute("SELECT ad, fiyat, puan FROM menu;")
    tum_kahveler = cur.fetchall()
    for m in tum_kahveler:
        print(f"{m[0].capitalize()} -Fiyat: {m[1]} TL - Puan: {m[2]} ")


print("=== COFFEE HOUSE ===")

while True:
    kullanici = input("Müşteri adını girin: ").strip().lower()

    if kullanici == "":
        print("Müşteri adı boş olamaz!")
        continue

    musteri = musteri_bul(kullanici)

    if musteri:
        islem = input("Ne yapmak istersiniz? (siparis/sil): ").strip().lower()

        if islem == "sil":
            onay = input(f"{musteri[1].capitalize()} adlı müşteriyi ve tüm sipariş geçmişini silmek istediğinize emin misiniz? (evet/hayır): ").strip().lower()

            if onay == "evet":
                cur.execute("DELETE FROM siparisler WHERE musteri_id = %s;", (musteri[0],))
                cur.execute("DELETE FROM musteriler WHERE id = %s;", (musteri[0],))
                conn.commit()
                print(f"{musteri[1].capitalize()} ve tüm sipariş geçmişi silindi.")
            else:
                print("Silme işlemi iptal edildi.")

        else:
            if musteri[2] >= 60:
                seviye = "Gold"
            elif musteri[2] >= 30:
                seviye = "Silver"
            else:
                seviye = "Bronze"

            print(f"Hoşgeldiniz {musteri[1].capitalize()}! puanın: {musteri[2]} | Seviyen: {seviye}")

            menuyu_goster()

            secim = input("Hangi kahveyi istersiniz (latte/espresso/americano/Mocha): ").strip().lower()
            cur.execute("SELECT puan FROM menu WHERE ad = %s;", (secim,))
            kahve = cur.fetchone()
            if kahve:
                puan = kahve[0]
                cur.execute(
                    "UPDATE musteriler SET puan = puan + %s, toplam_kahve = toplam_kahve + %s WHERE id = %s;",
                    (puan, 1, musteri[0])
                    )
                cur.execute(
                  "INSERT INTO siparisler (musteri_id, kahve_adi, puan) VALUES (%s, %s, %s);",
                  (musteri[0], secim, puan)
                  )
                conn.commit()
                print(f"Kahveniz hazır! toplam_kahve: {musteri[3] + 1}, Kazanılan puan: {puan}, yeni puan: {musteri[2] + puan}")

            else:
                print("Geçersiz kahve seçimi!")

    else:
        print("Müşteri Bulunamadı!")
        cevap = input("Yeni müşteri eklemek ister misiniz? (Evet/Hayır): ").strip().lower()
        if cevap == "evet":
            yeni_isim = input("Eklemek istediğiniz ismi girin: ").strip().lower()

            if yeni_isim == "":
                print("İsim boş olamaz!")
                continue

            cur.execute(
                "INSERT INTO musteriler (ad) VALUES (%s);",
                (yeni_isim,)
            )
            conn.commit()
            print(f"{yeni_isim.capitalize()} başarıyla eklendi!")
        else:
            print("İşlem iptal edildi.")

    devam = input("\nBaşka bir müşteriye hizmet vermek ister misiniz? (evet/hayır): ").strip().lower()
    if devam == "hayır":
        break

cur.close()

conn.close()
print("Program sonlandırıldı.")