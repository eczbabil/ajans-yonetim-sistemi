from flask import Blueprint, jsonify
from src.models import Teslimat

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/teslimatlar/<int:musteri_id>')
def api_teslimatlar(musteri_id):
    """Müşteriye göre teslimatları getir"""
    teslimatlar = Teslimat.query.filter_by(musteri_id=musteri_id).all()
    result = []
    for teslimat in teslimatlar:
        result.append({
            'id': teslimat.id,
            'baslik': teslimat.baslik,
            'durum': teslimat.durum
        })
    return jsonify(result)
