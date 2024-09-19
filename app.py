from flask import Flask,request, render_template,make_response,redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/import_raw_materials")
def import_raw_materials():
    return "TODO import_raw_materials"

@app.route("/customize_furniture_degsin")
def customize_furniture_degsin():
    return "TODO customize_furniture_degsin"

@app.route("/available_products")
def available_products():
    return "TODO available_products"

@app.route("/stock_view")
def stock_view():
    return "TODO stock_view"

@app.route("/payment_transaction")
def payment_transaction():
    return "TODO payment_transaction"

@app.route("/analysis")
def analysis():
    return "TODO analysis"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        return "todo login"
        # return redirect(url_for('index'))
    
    #GET METHOD
    return render_template("login.html")

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # Handle registration logic (storing user info in DB)
    # For now, just redirect to the same page
    return "todo register"

@app.route('/google-sign-in', methods=['POST'])
def google_sign_in():
    # Handle Google Sign-In logic
    return "google sign-in"

@app.route('/logout')
def logout():
    return redirect('/login')