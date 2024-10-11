from flask import Flask, request, render_template, make_response, redirect, url_for, flash, send_file
import io
import json
import base64
import os
from dotenv import load_dotenv
import mysql.connector

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

app = Flask(__name__)
app.secret_key = "mini-inventory"

@app.route("/")
def index():
    return render_template("index.html")


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

    return render_template('materials.html', materials=materials,admin_password=os.getenv('ADMIN_PASSWORD'))

@app.route('/add', methods=['GET', 'POST'])
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

    return render_template('add.html')

@app.route('/update', methods=['GET', 'POST'])
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
    
    return render_template('update.html', materials=materials)


@app.route('/remove', methods=['GET', 'POST'])
def remove_material():
    cursor = connection.cursor()
    
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

    cursor.execute("SELECT * FROM materials")
    materials = cursor.fetchall()
    
    return render_template('remove.html', materials=materials)




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
def add_product():
    return render_template("add_product.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if username == "admin" and password == "admin":
            return redirect('/')
        flash("Invalid Login", category='error')
        return render_template("login.html", error=True)

    return render_template("login.html")


@app.route('/logout')
def logout():
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
