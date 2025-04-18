import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from datetime import datetime
import uuid  # Import the uuid module
from reportlab.lib.pagesizes import letter
from barcode import EAN13
from barcode.writer import ImageWriter

from reportlab.lib import colors

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"




app.config.from_object(Config)
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    business_id = db.Column(db.Integer, nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.DateTime, default=db.func.now())

class LowStockAlert(db.Model):
    
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    business_id = db.Column(db.Integer, nullable=False)    
    alert_date = db.Column(db.DateTime, default=db.func.now())
    message = db.Column(db.String(255), nullable=False)


def create_alert(product_id, business_id, message):
    
    new_alert = LowStockAlert(product_id=product_id, business_id=business_id, message=message)
    return new_alert

def get_alert(alert_id):
    
    alert = LowStockAlert.query.get_or_404(alert_id)
    return alert

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    last_update = db.Column(db.DateTime, default=db.func.now())
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    business_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)

class Inventory(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    entry_date = db.Column(db.DateTime, default=db.func.now())
    type = db.Column(db.String(50), nullable=False)  
    business_name = db.Column(db.String(100), nullable=False)
def create_inventory(product_id, quantity, type, business_name):
    
    new_inventory = Inventory(product_id=product_id, quantity=quantity, type=type, business_name=business_name)
    return new_inventory
def get_inventory(product_id):
    
    pass
def create_sale(product_id, quantity, business_name):
    
    new_sale = Sale(product_id=product_id, quantity=quantity, business_name=business_name)
    return new_sale

def get_sale(sale_id):
    
    sale = Sale.query.get_or_404(sale_id)
    return sale
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, default=db.func.now())
    business_name = db.Column(db.String(100), nullable=False)


def update_sale(sale, product_id, quantity, business_name):    
    sale.product_id = product_id
    sale.quantity = quantity
    sale.business_name = business_name

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_information = db.Column(db.String(200))
    business_id = db.Column(db.Integer, nullable=False)

def create_supplier(name, business_id):
    


    new_provider = Provider(name=name, business_id=business_id)
    return new_provider

with app.app_context():
      db.create_all()

# Routes
@app.route("/") 
def main():  
    return render_template('index.html')  
@app.route("/index")

def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':   
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        business_name = request.form.get('business_name')

        if not all([name, lastname, email, password, confirm_password, business_name]):
            flash('All fields are required')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        business_id = uuid.uuid4().int & (1<<32)-1
        new_user = User(name=name, lastname=lastname, email=email, password=hashed_password, business_name=business_name, business_id=business_id)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!')
        return redirect(url_for('login'))
    return render_template('register.html') 
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Inicio de sesión exitoso!')
            return redirect(url_for('main'))
        elif not user:
            flash('Usuario no encontrado', 'error')

        else:
            flash('Correo electrónico o contraseña inválidos', 'error')
    return render_template('login.html')

@app.route("/products")
def list_products():
    
    user = User.query.first()
    if not user:
        flash('No se encontró el usuario')
        return redirect(url_for('login'))
    business_id = user.business_id
    products = Product.query.filter_by(business_id=business_id).all()
    return render_template('products.html', products=products)

    
@app.route("/products/add", methods=['GET', 'POST'])
def create_product():
    
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        barcode = request.form.get('barcode')
        name = request.form.get('name')
        cost_price = request.form.get('cost_price')
        sale_price = request.form.get('sale_price')
        file = request.files['image']
        image = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = filename

        provider_id = request.form.get('provider_id')

        if not all([barcode, name, cost_price, sale_price, provider_id]):
            flash('Todos los campos son requeridos')
            return redirect(url_for('add_product'))
        if Product.query.filter_by(barcode=barcode, business_id=business_id).first():
            flash('El código de barras ya está registrado')
            return redirect(url_for('add_product'))

        try:
            cost_price = float(cost_price)
            sale_price = float(sale_price)
            provider_id = int(provider_id)
        except ValueError:
            flash('Precio de costo y de venta deben ser números', 'error')
            return redirect(url_for('add_product'))
        new_product = Product(barcode=barcode, name=name, cost_price=cost_price, sale_price=sale_price, provider_id=provider_id, business_id=business_id, image=image)
        db.session.add(new_product)        
        db.session.commit()

        flash('Producto añadido exitosamente!', 'success')
        return redirect(url_for('list_products'))
        
    providers = Provider.query.filter_by(business_id=business_id).all()
    return render_template('product_form.html', providers=providers, is_edit=False)

@app.route("/products/edit/<int:product_id>", methods=['GET', 'POST'])
def edit_product(product_id):
    
    product = Product.query.get_or_404(product_id)
    user = User.query.first()
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    if request.method == 'POST':
        product.barcode = request.form['barcode']
        product.name = request.form['name']
        product.cost_price = float(request.form['cost_price'])
        product.sale_price = float(request.form['sale_price'])
        product.last_update = datetime.now()

        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
        product.provider_id = int(request.form['provider_id'])

        if not all([product.barcode, product.name, product.cost_price, product.sale_price, product.provider_id]):
            flash('All fields are required')
            return redirect(url_for('edit_product', product_id=product_id))   
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error editando producto: '+str(e), 'error')
        flash('Producto actualizado exitosamente!', 'success')
        return redirect(url_for('list_products'))
    providers = Provider.query.filter_by(business_id=user.business_id).all()
    return render_template('product_form.html', product=product, providers=providers, is_edit=True)
@app.route("/products/delete/<int:product_id>", methods=['POST'])
@app.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Producto eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error eliminando producto: '+str(e), 'error')
    return redirect(url_for('list_products'))

@app.route("/inventory")
def inventory_history():
    user = User.query.first()
    if not user:
        flash('No se encontró el usuario')
        return redirect(url_for('login'))
    history = Inventory.query.filter_by(business_name=user.business_name).order_by(Inventory.entry_date.desc()).all()
    return render_template('history.html', history=history)

def get_product(product_id):
    
    
    product = Product.query.get_or_404(product_id)
    return product
    
@app.route("/pos", methods=['GET', 'POST'])
def pos():
    user = User.query.first()
    business_name = user.business_name
    products = Product.query.filter_by(business_name=business_name).all()

    user = User.query.first()
    if not user:
        flash('No se encontró el usuario')
        return redirect(url_for('login'))
    business_id = user.business_id    
    if request.method == 'POST':      
        cart = request.form.getlist('cart[]')
        total_price = 0
        for item in cart:
            product_id, quantity = item.split('-')
            product_id = int(product_id)
            quantity = int(quantity)
            product = Product.query.get_or_404(product_id)
            total_price += product.sale_price * quantity
            
        if 'process_payment' in request.form:           
            for item in cart:
                product_id, quantity = item.split('-')
                product_id = int(product_id)
                quantity = int(quantity)
                product = Product.query.get_or_404(product_id)

                # Create sale record
                sale = Sale(product_id=product.id, quantity=quantity, business_name=business_name)
                db.session.add(sale)
                # Update inventory
                inventory = Inventory(product_id=product.id, quantity=quantity, type='exit', business_name=business_name)
                db.session.add(inventory)
                # Update product stock
                current_inventory = Inventory.query.filter_by(product_id=product.id, type='entry').all()
                current_stock = 0
                for entry in current_inventory:
                    current_stock += entry.quantity
                current_exits = Inventory.query.filter_by(product_id=product.id, type='exit').all()
                for exit in current_exits:
                    current_stock -= exit.quantity
                if current_stock < 0 :
                    low_stock_alert = LowStockAlert.query.filter_by(product_id=product.id, business_id=business_id).first()
                    if not low_stock_alert:
                        new_low_stock_alert = LowStockAlert(product_id=product.id, business_id=business_id, message='Stock is low for product '+ product.name + ', current stock is '+ str(current_stock))
                        db.session.add(new_low_stock_alert)
                        db.session.commit()
                elif current_stock > 0:

                    low_stock_alert = LowStockAlert.query.filter_by(product_id=product.id, business_id=business_id).first()
                    if low_stock_alert:
                        db.session.delete(low_stock_alert)
                    flash('No hay stock suficiente del producto '+ product.name +'!')
                    
                    return render_template('pos.html', products=products, total_price=total_price, cart=cart)
            db.session.commit()
            
            flash('Payment processed successfully!')
        else:
            flash('The cart is empty!')
        return render_template('pos.html', products=products, total_price=total_price)
    return render_template('pos.html', products=products)

@app.route("/providers")
def list_providers():
    user = User.query.first()
    providers = Provider.query.filter_by(business_id=user.business_id).all()
    return render_template('suppliers.html', providers=providers)

    try:
        db.session.delete(provider)
        db.session.commit()
        flash('Proveedor eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error eliminando proveedor: '+str(e), 'error')
    return redirect(url_for('list_providers'))
    
@app.route("/providers/add", methods=['GET', 'POST'])
def create_provider():
    

    user = User.query.first()
    if request.method == 'POST':
        name = request.form['name']
        if not name:
            flash('Name is required!', 'error')
            return redirect(url_for('create_provider'))
            
        try:
            new_provider = create_supplier(name, user.business_id)
            db.session.add(new_provider)
            db.session.commit()
            flash('Provider added successfully!', 'success')
            return redirect(url_for('list_providers'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding provider: '+str(e), 'error')
            return redirect(url_for('create_provider'))
    return render_template('supplier_form.html')
@app.route("/providers/edit/<int:provider_id>", methods=['GET', 'POST'])
def edit_provider(provider_id):
    
    provider = Provider.query.get_or_404(provider_id)
    if request.method == 'POST':
        provider.name = request.form['name']
        try:
            db.session.commit()
            flash('Proveedor editado exitosamente!', 'success')
            return redirect(url_for('list_providers'))
        except Exception as e:
            db.session.rollback()
            flash('Error editando proveedor: '+str(e), 'error')
        return redirect(url_for('list_providers'))
    
    return render_template('supplier_form.html', provider=provider, is_edit=True)

def delete_provider(provider_id):
        
    provider = Provider.query.get_or_404(provider_id)
    try:
        db.session.delete(provider)
        db.session.commit()
        flash('Proveedor eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error eliminando proveedor: '+str(e), 'error')
    return redirect(url_for('list_providers'))
@app.route("/analytics")
def analysis():
    user = User.query.first()
    if not user:
        flash('No se encontró el usuario')
        return redirect(url_for('login'))
    alerts = LowStockAlert.query.filter_by(business_id=user.business_id).all()
    return render_template('analytics.html', alerts=alerts)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=3001)
