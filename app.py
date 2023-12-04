
from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')




if __name__ == '__main__':
    app.run(debug=True)


app = Flask(__name__)
app.secret_key = 'your_secret_key'  

users = [
    {'email': 'user1@example.com', 'password': 'pass1', 'type': 'premium'},
    {'email': 'user2@example.com', 'password': 'pass2', 'type': 'public'},
]

@app.route('/')
def index():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    login_type = request.form.get('login-type')

    # Check if the user exists and the password is correct
    user = next((user for user in users if user['email'] == email and user['password'] == password), None)

    if user and user['type'] == login_type:
        session['user'] = user
        return redirect(url_for('index'))

    return "Invalid credentials or login type."

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

