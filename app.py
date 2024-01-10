# app.py
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import joblib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crime_data.db'
db = SQLAlchemy(app)
api = Api(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Define the CrimeData model for the database
class CrimeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    crime_rate = db.Column(db.Float, nullable=False)
    # ... (other columns)

# Define the User model for user authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Flask-RESTful API Resource for crime data
class CrimeDataResource(Resource):
    def get(self, country, state, province):
        data = CrimeData.query.filter_by(country=country, state=state, province=province).first()
        if data:
            return {
                'country': data.country,
                'state': data.state,
                'province': data.province,
                'crime_rate': data.crime_rate
            }
        else:
            return {'message': 'Data not found'}, 404

api.add_resource(CrimeDataResource, '/api/crime_data/<string:country>/<string:state>/<string:province>')

# ... (other routes and configurations)

# Route for rendering the prediction form
@app.route('/predict', methods=['GET'])
@login_required
def render_predict_form():
    return render_template('predict.html')

# Route for handling the prediction form submission
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    # Get input data from the frontend
    country = request.form.get('country')
    state = request.form.get('state')
    province = request.form.get('province')

    # Use the input data to fetch corresponding features from your database
    data = CrimeData.query.filter_by(country=country, state=state, province=province).first()

    if data:
        # Fetch crime rate feature from the database
        crime_rate_feature = data.crime_rate

        # Use the machine learning model to predict crime rate
        model = joblib.load('your_model_path.joblib')  # Load your trained model
        features = [[crime_rate_feature]]  # Replace with actual features
        prediction = model.predict(features)[0]

        # Render the result template with the prediction
        return render_template('result.html', prediction=prediction)
    else:
        # Render an error message if data is not found
        flash('Data not found. Please check your input.', 'error')
        return redirect(url_for('render_predict_form'))

# ... (other routes and configurations)

# Navigation Bar (Navbar)
@app.route('/navbar')
@login_required
def navbar():
    return render_template('navbar.html', username=current_user.username)

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully'

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
