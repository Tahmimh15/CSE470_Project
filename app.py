from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for security
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate= Migrate(app, db)

#Create Classes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), default="Free", nullable=False)
    events = db.relationship('Event', backref='host', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    privacy =  db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitations = db.relationship('Invitation', back_populates='event')


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event = db.relationship('Event', back_populates='invitations')
    user = db.relationship('User')


# Run this once to create the database
with app.app_context():
    db.create_all()

#Functions

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    user_events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', user=current_user, user_events=user_events)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid login credentials', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists', 'danger')
        else:
            new_user = User(email=email, username=username, fname=fname, lname=lname)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/change_role', methods=['GET'])
@login_required
def switch_role():
    if current_user.role == 'Free':
        current_user.role = 'Premium'
        db.session.commit()
        flash('Role switched to Premium successfully!', 'success')
    else:
        current_user.role = 'Free'
        db.session.commit()
        flash('Role switched to Free successfully!', 'success')

    return redirect(url_for('home'))

@app.route('/view_events')
@login_required
def events():
    events = Event.query.filter_by(privacy='Public').all()
    return render_template('events.html', events=events)


@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role == 'Premium':
        if request.method == 'POST':
            event_name = request.form['event_name']
            location = request.form['location']
            description = request.form['description']
            privacy = request.form['privacy']

            new_event = Event(event_name=event_name, location=location, description=description, host=current_user, privacy=privacy)
            db.session.add(new_event)
            db.session.commit()

            flash('Post created successfully!', 'success')
            return redirect(url_for('home'))

        return render_template('create_event.html')
    
    else:
        flash('Only Premium users can access this!', 'danger')
        return redirect(url_for('events'))
    

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user.id == event.user_id:
        if request.method == 'POST':
            event.event_name = request.form['event_name']
            event.location = request.form['location']
            event.description = request.form['description']

            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('home'))

        return render_template('edit_event.html', event=event)
    else:
        flash('Permission denied. Admins or event authors only!', 'danger')
        return redirect(url_for('home'))

@app.route('/delete_event/<int:event_id>', methods=['GET'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user.id == event.user_id:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
    else:
        flash('Permission denied. Admins or event authors only!', 'danger')

    return redirect(url_for('home'))

@app.route('/search_event', methods=['GET', 'POST'])
@login_required
def search_event():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')

        searched_events = Event.query.filter(
        Event.event_name.ilike(f"%{search_query}%") |
        Event.description.ilike(f"%{search_query}%") |
        Event.location.ilike(f"%{search_query}%")
        ).all()

        return render_template('search_event.html', searched_events = searched_events)
    
    else:
        flash('Only Premium users can access this!', 'danger')
        return redirect(url_for('events'))




if __name__ == '__main__':
    app.run(debug=True)
