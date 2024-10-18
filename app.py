from flask import Flask, request, render_template, make_response, redirect, url_for, flash, send_file, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
import io
import json
import base64
import os
from dotenv import load_dotenv
import mysql.connector
from werkzeug.security import check_password_hash

# Initialize Flask APP
app = Flask(__name__)
app.secret_key = "mini-inventory"

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Where to redirect if user is not logged in
login_manager.login_message_category = 'warning'  # Flash message category for login required

# Load environment variables
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWD = os.getenv('DB_PASSWD')

# Database connection
connection = mysql.connector.connect(
    host=DB_HOST, 
    user=DB_USER,
    password=DB_PASSWD, 
    database="mini",
    port=24967
)

class User(UserMixin):
    """Define a simple User model. Flask-Login requires this."""
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
# Load user from the database by their ID
@login_manager.user_loader
def load_user(user_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE userID = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return User(id=user['userID'], username=user['username'], password=user['password'])
    return None


@app.route("/")
@login_required 
def index():
    return render_template("index.html")

@app.route('/verify_password', methods=['POST'])
def verify_password():
    data = request.json
    password = data.get('password')

    # Assume you have a database connection 'conn'
    conn = connection  
    cursor = conn.cursor(dictionary=True)
    
    # Retrieve the hashed password for the admin user
    cursor.execute("SELECT password FROM users WHERE username = 'admin';")
    result = cursor.fetchone()  # Fetch the first matching result
    cursor.close()

    # Check if the admin user exists and if the provided password matches the stored hash
    if result and check_password_hash(result['password'], password):
        return jsonify(success=True), 200
    else:
        return jsonify(success=False), 403

@app.route('/materials', methods=['GET', 'POST'])
def materials():
    conn = connection  
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        action = request.form['action']
        name = request.form['name']
        quantity = request.form.get('quantity', 0)

        if action == 'add':
            cursor.execute("INSERT INTO materials (name, quantity, remaining, used) VALUES (%s, %s, %s, %s)", 
                           (name, quantity, quantity, 0))
            flash("Material added successfully!")
        elif action == 'update':
            cursor.execute("UPDATE materials SET quantity = %s, remaining = remaining + %s WHERE name = %s", 
                           (quantity, quantity, name))
            flash("Material updated successfully!")
        elif action == 'remove':
            cursor.execute("DELETE FROM materials WHERE name = %s", (name,))
            flash("Material removed successfully!")
        
        conn.commit()

    cursor.execute("SELECT * FROM materials")
    materials = cursor.fetchall()

    
    cursor.close()

    return render_template('materials.html', materials=materials,admin_password="Hello World")

@app.route('/material/add', methods=['GET', 'POST'])
@login_required
def add_material():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        material_type = request.form['type']

        cursor = connection.cursor()
        cursor.execute("INSERT INTO materials (name, quantity, type) VALUES (%s, %s, %s)", (name, quantity, material_type))
        connection.commit()
        flash("Material added successfully!")
        return redirect(url_for('materials'))

    return render_template('material/add.html')

@app.route('/material/update', methods=['GET', 'POST'])
@login_required 
def update_material():
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        material_id = request.form['id']
        new_name = request.form['name']
        new_quantity = request.form['quantity']
        new_type = request.form['type']

        cursor.execute("UPDATE materials SET name = %s, quantity = %s, type = %s WHERE id = %s", 
                       (new_name, new_quantity, new_type, material_id))
        connection.commit()
        flash("Material updated successfully!")
        return redirect(url_for('materials'))

    cursor.execute("SELECT * FROM materials")
    materials = cursor.fetchall()    
    return render_template('material/update.html', materials=materials)


@app.route('/material/remove', methods=['GET', 'POST'])
@login_required
def remove_material():
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        material_id = request.form['id']

        cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))
        connection.commit()

        cursor.execute("SET @new_id = 0;")
        cursor.execute("UPDATE materials SET id = (@new_id := @new_id + 1);")
        connection.commit()

        cursor.execute("ALTER TABLE materials AUTO_INCREMENT = 1;")
        connection.commit()

        flash("Material removed and IDs reordered successfully!")
        return redirect(url_for('materials'))

    cursor.execute("SELECT id, name FROM materials")
    materials = cursor.fetchall()
    return render_template('material/remove.html', materials=materials)

@app.route("/products", methods=["GET", "POST"])
def available_products():
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM products;") 
    products = cursor.fetchall()

    for product in products:
        product["Img"] = base64.b64encode(product["Img"]).decode('utf-8')
    
    cursor.close()
    return render_template("products.html", products=products)

@app.route("/product", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        new_product = request.form.to_dict()
        image = request.files['image'].read()

        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (name, category, psize, Price, InStockCount, Img, Descript) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (new_product["name"], new_product["category"], new_product["psize"], 
                        new_product["price"], new_product["in_stock_count"], image, new_product["description"]))
        connection.commit()
        cursor.close()

        return redirect("/products")


@app.route("/product/add")
@login_required 
def add_product():
    return render_template("add_product.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        cursor = connection.cursor(dictionary=True)
        cursor.execute("select userID, password from users where username=%s" ,(username, ))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            logged_in_user = User(id=user['userID'], username=username, password=user['password'])
            login_user(logged_in_user)
            return redirect('/')
        flash("Invalid username or password", category='error')
        # return render_template("login.html", error=True)

    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(error=None):
    return "O_0 404 NOT FOUND"

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=10)

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)