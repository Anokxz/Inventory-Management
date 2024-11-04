from flask import Flask, request, render_template, make_response, redirect, url_for, flash, send_file, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
from io import BytesIO
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
login_manager.login_view = 'login' 
login_manager.login_message_category = 'warning'  

# Load env values
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWD = os.getenv('DB_PASSWD')

# DB connection
dbconfig = {
    "host": DB_HOST, 
    "user": DB_USER,
    "password":DB_PASSWD, 
    "database":"mini",
    "port": 24967,
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=6,  # Adjust the pool size as needed
    **dbconfig
)
class User(UserMixin):
    """Define a simple User model. Flask-Login requires this."""
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
# Load user from the db by their ID
@login_manager.user_loader
def load_user(user_id):
    user = sql_execute("SELECT * FROM users WHERE userID = %s", (user_id,))[0]
    if user:
        return User(id=user['userID'], username=user['username'], password=user['password'])
    return None


@app.route("/")
@login_required 
def index():
    return render_template("index.html")

@app.route('/materials', methods=['GET'])
def materials():
    materials = sql_execute("SELECT * FROM materials")
    return render_template('materials.html', materials=materials)

@app.route('/material/add', methods=['GET', 'POST'])
@login_required
def add_material():
    if request.method == 'POST':
        name,quantity,material_type = request.form['name'], request.form['quantity'], request.form['type']
        sql_execute("INSERT INTO materials (name, quantity, type) VALUES (%s, %s, %s)", (name, quantity, material_type))
        flash("Material added successfully!")
        
        return redirect(url_for('materials'))
    return render_template('material/add.html')

@app.route('/material/update', methods=['GET', 'POST'])
@login_required 
def update_material():    
    if request.method == 'POST':
        material_id = request.form['id']
        new_name = request.form['name']
        new_quantity = request.form['quantity']
        new_type = request.form['type']

        sql_execute("UPDATE materials SET name = %s, quantity = %s, type = %s WHERE id = %s", 
                       (new_name, new_quantity, new_type, material_id))

        flash("Material updated successfully!")
        return redirect(url_for('materials'))

    materials = sql_execute("SELECT * FROM materials")  
    return render_template('material/update.html', materials=materials)

@app.route('/material/remove', methods=['GET', 'POST'])
@login_required
def remove_material():    
    if request.method == 'POST':
        material_id = request.form['id']

        sql_execute("DELETE FROM materials WHERE id = %s", (material_id,))
        sql_execute("SET @new_id = 0;")
        sql_execute("UPDATE materials SET id = (@new_id := @new_id + 1);")
        sql_execute("ALTER TABLE materials AUTO_INCREMENT = 1;")

        flash("Material removed and IDs reordered successfully!")
        return redirect(url_for('materials'))

    materials =sql_execute("SELECT id, name FROM materials")
    return render_template('material/remove.html', materials=materials)

@app.route("/products", methods=["GET", "POST"])
def products():
    products = sql_execute("SELECT PID, name, Price, Descript, Img FROM products WHERE InStockCount > 0;")
    for product in products:
        if product['Img'] is not None:
            product['Img'] = base64.b64encode(product['Img']).decode('utf-8')
    return render_template("products.html", products=products)

@app.route("/product/<int:id>", methods=["GET"])
def product(id):
    product = sql_execute("SELECT PID, name, price, Img, Descript, category FROM products WHERE PID = %s AND InStockCount > 0", (id, ))

    if not product:
        return f"Product ID - {id} not found in the database", 404

    product = product[0]  # Get the first result
    
    if product['Img'] is not None:
        # Convert the binary image to base64
        product['Img'] = "data:image/jpeg;base64," + base64.b64encode(product['Img']).decode('utf-8')

    return render_template("product.html", product=product)

@app.route("/product/add", methods=['GET', 'POST'])
@login_required 
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        psize = request.form['psize']
        price = request.form['price']
        in_stock_count = request.form['in_stock_count']
        description = request.form['description']
        image = request.files['image'].read()
        sql_execute("INSERT INTO products (name, category, psize, Price, InStockCount, Descript, Img) VALUES (%s, %s, %s, %s, %s, %s, %s)", (name, category, psize, price, in_stock_count, description, image))
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))
    return render_template("product/add.html")

@app.route("/product/remove" , methods=['GET', 'POST'])
@login_required 
def remove_product():
    if request.method == 'POST' :
        id = request.form["product_id"]
        sql_execute("DELETE FROM products WHERE PID = %s", (id,))
        sql_execute("SET @new_id = 0;")
        sql_execute("UPDATE products SET id = (@new_id := @new_id + 1);")
        sql_execute("ALTER TABLE products AUTO_INCREMENT = 1;")        
        flash('Product removed successfully!', 'success')
        return redirect("/products")
    products = sql_execute("select PID, name, category from products;")
    return render_template("product/remove.html", products=products)

@app.route("/product/update")
@login_required 
def update_product():
    return render_template("product/update.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        user = sql_execute("select userID, password from users where username=%s" ,(username, ))[0]
        if user and check_password_hash(user["password"], password):
            logged_in_user = User(id=user['userID'], username=username, password=user['password'])
            login_user(logged_in_user)
            return redirect('/')
        flash("Invalid username or password", category='error')
        # return render_template("login.html", error=True)

    return render_template("login.html")

@app.route('/transactions')
@login_required
def transactions():
    # cursor = connection.cursor(dictionary=True)
    # cursor.execute("SELECT * FROM transactions;") 
    # transactions = cursor.fetchall()

    return render_template("payment.html")

@app.route('/transaction/add')
@login_required
def add_transactions():
    return render_template("add_transaction.html")

@app.route('/transaction/bill')
@login_required
def bill_transactions():
    return render_template("bill.html")

@app.route('/update_status', methods=['POST'])
def update_status():
    customization_id = request.form['customization_id']
    new_status = request.form['status']
    try:
        sql_execute(
            "UPDATE customizations SET status = %s WHERE id = %s",
            (new_status, customization_id)
        )
        flash('Status updated successfully!', 'success')
    except Exception as e:
        flash('An error occurred while updating status.', 'error')
        print(e)  # For debugging

    return redirect(url_for('customize_status'))

# Route to render the customization details page
@app.route('/customize_status')
def customize_status():
    sql_execute("SET @new_id = 0;")
    sql_execute("UPDATE customizations SET id = (@new_id := @new_id + 1);")
    sql_execute("ALTER TABLE customizations AUTO_INCREMENT = 1;") 
    customizations = sql_execute("SELECT * FROM customizations")
    return render_template("customize_status.html", customizations=customizations)

@app.route('/customize/<int:id>', methods=['GET', 'POST'])
def customize(id):
    product = sql_execute("select PID, name from products where PID = %s", (id, ))[0]

    if request.method == 'POST':
        # Retrieve form data
        product_id = product['PID']
        name=product['name']
        length = request.form['length']
        width = request.form['width']
        height = request.form['height']
        material = request.form['material']
        extra_description = request.form['extraDescription']

        # Save the data to the database
        sql_execute("INSERT INTO customizations (product_id,name, length, width, height, material, description) VALUES (%s,%s, %s, %s, %s, %s, %s)",
                    (id,name, length, width, height, material, extra_description))

        flash('Customization saved successfully!', 'success')
        return redirect(url_for('customize_status'))

    
    return render_template("customize.html", product=product)  

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
    app.permanent_session_lifetime = timedelta(minutes=30)

def sql_execute(command, fields=()):
    connection = connection_pool.get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(command, fields)
        output = cursor.fetchall()  # Fetch the result
    except mysql.connector.errors.InternalError as e:
        # Handle the unread result error by clearing old results
        if "Unread result found" in str(e):
            cursor.fetchall()  # Clear the unread results
            cursor.execute(command, fields)  # Re-run the query
            output = cursor.fetchall()
        else:
            output = []
    except:
        output = []
    finally:
        connection.commit()  
        cursor.close()
        connection.close()
    return output


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)