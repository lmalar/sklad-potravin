from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os
import csv
import sqlite3
from io import StringIO

app = Flask(__name__)
app.secret_key = os.urandom(24)
db_path = os.path.join(os.path.dirname(__file__), 'data', 'sklad.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50))
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, default='Potraviny')
    group_name = db.Column(db.String(100), nullable=False, default='')
    count = db.Column(db.Integer, nullable=False, default=1)
    package_size = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=False)
    expiration = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(item)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute("ALTER TABLE item ADD COLUMN category VARCHAR(50) DEFAULT 'Potraviny'")
    if 'group_name' not in columns:
        cursor.execute("ALTER TABLE item ADD COLUMN group_name VARCHAR(100) DEFAULT ''")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    loc_filter = request.args.get('location', '')
    cat_filter = request.args.get('category', '')
    search_q = request.args.get('q', '')
    sort_by = request.args.get('sort', 'expiration')
    
    if loc_filter in ('Všechny', 'None'): loc_filter = ''
    if cat_filter in ('Všechny', 'None'): cat_filter = ''
    
    query = Item.query
    if loc_filter:
        query = query.filter_by(location=loc_filter)
    if cat_filter:
        query = query.filter_by(category=cat_filter)
        
    if sort_by == 'name':
        query = query.order_by(Item.name.asc())
    elif sort_by == 'location':
        query = query.order_by(Item.location.asc())
    elif sort_by == 'category':
        query = query.order_by(Item.category.asc(), Item.group_name.asc())
    else:
        query = query.order_by(Item.expiration.asc())
        
    items = query.all()
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    categories = [c[0] for c in db.session.query(Item.category).distinct().all() if c[0]]
    
    def format_size(size):
        if size is None: return ""
        return int(size) if size.is_integer() else size
        
    def get_expiration_status(exp_date):
        if not exp_date: return ""
        today = datetime.now().date()
        months_diff = (exp_date.year - today.year) * 12 + (exp_date.month - today.month)
        if months_diff < 0: return "table-danger"
        elif months_diff <= 1: return "table-warning"
        return ""
        
    return render_template(
        'index.html',
        items=items,
        locations=locations,
        categories=categories,
        selected_loc=loc_filter,
        selected_cat=cat_filter,
        search_q=search_q,
        format_size=format_size,
        get_expiration_status=get_expiration_status
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        location = request.form.get('location_select')
        if location == '_NEW_':
            location = request.form.get('location_new', '').strip()
        session['last_location'] = location
        
        category = request.form.get('category_select')
        if category == '_NEW_':
            category = request.form.get('category_new', '').strip() or 'Potraviny'
            
        group_name = request.form.get('group_select')
        if group_name == '_NEW_':
            group_name = request.form.get('group_new', '').strip()
        
        ps_str = request.form.get('package_size')
        exp_str = request.form.get('expiration')
        
        new_item = Item(
            barcode=request.form.get('barcode'),
            name=request.form.get('name'),
            category=category,
            group_name=group_name or '',
            count=request.form.get('count', type=int),
            package_size=float(ps_str) if ps_str else None,
            unit=request.form.get('unit'),
            expiration=datetime.strptime(exp_str, '%Y-%m').date() if exp_str else None,
            location=location
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
        
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    categories = [c[0] for c in db.session.query(Item.category).distinct().all() if c[0]]
    groups = [g[0] for g in db.session.query(Item.group_name).distinct().all() if g[0]]
    
    if not locations: locations = ['Lednice', 'Mrazák', 'Špajz']
    if not categories: categories = ['Potraviny', 'Drogerie', 'Kosmetika']
    last_loc = session.get('last_location', locations[0] if locations else '')
    
    return render_template('add.html', locations=locations, categories=categories, groups=groups, last_loc=last_loc)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        location = request.form.get('location_select')
        if location == '_NEW_':
            location = request.form.get('location_new', '').strip()
            
        category = request.form.get('category_select')
        if category == '_NEW_':
            category = request.form.get('category_new', '').strip() or 'Potraviny'
            
        group_name = request.form.get('group_select')
        if group_name == '_NEW_':
            group_name = request.form.get('group_new', '').strip()

        item.barcode = request.form.get('barcode')
        item.name = request.form.get('name')
        item.category = category
        item.group_name = group_name or ''
        item.count = request.form.get('count', type=int)
        ps_str = request.form.get('package_size')
        item.package_size = float(ps_str) if ps_str else None
        item.unit = request.form.get('unit')
        exp_str = request.form.get('expiration')
        item.expiration = datetime.strptime(exp_str, '%Y-%m').date() if exp_str else None
        item.location = location
        db.session.commit()
        return redirect(url_for('index'))
        
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    categories = [c[0] for c in db.session.query(Item.category).distinct().all() if c[0]]
    groups = [g[0] for g in db.session.query(Item.group_name).distinct().all() if g[0]]
    if not categories: categories = ['Potraviny', 'Drogerie', 'Kosmetika']
    return render_template('edit.html', item=item, locations=locations, categories=categories, groups=groups)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_location', methods=['POST'])
def delete_location():
    loc = request.form.get('location')
    if loc:
        Item.query.filter_by(location=loc).delete()
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_count/<int:id>/<action>', methods=['POST'])
def update_count(id, action):
    item = Item.query.get_or_404(id)
    if action == 'increase': item.count += 1
    elif action == 'decrease':
        item.count -= 1
        if item.count <= 0: db.session.delete(item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/api/lookup/<barcode>')
def lookup(barcode):
    endpoints = [
        "https://world.openfoodfacts.org",
        "https://world.openbeautyfacts.org",
        "https://world.openproductsfacts.org"
    ]
    headers = {'User-Agent': 'MujSkladApp/1.0 - domaci_pouziti'}
    for base_url in endpoints:
        try:
            resp = requests.get(f"{base_url}/api/v0/product/{barcode}.json", headers=headers, timeout=5)
            data = resp.json()
            if data.get('status') == 1:
                product = data.get('product', {})
                name = (product.get('product_name') or product.get('product_name_cs') or product.get('product_name_en') or product.get('generic_name') or product.get('generic_name_cs') or product.get('brand_owner') or '')
                cats_str = product.get('categories', '')
                cats_list = [c.strip() for c in cats_str.split(',')] if cats_str else []
                category = cats_list[0] if cats_list else 'Potraviny'
                group = cats_list[-1] if len(cats_list) > 1 else ''
                return jsonify({'found': True, 'name': name, 'raw_quantity': product.get('quantity', ''), 'category': category, 'group': group})
        except Exception: continue
    return jsonify({'found': False})

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/export')
def export_csv():
    items = Item.query.order_by(Item.location.asc(), Item.category.asc(), Item.name.asc()).all()
    si = StringIO()
    cw = csv.writer(si, delimiter=';')
    cw.writerow(['Produkt', 'Kategorie', 'Skupina', 'EAN', 'Mnozstvi', 'Velikost', 'Jednotka', 'Sklad', 'Expirace'])
    
    for item in items:
        exp = item.expiration.strftime('%m/%Y') if item.expiration else ''
        cw.writerow([item.name, item.category, item.group_name, item.barcode, item.count, item.package_size, item.unit, item.location, exp])
        
    output = '\ufeff' + si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=sklad_export.csv"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
