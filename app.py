from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key'  # Replace with an actual secure secret key

# Dummy user data (replace with your authentication logic)
users = {
    'user1@example.com': {'password': 'password1', 'type': 'premium'},
    'user2@example.com': {'password': 'password2', 'type': 'public'},
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    login_type = request.form.get('login-type')

    if email in users and users[email]['password'] == password:
        session['user'] = {
            'email': email,
            'type': login_type,
        }
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error='Invalid credentials')

@app.route('/home')
def home():
    user = session.get('user')
    if user:
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('registration.html')

if __name__ == '__main__':
    app.run(debug=True)

