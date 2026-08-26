from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os

app = Flask(__name__)
# Náhodný klíč pro session (uchování posledního skladu)
app.secret_key = os.urandom(24)

db_path = os.path.join(os.path.dirname(__file__), 'data', 'sklad.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50))
    name = db.Column(db.String(200), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=1)
    package_size = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=False)
    expiration = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    loc_filter = request.args.get('location')
    query = Item.query
    if loc_filter:
        query = query.filter_by(location=loc_filter)
    items = query.order_by(Item.expiration.asc()).all()
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    
    def format_size(size):
        if size is None: return ""
        return int(size) if size.is_integer() else size
        
    # NOVÉ: Funkce pro určení barvy řádku
    def get_expiration_status(exp_date):
        if not exp_date:
            return ""
            
        today = datetime.now().date()
        # Vypočítáme rozdíl v měsících (roky převedeme na měsíce)
        months_diff = (exp_date.year - today.year) * 12 + (exp_date.month - today.month)
        
        if months_diff < 0:
            return "table-danger" # Červená - prošlé
        elif months_diff <= 1:
            return "table-warning" # Žlutá - expiruje tento nebo příští měsíc
            
        return "" # Bez barvy
        
    return render_template('index.html', items=items, locations=locations, selected_loc=loc_filter, format_size=format_size, get_expiration_status=get_expiration_status)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        barcode = request.form.get('barcode')
        name = request.form.get('name')
        count = request.form.get('count', type=int)
        package_size_str = request.form.get('package_size')
        unit = request.form.get('unit')
        exp_str = request.form.get('expiration')
        
        location = request.form.get('location_select')
        if location == '_NEW_':
            location = request.form.get('location_new')
        
        session['last_location'] = location
        
        package_size = float(package_size_str) if package_size_str else None
        
        expiration = datetime.strptime(exp_str, '%Y-%m').date() if exp_str else None
        
        new_item = Item(barcode=barcode, name=name, count=count, package_size=package_size, unit=unit, expiration=expiration, location=location)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
        
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    if not locations:
        locations = ['Lednice', 'Mrazák', 'Špajz']
        
    last_loc = session.get('last_location', locations[0] if locations else '')
        
    return render_template('add.html', locations=locations, last_loc=last_loc)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_location', methods=['POST'])
def delete_location():
    loc_to_delete = request.form.get('location')
    if loc_to_delete:
        Item.query.filter_by(location=loc_to_delete).delete()
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_count/<int:id>/<action>', methods=['POST'])
def update_count(id, action):
    item = Item.query.get_or_404(id)
    
    if action == 'increase':
        item.count += 1
    elif action == 'decrease':
        item.count -= 1
        if item.count <= 0:
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('index'))
            
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/lookup/<barcode>')
def lookup(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        headers = {'User-Agent': 'MujSkladApp/1.0 - domaci_pouziti'}
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        
        if data.get('status') == 1:
            product = data.get('product', {})
            name = (product.get('product_name') or 
                    product.get('product_name_cs') or 
                    product.get('product_name_en') or 
                    product.get('generic_name') or 
                    product.get('generic_name_cs') or
                    product.get('brand_owner') or
                    '')
            quantity_str = product.get('quantity', '')
            
            return jsonify({'found': True, 'name': name, 'raw_quantity': quantity_str})
            
    except Exception as e:
        print(f"Chyba: {e}", flush=True)
        
    return jsonify({'found': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)