from datetime import datetime

def format_date(date_obj, format='%d.%m.%Y'):
    """Tarihi formatla"""
    if not date_obj:
        return ''
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
    return date_obj.strftime(format)

def format_currency(amount):
    """Para birimini formatla"""
    if not amount:
        return '0,00 ₺'
    return f"{amount:,.2f} ₺".replace(',', 'X').replace('.', ',').replace('X', '.')
