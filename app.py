from flask import Flask,request, render_template,make_response,redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/import_materials")
def import_materials():
    return render_template("import.html")

@app.route("/customize_design")
def customize_design():
    return "TODO customize_design"

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
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        
        if username == "admin" and password == "admin":
            # Add this to session storage
            return redirect('/')
        return "Display error in login page"
        return  render_template("login.html", error=True)
    #GET METHOD
    return render_template("login.html")

@app.route('/logout')
def logout():
    return redirect('/login')