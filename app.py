from flask import Flask,request, render_template,make_response,redirect, url_for,flash, send_file
import io
import json
import base64

import os
from dotenv import load_dotenv
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWD = os.getenv('DB_PASSWD')

import mysql.connector
connection = mysql.connector.connect(
    host=DB_HOST, 
    user=DB_USER,
    password=DB_PASSWD, 
    database="mini",
    port="24967"
)

app = Flask(__name__)
app.secret_key = "mini-inventory"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/materials")
def materials():
    return render_template("materials.html")

@app.route("/customize_design")
def customize_design():
    return "TODO customize_design"

@app.route("/products", methods=["GET", "POST"])
def available_products():
    if request.method == "POST":
        pass
 
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("select * from products;") 

    products = cursor.fetchall()
    for product in products:
        # product["Img"] = send_file(io.BytesIO(product["Img"]), mimetype='image/jpeg')
        product["Img"] = base64.b64encode(product["Img"]).decode('utf-8')
    return render_template("products.html", products=products)

@app.route("/product", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        new_product = request.form.to_dict()
        image = request.files['image'].read()

        
        cursor = connection.cursor()
        cursor.execute("Insert into products(name, category, psize, Price, InStockCount, Img, Descript) \
                        values(%s ,%s ,%s ,%s ,%s ,%s ,%s)",\
                (new_product["name"],new_product["category"],new_product["psize"],\
                new_product["price"],new_product["in_stock_count"],image,new_product["description"]))
        connection.commit()

        return redirect("/products") 

@app.route("/product/add")
def add_product():
    return render_template("add_product.html")

@app.route("/stock_view")
def stock_view():
    return "TODO stock_view"

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/transaction")
def transaction():
    return render_template("transaction.html")

@app.route("/analysis")
def analysis():
    return "TODO analysis"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        
        if username == "admin" and password == "admin":
            # Add this to session storage
            return redirect('/')
        flash("Invalid Login", category='error')
        return  render_template("login.html", error=True)
    #GET METHOD
    return render_template("login.html")

@app.route('/logout')
def logout():
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)