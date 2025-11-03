from flask import Flask, render_template, request, redirect, url_for, session
import os

# search in ./CampusCostMethods/ for CampusCostMethods
import sys
sys.path.append('./CampusCostMethods')
import CampusCostMethods

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key required for session management


# ROUTES
# -------------------
# Home page / login page
@app.route('/')
def home():
    return render_template('login.html')

# Login form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if username exists and password matches
    if CampusCostMethods.authenticateLogin(username,password): 
        session['username'] = username  # Save user in session
        return index() 
    else:
        # Invalid login
        return "<h1>Invalid username or password</h1><a href='/'>Try again</a>"

# Register / create account page
@app.route('/register')
def register():
    return render_template('register.html')
    
#Load vending machine template page
# Load data to vending_temp html
@app.route('/vending_temp/data')
def vending_temp():
    # Pretend this is data from SQL
    items = [
        {"name": "Candy Bar", "price": 1.25, "available": True},
        {"name": "Chips", "price": 1.00, "available": True},
        {"name": "Soda", "price": 1.50, "available": False}
    ]

    return render_template('vending_temp.html', items=items)
    
#Load main menu page
@app.route('/index')
def index():
    buildings = []
    buildings = CampusCostMethods.fetchBuildings()
    
    
    return render_template('index.html', blding = buildings)
    
#TODO: Method to handle finding photo 

# Handle registration form submission
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    
    # Check if user already exists, if not newUser adds to database
    if not CampusCostMethods.newUser(username,password): 
        return "<h1>Username already exists!</h1><a href='/register'>Try again</a>"
    else:
        return "<h1>Account created successfully!</h1><a href='/'>Login here</a>"





# RUN THE APP
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
