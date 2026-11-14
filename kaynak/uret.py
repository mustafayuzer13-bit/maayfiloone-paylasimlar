#!/usr/bin/env python3
"""Sonraki N Reels videosunu üretir ve kuyruk.json'a ekler.
Kullanım (depo kökünden):  python3 kaynak/uret.py 35
Yayınlanmamış en eski kayıt = sıradaki paylaşım.
"""
import json, os, random, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(ROOT, 'kaynak')
RAW = 'https://raw.githubusercontent.com/mustafayuzer13-bit/maayfiloone-paylasimlar/main/'
TEL = '0543 952 22 43'

HOOKS = [
    (["Hâlâ", "deftere mi", "yazıyorsunuz?"], 1),
    (["Hangi makineniz", "gerçekten", "kazandırıyor?"], 2),
    (["Alacaklarınızı", "unutuyor", "musunuz?"], 1),
    (["Ay sonu", "hesap", "kabusu mu?"], 2),
    (["Operatör", "kaç saat", "çalıştı?"], 1),
    (["Excel'de", "kaybolmaya", "son!"], 2),
    (["Filonuz", "cebinizde"], 1),
    (["Kâğıt, kalem,", "hesap makinesi…", "Bırakın!"], 2),
    (["Makine", "kiralıyorsanız", "bunu izleyin"], 0),
    (["Kim ne kadar", "borçlu?", "Tek tıkla görün"], 1),
    (["Yakıt", "masrafınız", "nereye gidiyor?"], 1),
    (["Şantiyede de", "ofiste de", "aynı veri"], 2),
    (["Kârınızı", "tahminle değil", "rakamla bilin"], 1),
    (["Günlük işler", "karışıyor mu?"], 0),
    (["Tahsilatı", "kaçırmayın"], 0),
    (["İş makinesi", "sahipleri", "dikkat!"], 2),
    (["Filo yönetimi", "bu kadar", "kolay olmalı"], 1),
    (["Defter", "kaybolur,", "veri kalır"], 2),
    (["Bir makinenin", "gerçek", "maliyeti ne?"], 2),
    (["Müşteri", "aradı, bakiye", "ne kadar?"], 1),
    (["Telehandler,", "ekskavatör,", "vinç…"], 0),
    (["5 saniyede", "filo raporu"], 0),
    (["Hesabı", "akşam değil", "anında görün"], 1),
    (["Kayıt tutmak", "angarya", "olmasın"], 1),
    (["İşinizi", "büyütmenin", "ilk adımı"], 1),
    (["Makineleriniz", "çalışıyor,", "peki kazanıyor mu?"], 2),
    (["Operatörden", "anlık", "bildirim"], 1),
    (["Verileriniz", "güvende mi?"], 1),
    (["Her yerden", "erişim"], 0),
    (["Maay Filo One", "ile tanışın"], 0),
]

T = {  # konu: (başlıklar, alt etiket, mobil, ekran, fotoğraflar, maddeler)
    'makine': (["Tüm makineleriniz tek ekranda", "Her makinenin kazancı ayrı ayrı", "Makine kayıtları düzenli"],
               "Makine & operatör takibi", 'mobil/makinelerim.png', 'ekran/makine-kayitlari.jpg',
               ['arka/04_erkek_santiye_kabin_makinelerim.jpg', 'arka/manitou.jpg', 'arka/haber_kapak.jpg'],
               "Makine bazında gelir, gider ve kâr takibi"),
    'gider': (["Her kuruş kayıt altında", "Yakıt, bakım, sigorta… hepsi burada", "Giderlerinizi kontrol edin"],
              "Gider yönetimi", 'mobil/giderler.png', 'ekran/giderler.jpg',
              ['arka/05_erkek_santiye_ofisi_giderler.jpg', 'arka/10_kadin_modern_ofis_giderler.jpg'],
              "Yakıt, bakım ve tüm gider kalemleri tek yerde"),
    'kar': (["Kâr / zarar anında önünüzde", "Rakamlar net, kararlar doğru", "Aylık kârlılık tek bakışta"],
            "Gelir – gider özeti", 'mobil/gelir-gider-ozeti.png', 'ekran/gelir-gider-ozeti.jpg',
            ['arka/03_erkek_modern_ofis_gelir_gider_ozeti.jpg', 'arka/08_kadin_modern_ofis_gelir_gider_ozeti.jpg'],
            "Gelir-gider ve kâr-zarar raporları"),
    'cari': (["Alacaklarınızı kaçırmayın", "Kim ne kadar borçlu, anında görün", "Tahsilat artık kontrolünüzde"],
             "Cari hesap & tahsilat", 'mobil/cari-hesap.png', 'ekran/cari-hesap.jpg',
             ['arka/02_erkek_modern_ofis_cari_hesap.jpg', 'arka/06_kadin_modern_ofis_cari_hesap.jpg'],
             "Cari hesap, alacak yaşlandırma ve tahsilat takibi"),
    'gunluk': (["Günlük işler tek listede", "Hangi iş, hangi makine, kaç saat", "Sahadaki her iş kayıtlı"],
               "Günlük iş takibi", None, 'ekran/gunluk-isler.jpg',
               ['arka/01_erkek_santiye_ofisi_gunluk_isler.jpg', 'arka/09_kadin_santiye_ofisi_gunluk_isler.jpg'],
               "Günlük iş, çalışma saati ve müşteri kaydı"),
    'operator': (["Operatörden anlık bildirim", "Sahadan ofise kesintisiz bilgi"],
                 "Operatör bildirimleri", 'mobil/operator-bildirimleri.png', None, ['arka/09_kadin_santiye_ofisi_gunluk_isler.jpg', 'arka/01_erkek_santiye_ofisi_gunluk_isler.jpg'],
                 "Operatör hesapları ve anlık bildirimler"),
    'guven': (["Verileriniz güvende", "Güvenli giriş, her cihazdan erişim"],
              "Masaüstü · Mobil · Online", 'mobil/guvenli-giris.png', None, ['arka/02_erkek_modern_ofis_cari_hesap.jpg', 'arka/06_kadin_modern_ofis_cari_hesap.jpg'],
              "Masaüstü, mobil ve online; güvenli erişim"),
}
ALLBG = sorted({p for v in T.values() for p in v[4]})
QUESTIONS = ["Sizin filonuzda en çok vakit alan iş hangisi? 👇", "Kaç makineyle çalışıyorsunuz? Yorumlara yazın 👇",
             "Kayıtlarınızı şu an nasıl tutuyorsunuz? 👇", "En çok hangi özelliği merak ettiniz? 👇",
             "Sizce filo yönetiminde en zor kısım ne? 👇", "Ekip arkadaşınızı etiketleyin 👇"]
TAGS = ["#MaayFiloOne #FiloYönetimi #İşMakinesi #MakineKiralama #Şantiye",
        "#MaayFiloOne #İnşaat #Manitou #Telehandler #İşMakineleri",
        "#MaayFiloOne #FiloTakip #MakineTakip #Kütahya #İnşaatSektörü",
        "#MaayFiloOne #Ekskavatör #Vinç #MakineKiralama #Yazılım"]

def build(idx, rng):
    hook, acc = HOOKS[idx % len(HOOKS)]
    topics = rng.sample(list(T), 3)
    scenes = [{"type": "hook", "bg": os.path.join(K, rng.choice(ALLBG)), "lines": hook, "accent": acc, "dur": 3.0}]
    for tp in topics:
        titles, sub, mob, scr, photos, _ = T[tp]
        kinds = [k for k, ok in (('phone', mob), ('screen', scr), ('photo', photos)) if ok]
        kind = rng.choice(kinds); title = rng.choice(titles)
        if kind == 'phone': sc = {"type": "phone", "img": os.path.join(K, mob)}
        elif kind == 'screen': sc = {"type": "screen", "img": os.path.join(K, scr), "focus": [rng.choice([0.2, 0.5, 0.8]), 0.4]}
        else: sc = {"type": "photo", "bg": os.path.join(K, rng.choice(photos))}
        sc.update({"title": title, "sub": sub, "dur": 3.0}); scenes.append(sc)
    scenes.append({"type": "cta", "dur": 3.5})
    cap = (" ".join(hook).replace("… ", "… ") + "\n\n"
           + "Maay Filo One ile filonuzu tek ekrandan yönetin.\n\n"
           + "\n".join("✅ " + T[tp][5] for tp in topics)
           + "\n💻 Masaüstü · 📱 Mobil · 🌐 Online\n\n"
           + f"🎁 7 gün ücretsiz deneyin!\n📞 {TEL}\n\n"
           + rng.choice(QUESTIONS) + "\n\n" + rng.choice(TAGS))
    return {"scenes": scenes, "music_seed": idx * 7 + 3}, cap

def main(n):
    qp = os.path.join(ROOT, 'kuyruk.json')
    q = json.load(open(qp)) if os.path.exists(qp) else []
    start = max([e['no'] for e in q], default=0)
    os.makedirs(os.path.join(ROOT, 'videos'), exist_ok=True)
    for k in range(n):
        no = start + k + 1; rng = random.Random(no * 1009)
        spec, cap = build(no - 1, rng)
        name = f"videos/reel-{no:03d}.mp4"; sp = f"/tmp/spec_{no}.json"
        json.dump(spec, open(sp, 'w'), ensure_ascii=False)
        subprocess.run([sys.executable, os.path.join(K, 'reel.py'), sp, os.path.join(ROOT, name)], check=True)
        q.append({"no": no, "video": name, "url": RAW + name, "caption": cap, "posted": False, "media_id": None, "posted_at": None})
        json.dump(q, open(qp, 'w'), ensure_ascii=False, indent=1)
        print('ok', no, flush=True)

if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 35)
