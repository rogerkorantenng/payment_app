from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import googlemaps
from square.client import Client

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Configure SQLAlchemy to use SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Replace with your desired database name
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize Google Maps client
gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')

# Initialize Square client
square_client = Client(
    access_token='YOUR_SQUARE_ACCESS_TOKEN',
    environment='sandbox'  # or 'production' for live mode
)

# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Define Product model (for storing orders)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)

# Define registration and login forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Create the database
db.create_all()

# Routes (Similar to previous responses)

@app.route('/')
def home():
    return "Welcome to the Home Page"

@app.route('/order', methods=['POST'])
@login_required
def order():
    address = request.form['address']
    product_name = request.form['product_name']
    product_price = request.form['product_price']

    geocode_result = gmaps.geocode(address)
    if not geocode_result:
        return "Invalid address"

    location = geocode_result[0]['geometry']['location']
    lat = location['lat']
    lng = location['lng']

    try:
        response = square_client.payments.create_payment(
            source_id='YOUR_SQUARE_CUSTOMER_CARD_ID',
            amount=int(product_price) * 100,
            currency='USD',
            location_id='YOUR_SQUARE_LOCATION_ID',
            autocomplete=True,
            notes=f'Order for {product_name} at {address}',
            customer_id='YOUR_SQUARE_CUSTOMER_ID'
        )

        if response.is_success():
            # Save the order in the database
            order = Product(user_id=current_user.id, address=address, product_name=product_name, product_price=product_price)
            db.session.add(order)
            db.session.commit()
            return "Payment successful! Your order has been placed."
        else:
            return f"Payment failed: {response.errors}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful.', 'success')
            return redirect(url_for('order_page'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/order_page')
@login_required
def order_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
