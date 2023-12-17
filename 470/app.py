from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime  #maisha


app = Flask("Nimontron", static_url_path="/static")
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Set a secret key for security
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate= Migrate(app, db)

#Create Classes
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    fname = db.Column(db.String(80), nullable=False)
    lname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(255), default="Free", nullable=False)
    events = db.relationship('Event', backref='host', lazy=True)
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(255), unique=True, nullable=False)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password_hash = db.Column(db.String(120), nullable=False)
#     fname = db.Column(db.String(255), nullable=False)
#     lname = db.Column(db.String(255), nullable=False)
#     role = db.Column(db.String(255), default="Free", nullable=False)
#     events = db.relationship('Event', backref='host', lazy=True)
    def get_id(self):
        return self.id

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)


# class User(db.Model, UserMixin):
#     __tablename__ = 'user2'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(80), nullable=False)
#     fname = db.Column(db.String(80), nullable=False)
#     lname = db.Column(db.String(80), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     role = db.Column(db.String(255), default="Free", nullable=False)
#     events = db.relationship('Event', backref='host', lazy=True)

#     def get_id(self):
#         return self.id

#     def __repr__(self):
#         return f"User2(id={self.id}, username='{self.username}')"


@app.route("/invite", methods=['GET', 'POST'])
def invite():
    registered_users= User.query.all()
    return render_template("invite.html", registered_users=registered_users)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(255), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    privacy =  db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitations = db.relationship('Invitation', back_populates='event')
    # Added fields for ticketing purposes   #maisha
    has_seating_chart = db.Column(db.Boolean, default=False)
    seating_chart_url = db.Column(db.String(255), nullable=True)
    

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event = db.relationship('Event', back_populates='invitations')
    user = db.relationship('User')

class Ticket(db.Model): #maisha
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    seat_number = db.Column(db.String(20), nullable=True)
    price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=True)
    # Add more fields as needed, such as purchase status, etc.

    event = db.relationship('Event', backref='tickets')
    user = db.relationship('User', backref='tickets')

class Seat(db.Model): #maisha
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    seat_number = db.Column(db.String(20), nullable=False)
    seat_type = db.Column(db.String(20), nullable=False)  # 'Gold' or 'Standard'
    price = db.Column(db.Float, nullable=False)

    event = db.relationship('Event', backref='seats')

class Wallet(db.Model): #maisha
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

    user = db.relationship('User', backref='wallet', uselist=False)


# Run this once to create the database

#with app.app_context():
    #db.create_all()

#Functions

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def premium_required(func):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isPremium(): 
            flash('Premium users only!', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_function


class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4,max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')



@app.route('/homepage')
@login_required
def home():
    user_events = Event.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', user=current_user, user_events=user_events)

# @app.route('/login', methods=['GET', 'POST'])

# def login():
#     form = UserLoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user:
#             if check_password_hash(user.password_hash, form.password.data):
#                 login_user(user)
#                 flash('Login successful!', 'success')
#                 return redirect(url_for('home'))
#             else:
#                 flash('Invalid login credentials', 'danger')
#         else:
#             flash('Invalid login credentials', 'danger')
#     return render_template('login.html', form=form)


# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()

#         if user and user.check_password(password):
#             login_user(user)
#             flash('Login successful!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Invalid login credentials', 'danger')

#     return render_template('login.html')


#from your_forms_file import UserLoginForm  # Import the form you've created


# def login():
#     form = UserLoginForm()

#     if form.validate_on_submit():
#         print("I am inside if condition.....")
#         email = form.email.data
#         password = form.password.data

#         user = User.query.filter_by(email=email).first()

#         if user and user.check_password(password):
#             # Login successful logic
#             login_user(user)  # This is the missing part
#             flash('Login successful!', 'success')
#             # Redirect to appropriate page after login
#             return redirect(url_for('index'))
#         else:
#             flash('Invalid login credentials', 'danger')

#     return render_template('login.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        instructor = User.query.filter_by(username=form.username.data).first()

        if instructor and form.password.data == instructor.password:
            login_user(instructor)  # Log in the instructor
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        flash('Login failed. Please check your credentials.', 'danger')

    return render_template('login.html', form=form)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         fname = request.form['fname']
#         lname = request.form['lname']
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']

#         existing_user = User.query.filter_by(username=username).first()

#         if existing_user:
#             flash('Username already exists', 'danger')
#         else:
#             new_user = User(email=email, username=username, fname=fname, lname=lname)
#             new_user.set_password(password)
#             db.session.add(new_user)
#             db.session.commit()
#             flash('Registration successful! Please log in.', 'success')
#             return redirect(url_for('login'))

#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = User2RegistrationForm()
    if form.validate_on_submit():
        new_instructor = User(username=form.username.data, password=form.password.data, email=form.email.data, fname=form.fname.data, lname=form.lname.data)
        db.session.add(new_instructor)
        db.session.commit()

        # Create a wallet for the new user  #maisha
        new_wallet = Wallet(user_id=new_instructor.id)
        db.session.add(new_wallet)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



class User2RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max =20)],render_kw={"placeholder": "Password"})
    fname = StringField('First Name', validators=[InputRequired()],render_kw={"placeholder": "First name"})
    lname = StringField('Last Name', validators=[InputRequired()],render_kw={"placeholder": "Last name"})
    email = StringField('Email', validators=[InputRequired(), Length(min=4, max =20)],render_kw={"placeholder": "Email"})
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('This username already exists, choose a different username.') 
        
@app.route('/register', methods=['GET','POST'])
# def register():
#     form = User2RegistrationForm()
#     if form.validate_on_submit():
#         new_instructor = User(username=form.username.data,password=form.password.data,email=form.email.data,fname=form.fname.data,lname=form.lname.data)
#         db.session.add(new_instructor)
#         db.session.commit()
#         #return render_template('instructor_login.html')
#         return redirect(url_for('login'))
    
#     return render_template('register.html', form=form)

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
            has_seating_chart = request.form.get('has_seating_chart', False)
            seating_chart_url = request.form.get('seating_chart_url', '')
            total_seats = int(request.form['total_seats'])

            # Fetch and handle other ticketing details (e.g., date, timings) #maisha

            new_event = Event(event_name=event_name, location=location, description=description, host=current_user, privacy=privacy, has_seating_chart=has_seating_chart, seating_chart_url=seating_chart_url)
            db.session.add(new_event)
            db.session.commit()

            seat_details = []
            for i in range(1, total_seats + 1):
                seat_number = request.form[f'seat_{i}_number']
                seat_type = request.form[f'seat_{i}_type']
                seat_price = float(request.form[f'seat_{i}_price'])
                seat_details.append({'seat_number': seat_number, 'seat_type': seat_type, 'seat_price': seat_price})

            for seat in seat_details:
                new_seat = Seat(event_id=new_event.id, seat_number=seat['seat_number'], seat_type=seat['seat_type'], price=seat['seat_price'])
                db.session.add(new_seat)
            db.session.commit()

            flash('Event created successfully!', 'success')
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

@app.route('/purchase/<int:event_id>', methods=['GET', 'POST'])
@login_required
def purchase(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Fetch seat number, price, and other necessary details from the form #maisha
        seat_number = request.form['seat_number']
        price = float(request.form['price'])  # Adjust type conversion as needed

        # Fetch the buyer's wallet and the event creator's wallet 
        buyer_wallet = current_user.wallet
        event_creator_wallet = event.host.wallet

        if buyer_wallet.balance >= price:  # Check if the buyer has enough balance
            # Deduct the ticket price from the buyer's wallet
            buyer_wallet.balance -= price
            # Add the ticket price to the event creator's wallet
            event_creator_wallet.balance += price

            # Create a new ticket and associate it with the user and event
            new_ticket = Ticket(event_id=event_id, user_id=current_user.id, seat_number=seat_number, price=price, purchase_date=datetime.now())
            db.session.add(new_ticket)
            db.session.commit()

            flash('Ticket purchased successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Insufficient balance in your wallet!', 'danger')
            return redirect(url_for('purchase', event_id=event_id))

    # Render a form for selecting seats or buying tickets
    return render_template('purchase.html', event=event)



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
