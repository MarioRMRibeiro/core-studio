# routes.py
from flask import Blueprint, jsonify, request, redirect, url_for, flash
from flask_httpauth import HTTPBasicAuth
from backend.models import db, User, Appointment, Session, Booking  # Import your models
from werkzeug.security import generate_password_hash, check_password_hash
from backend.schemas import UserSchema, AppointmentSchema
from flask import render_template
from flask_login import login_user, login_required, logout_user, current_user, login_manager

# Create a blueprint for routes
main = Blueprint('main', __name__)

# Initialize HTTPBasicAuth
auth = HTTPBasicAuth()

# Dummy user data for authentication (as you mentioned)
users = {
    "admin": generate_password_hash("password123")
}

user_schema = UserSchema()  # for single user operations
users_schema = UserSchema(many=True)  # for multiple users
appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)
# Home route


@main.route('/', methods=['GET', 'POST'])
def home():
    next_page = request.args.get('next')  # Capture the next page
    print(f"Next page: {next_page}")
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user:
            print(f"User found: {user.username}")
        else:
            print("No user found with that username")

        if user and check_password_hash(user.password, password):
            print("Password matched")
            login_user(user, remember=True)  # Log in with remember=True
            
            print(f"Logged in user: {current_user.username}")  # Debugging current_user after login
            
            # Redirect to the original destination or admin dashboard
            return redirect(next_page or (url_for('main.admin_dashboard') if user.role == 'admin' else url_for('main.book_session')))
        else:
            flash('Invalid username or password')
    return render_template('core.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

##@main.route('/create-admin', methods=['GET'])
##def create_admin():
    # Add the admin user (only run this once)
    #admin_user = User(username='mario', email='mario@example.com', password=generate_password_hash('password123'), role='admin')
    #db.session.add(admin_user)
    #db.session.commit()
    #return "Admin user created!"
    
    
# Route to get all users
@main.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username} for user in users])

# Route to add a new user
@main.route('/add_user', methods=['POST'])
@auth.login_required  # Add this line to require authentication
def add_user():  
    try:
        data = request.get_json()
        # Validate the data using the schema
        errors = user_schema.validate(data)
        if errors:
            return jsonify(errors), 400  # Return errors if validation fails
        new_user = User(
                username=data['username'], 
                email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User added successfully"}), 201
    except Exception as e:
        # If an unexpected error occurs, return 500 Internal Server Error
        return jsonify({"error": str(e)}), 500
        
@main.route('/user/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return user_schema.jsonify(user)   
 
@main.route('/schedule', methods=['POST'])
def schedule_appointment():
    name = request.json.get('name')
    date = request.json.get('date')
    time = request.json.get('time')
    tipo = request.json.get('tipo')
    
    # Validate the input
    if not name or not date or not time:
        return jsonify({"error": "Please provide name, date, time and tipo."}), 400

    # Create a new appointment
    new_appointment = Appointment(name=name, date=date, time=time, tipo=tipo)
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"message": "Appointment scheduled successfully!"}), 201
 
# Authentication handler
@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None
    
    
@main.route('/sessions', methods=['GET'])
@login_required
def view_sessions():
    sessions = PTSession.query.filter(PTSession.spots_available > 0).all()
    return render_template('view_sessions.html', sessions=sessions)


# Schedule appointment page
@main.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        # Capture and process form data (already implemented)
        return redirect('/')
    return render_template('schedule.html')

@main.route('/admin/create_session', methods=['GET', 'POST'])
@login_required
def create_session():
    if request.method == 'POST':
        day = request.form['day']
        time = request.form['time']
        spots = request.form['spots']
        
        new_session = Session(day=day, time=time, spots=spots)
        db.session.add(new_session)
        db.session.commit()
        flash('Session created successfully!')
    
    sessions = Session.query.all()
    return render_template('manage_sessions.html', sessions=sessions)
    
@main.route('/admin/edit_session/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_session(id):
    session = PTSession.query.get_or_404(id)
    if request.method == 'POST':
        session.date = request.form.get('date')
        session.time = request.form.get('time')
        session.spots_available = request.form.get('spots')
        db.session.commit()
        flash('Session updated successfully!')
        return redirect(url_for('main.admin_dashboard'))
        
@main.route('/admin/delete_session/<int:id>', methods=['POST'])
@auth.login_required
def delete_session(id):
    session = Session.query.get(id)
    if session:
        db.session.delete(session)
        db.session.commit()
        flash('Session deleted successfully!')
    return redirect(url_for('main.manage_sessions'))
    
@main.route('/sessions')
@login_required
def user_sessions():
    sessions = PTSession.query.all()  # Assuming PTSession is the model for sessions
    return render_template('sessions.html', sessions=sessions)

@main.route('/book_session', methods=['GET', 'POST'])
@auth.login_required
def book_session():
    if session.get('role') == 'admin':
        flash('Admins cannot book sessions.')
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        session_id = request.form['session_id']
        user_id = session['user_id']

        appointment = Appointment(user_id=user_id, session_id=session_id)
        db.session.add(appointment)
        db.session.commit()

        flash('You have successfully booked a session!')
        return redirect(url_for('book_session'))

    sessions = Session.query.filter(Session.available_spots > 0).all()
    return render_template('book_session.html', sessions=sessions)


@main.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("You do not have access to this page.")
        return redirect(url_for('main.home'))
    return render_template('admin_dashboard.html')  # Adjust the template name as needed


    
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists, please choose another one.')
            return render_template('register.html', error="Username already exists.")

        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email or log in.')
            return render_template('register.html', error="Email already registered.")

        # Password validation (length check)
        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return render_template('register.html', error="Password too short.")

        # Hash the password and create the new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        # Save to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('main.home'))

    return render_template('register.html')