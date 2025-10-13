from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Fake user database for testing
users = {
    "Rob": "password",
    "Benny": "password"
}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Simple authentication check
    if username in users and users[username] == password:
        return f"<h1>Welcome, {username}!</h1>"
    else:
        return "<h1>Invalid username or password</h1><a href='/'>Try again</a>"

if __name__ == '__main__':
    app.run(debug=True)
