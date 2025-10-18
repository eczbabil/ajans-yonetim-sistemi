from flask import Blueprint, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename
from src.models import Musteri
from src.utils.database import db

excel_bp = Blueprint('excel', __name__)

@excel_bp.route('/excel_import', methods=['GET', 'POST'])
def excel_import():
    """Excel import"""
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            
            try:
                # Excel'den veri oku ve veritabanına aktar
                df = pd.read_excel(filepath)
                
                # Müşterileri içe aktar
                if 'Müşteri Adı' in df.columns:
                    for _, row in df.iterrows():
                        musteri = Musteri(
                            ad=row['Müşteri Adı'],
                            sektor=row.get('Sektör', ''),
                            aylik_ucret=row.get('Aylık Ücret (TL)', 0),
                            ilgil_kisi=row.get('İlgili Kişi', ''),
                            telefon=row.get('Telefon', ''),
                            email=row.get('E-posta', ''),
                            notlar=row.get('Notlar', '')
                        )
                        db.session.add(musteri)
                
                db.session.commit()
                flash('Excel verisi başarıyla içe aktarıldı!', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Hata: {str(e)}', 'error')
    
    return render_template('excel_import.html')

@excel_bp.route('/excel_export')
def excel_export():
    """Excel export"""
    try:
        # Tüm verileri Excel'e export et
        with pd.ExcelWriter('ajans_raporu.xlsx', engine='openpyxl') as writer:
            # Müşteriler
            musteriler = pd.read_sql('SELECT * FROM musteri', db.engine)
            musteriler.to_excel(writer, sheet_name='Müşteriler', index=False)
            
            # İş günlüğü
            isler = pd.read_sql('SELECT * FROM is_gunlugu', db.engine)
            isler.to_excel(writer, sheet_name='İş Günlüğü', index=False)
            
            # Teslimatlar
            teslimatlar = pd.read_sql('SELECT * FROM teslimat', db.engine)
            teslimatlar.to_excel(writer, sheet_name='Teslimatlar', index=False)
            
            # Sosyal medya
            sosyal = pd.read_sql('SELECT * FROM sosyal_medya', db.engine)
            sosyal.to_excel(writer, sheet_name='Sosyal Medya', index=False)
        
        flash('Veriler Excel dosyasına export edildi!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))
