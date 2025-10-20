"""
Word Rapor Oluşturma Modülü
Müşteri bazlı detaylı raporlar oluşturur
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime, timedelta
from collections import Counter


def add_heading_custom(doc, text, level=1):
    """
    Özel başlık ekler
    """
    heading = doc.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in heading.runs:
        run.font.color.rgb = RGBColor(37, 99, 235)  # Mavi renk
    return heading


def generate_musteri_raporu(db, musteri, start_date=None, end_date=None):
    """
    Müşteri için detaylı Word raporu oluşturur
    
    Args:
        db: Database session
        musteri: Musteri objesi
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
    
    Returns:
        Document: Word dokümanı
    """
    try:
        from app import IsGunlugu, Teslimat, SosyalMedya, Revizyon
    except ImportError:
        # Alternatif import yolu
        from ...app import IsGunlugu, Teslimat, SosyalMedya, Revizyon
    
    # Tarih aralığı belirleme
    if not end_date:
        end_date = datetime.now().date()
    if not start_date:
        # Son 30 gün
        start_date = end_date - timedelta(days=30)
    
    # Word dokümanı oluştur
    doc = Document()
    
    # Başlık
    title = doc.add_heading(f'{musteri.ad} - Detaylı Ajans Raporu', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Tarih bilgisi
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_run = date_para.add_run(
        f'Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y")}\n'
        f'Dönem: {start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}'
    )
    date_run.font.size = Pt(10)
    date_run.font.color.rgb = RGBColor(100, 100, 100)
    
    doc.add_paragraph()  # Boşluk
    
    # ===== GENEL ÖZET =====
    add_heading_custom(doc, '📊 Genel Özet', level=1)
    
    # İş günlüğü verileri
    isler = db.session.query(IsGunlugu).filter(
        IsGunlugu.musteri_id == musteri.id,
        IsGunlugu.tarih >= start_date,
        IsGunlugu.tarih <= end_date
    ).all()
    
    toplam_dakika = sum([is_item.sure_dakika for is_item in isler])
    toplam_saat = round(toplam_dakika / 60, 1)
    is_sayisi = len(isler)
    
    # Benzersiz iş günü sayısı
    benzersiz_gunler = len(set([is_item.tarih for is_item in isler]))
    
    # Benzersiz sorumlu kişiler
    sorumlu_kisiler = set([is_item.sorumlu_kisi for is_item in isler if is_item.sorumlu_kisi])
    ekip_buyuklugu = len(sorumlu_kisiler)
    
    # Özet paragraf
    ozet = doc.add_paragraph()
    ozet_text = (
        f"Toplam ortalama {toplam_saat} saat hizmet verilmiş. "
        f"{musteri.ad} için {benzersiz_gunler} iş günü boyunca "
        f"{ekip_buyuklugu} kişilik ekibimiz toplam {toplam_saat} saat çalıştı."
    )
    ozet.add_run(ozet_text).bold = True
    
    doc.add_paragraph()
    
    # ===== GENEL GÖSTERGELER TABLOSU =====
    add_heading_custom(doc, '📈 Genel Göstergeler', level=2)
    
    # Teslimat verileri
    teslimatlar = db.session.query(Teslimat).filter(
        Teslimat.musteri_id == musteri.id,
        Teslimat.teslim_tarihi >= start_date,
        Teslimat.teslim_tarihi <= end_date
    ).all()
    
    # Teslimat türlerine göre say
    tasarim_sayisi = len([t for t in teslimatlar if 'tasarım' in (t.teslim_turu or '').lower() or 'tasarım' in (t.aktivite_turu or '').lower()])
    video_sayisi = len([t for t in teslimatlar if 'video' in (t.teslim_turu or '').lower() or 'video' in (t.aktivite_turu or '').lower()])
    
    # Revizyonlar
    revizyonlar = db.session.query(Revizyon).filter(
        Revizyon.musteri_id == musteri.id,
        Revizyon.tarih >= start_date,
        Revizyon.tarih <= end_date
    ).all()
    
    tasarim_revize = len([r for r in revizyonlar if any(t.id == r.teslimat_id and 'tasarım' in (t.teslim_turu or '').lower() for t in teslimatlar)])
    video_revize = len([r for r in revizyonlar if any(t.id == r.teslimat_id and 'video' in (t.teslim_turu or '').lower() for t in teslimatlar)])
    
    onaylanan = len([t for t in teslimatlar if t.durum == 'Onaylandı'])
    
    # Sosyal medya
    sosyal_medyalar = db.session.query(SosyalMedya).filter(
        SosyalMedya.musteri_id == musteri.id,
        SosyalMedya.tarih >= start_date,
        SosyalMedya.tarih <= end_date
    ).all()
    
    yayinlanan = len([s for s in sosyal_medyalar if s.durum == 'Yayınlandı'])
    
    # Tablo oluştur
    table = doc.add_table(rows=7, cols=2)
    table.style = 'Light Grid Accent 1'
    
    # Başlıklar
    table.rows[0].cells[0].text = 'Gösterge'
    table.rows[0].cells[1].text = 'Sonuç'
    
    # Veriler
    table.rows[1].cells[0].text = 'Toplam medya dosyası'
    table.rows[1].cells[1].text = f"{len(teslimatlar)} ({tasarim_sayisi} tasarım + {video_sayisi} video)"
    
    table.rows[2].cells[0].text = 'Toplam revize'
    table.rows[2].cells[1].text = f"{len(revizyonlar)} ({tasarim_revize} tasarım + {video_revize} video)"
    
    table.rows[3].cells[0].text = 'Onaylanan işler'
    table.rows[3].cells[1].text = str(onaylanan)
    
    table.rows[4].cells[0].text = 'Yayınlanan işler'
    table.rows[4].cells[1].text = str(yayinlanan)
    
    table.rows[5].cells[0].text = 'Red edilen'
    table.rows[5].cells[1].text = "0"
    
    table.rows[6].cells[0].text = 'Proje süresi'
    table.rows[6].cells[1].text = f"{(end_date - start_date).days} gün ({start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')})"
    
    doc.add_page_break()
    
    # ===== TESLİMAT DETAYLARI =====
    add_heading_custom(doc, '📦 Teslimat Listesi', level=2)
    
    if teslimatlar:
        for teslimat in teslimatlar:
            doc.add_paragraph(
                f"{teslimat.teslim_tarihi.strftime('%d.%m.%Y')} - "
                f"{teslimat.sorumlu_kisi or 'Belirsiz'} - "
                f"{teslimat.baslik} ({teslimat.durum})",
                style='List Bullet'
            )
    else:
        doc.add_paragraph("Bu dönemde teslimat bulunmuyor.")
    
    doc.add_paragraph()
    
    # ===== REVİZYON DETAYLARI =====
    add_heading_custom(doc, '🔄 Revizyon Detayları', level=2)
    
    if revizyonlar:
        for revizyon in revizyonlar:
            # Teslimat bilgisini bul
            teslimat = next((t for t in teslimatlar if t.id == revizyon.teslimat_id), None)
            teslimat_adi = teslimat.baslik if teslimat else f"Teslimat #{revizyon.teslimat_id}"
            
            doc.add_paragraph(
                f"{revizyon.tarih.strftime('%d.%m.%Y')} - {teslimat_adi} - "
                f"{revizyon.revize_talep_eden}: {revizyon.revize_konusu[:50]}...",
                style='List Bullet'
            )
    else:
        doc.add_paragraph("Bu dönemde revizyon bulunmuyor.")
    
    doc.add_paragraph()
    
    # ===== DURUM ÖZETİ TABLOSU =====
    add_heading_custom(doc, '📋 Durum Özeti', level=2)
    
    durum_table = doc.add_table(rows=5, cols=2)
    durum_table.style = 'Light Grid Accent 1'
    
    durum_table.rows[0].cells[0].text = 'Kategori'
    durum_table.rows[0].cells[1].text = 'Adet'
    
    durum_table.rows[1].cells[0].text = 'Toplam iş üretilen'
    durum_table.rows[1].cells[1].text = str(len(teslimatlar))
    
    durum_table.rows[2].cells[0].text = 'Revize alan'
    durum_table.rows[2].cells[1].text = str(len(revizyonlar))
    
    durum_table.rows[3].cells[0].text = 'Onaylanan'
    durum_table.rows[3].cells[1].text = str(onaylanan)
    
    durum_table.rows[4].cells[0].text = 'Yayınlanan'
    durum_table.rows[4].cells[1].text = str(yayinlanan)
    
    doc.add_paragraph()
    
    # ===== İŞ TİPİ DAĞILIMI =====
    add_heading_custom(doc, '🎨 İş Tipi Dağılımı', level=2)
    
    aktivite_turleri = [is_item.aktivite_turu for is_item in isler if is_item.aktivite_turu]
    aktivite_sayaci = Counter(aktivite_turleri)
    
    if aktivite_sayaci:
        for aktivite, sayi in aktivite_sayaci.most_common():
            doc.add_paragraph(f"{aktivite}: {sayi} iş", style='List Bullet')
    else:
        doc.add_paragraph("İş tipi verisi bulunmuyor.")
    
    doc.add_paragraph()
    
    # ===== SOSYAL MEDYA =====
    if sosyal_medyalar:
        add_heading_custom(doc, '📱 Sosyal Medya İçerikleri', level=2)
        
        for sosyal in sosyal_medyalar:
            doc.add_paragraph(
                f"{sosyal.tarih.strftime('%d.%m.%Y')} - {sosyal.platform} - "
                f"{sosyal.gonderi_turu} - {sosyal.icerik_basligi} ({sosyal.durum})",
                style='List Bullet'
            )
    
    # ===== SONUÇ =====
    doc.add_page_break()
    add_heading_custom(doc, '✅ Sonuç', level=2)
    
    sonuc = doc.add_paragraph()
    sonuc.add_run(f"Ajans, {(end_date - start_date).days} gün içinde {musteri.ad} için:\n").bold = True
    sonuc.add_run(f"• {len(teslimatlar)} teslimat üretmiş\n")
    sonuc.add_run(f"• Bunların {len(revizyonlar)}'i revize edilmiş\n")
    sonuc.add_run(f"• {onaylanan} tanesi onaylanmış\n")
    sonuc.add_run(f"• {yayinlanan} tanesi yayına gitmiştir\n")
    sonuc.add_run(f"• Toplam {toplam_saat} saat hizmet verilmiştir\n")
    
    return doc


def save_musteri_raporu(doc, musteri, output_path=None):
    """
    Raporu dosyaya kaydeder
    
    Args:
        doc: Document objesi
        musteri: Musteri objesi
        output_path: Çıktı dosya yolu (opsiyonel)
    
    Returns:
        str: Dosya yolu
    """
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{musteri.ad.replace(' ', '_')}_{timestamp}_rapor.docx"
        output_path = f"uploads/{filename}"
    
    doc.save(output_path)
    return output_path

