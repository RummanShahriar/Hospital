from flask import Flask, jsonify, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Mydatabase.db"
db = SQLAlchemy(app)
app.secret_key = 'secret_key'


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


# Doctor/Other model
class Other(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)  # e.g., "doctor"
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    specialization = db.Column(db.String(100), default='')
    experience = db.Column(db.String(100), default='')
    contact = db.Column(db.String(100), default='')
    address = db.Column(db.String(200), default='')
    slots = db.Column(db.String(100), default='')  # New field for slots
    day = db.Column(db.String(50), default='')     # New field for day
    fees = db.Column(db.String(50), default='')    # New field for fees

    def __init__(self, email, password, name, role, specialization='', experience='', contact='', address='', slots='', day='', fees=''):
        self.name = name
        self.role = role
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.specialization = specialization
        self.experience = experience
        self.contact = contact
        self.address = address
        self.slots = slots
        self.day = day
        self.fees = fees

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


# Patient Info model
class PatientInfo(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    address = db.Column(db.String(200))
    district = db.Column(db.String(100))
    post_no = db.Column(db.String(20))
    blood_type = db.Column(db.String(10))
    age = db.Column(db.Integer)
    diabetes = db.Column(db.String(10))

    def __init__(self, email, address='', district='', post_no='', blood_type='', age=None, diabetes=''):
        self.email = email
        self.address = address
        self.district = district
        self.post_no = post_no
        self.blood_type = blood_type
        self.age = age
        self.diabetes = diabetes


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    patient_email = db.Column(db.String(100))  # Patient email
    doc_email = db.Column(db.String(100))      # Doctor email
    date = db.Column(db.Date)                  # Appointment date
    day = db.Column(db.String(50))             # Day of appointment
    slot = db.Column(db.String(50))            # Time slot
    patient_ok = db.Column(db.String(50))         # Patient approval
    doc_ok = db.Column(db.String(50))             # Doctor approval
    payment = db.Column(db.String(50))            # Payment status

    def __init__(self, patient_email, doc_email, date=None, day=None, slot=None, 
                 patient_ok=None, doc_ok=None, payment="False"):
        self.patient_email = patient_email
        self.doc_email = doc_email
        self.date = date
        self.day = day
        self.slot = slot
        self.patient_ok = patient_ok
        self.doc_ok = doc_ok
        self.payment = payment

    def __repr__(self):
        return f"<Appointment {self.id}, Patient: {self.patient_email}, Doctor: {self.doc_email}>"


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    patient_email = db.Column(db.String(100))  # Patient email
    doctor_email = db.Column(db.String(100))  # Doctor email
    prescription_text = db.Column(db.Text, nullable=True)  # Prescription text
    pharmacist_email = db.Column(db.String(100), nullable=True)  # Pharmacist email
    pharmacist_text = db.Column(db.Text, nullable=True)  # Pharmacist's notes
    bill = db.Column(db.Float, nullable=True)  # Bill for the prescription

    def __init__(self, patient_email, doctor_email, prescription_text=None, 
                 pharmacist_email=None, pharmacist_text=None, bill=None):
        self.patient_email = patient_email
        self.doctor_email = doctor_email
        self.prescription_text = prescription_text
        self.pharmacist_email = pharmacist_email
        self.pharmacist_text = pharmacist_text
        self.bill = bill

# Complaint model
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)

    def __init__(self, user_email, category, complaint_text):
        self.user_email = user_email
        self.category = category
        self.complaint_text = complaint_text

# Medicine model
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    name = db.Column(db.String(100), nullable=False)  # Medicine name
    available_dose = db.Column(db.Integer, nullable=False)  # Available dose (quantity)
    price = db.Column(db.Float, nullable=False)  # Price per unit
    side_effect = db.Column(db.Text, nullable=True)  # Side effects (optional)

    def __init__(self, name, available_dose, price, side_effect=None):
        self.name = name
        self.available_dose = available_dose
        self.price = price
        self.side_effect = side_effect


# Initialize the database
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            
            return redirect('/register')

        # Register the new user
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('User has been registered successfully', 'success')
        return redirect('/login')

    return render_template('register.html')


@app.route('/other_register', methods=['GET', 'POST'])
def other_register():
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        if Other.query.filter_by(email=email).first():
            return redirect('/other_register')

        # Register the new user
        new_user = Other(name=name, email=email, password=password,role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/admin_M')

    return render_template('other_register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if (user and user.check_password(password)) and (email == user.email) and (name == user.name):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again or register.', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/other_login', methods=['GET', 'POST'])
def other_login():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = Other.query.filter_by(email=email).first()
        if (user and user.check_password(password)) and (email == user.email) and (name == user.name):
            session['email'] = user.email

            ###### Now only for doctor -->> further Admin and Pharmacist
            if (user.role == 'doctor') :
                return redirect('/doc_dash')
            elif (user.role == 'admin') :
                return redirect('/admin_M')
            elif (user.role == 'pharmacist') :
                return redirect('/pharmacist_dash')
            
        else:
            
            return redirect('/other_login')

    return render_template('other_login.html')



@app.route('/dashboard', endpoint='user_dashboard')
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)
    return redirect('/login')

@app.route('/doc_dash', endpoint='doctor_dashboard')
def doc_dash():
    if 'email' in session:
        user = Other.query.filter_by(email=session['email']).first()
        return render_template('doc_dash.html', user=user)
    return redirect('/other_login')


@app.route('/doc_prescription')
def doc_prescription():
    if 'email' in session:
        user = Other.query.filter_by(email=session['email']).first()
        return render_template('doc_prescription.html', user=user)
    return redirect('/other_login')


@app.route('/prescription')
def prescription():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user:
            prescriptions = Prescription.query.filter_by(patient_email=user.email).all()
            return render_template('prescription.html', user=user, prescriptions=prescriptions)
    return redirect('/login')

@app.route('/doc_prescription_form', methods=['GET', 'POST'])
def doc_prescription_form():
    if 'email' not in session:
        return redirect('/other_login')

    doctor_email = session['email']

    if request.method == 'GET':
        # Fetch eligible patient emails
        appointments = Appointment.query.filter_by(doc_email=doctor_email).filter(Appointment.payment != "False").all()
        patient_emails = {appointment.patient_email for appointment in appointments}  # Use a set to avoid duplicates
        
        # Render the form with the patient emails
        return render_template('doc_prescription_form.html', patient_emails=patient_emails)

    elif request.method == 'POST':
        patient_email = request.form['patient_email']
        prescription_text = request.form['prescription_text']
        pharmacist_text = request.form['pharmacist_text']  # Capture the date input

        # Add prescription
        new_prescription = Prescription(
            patient_email=patient_email,
            doctor_email=doctor_email,
            prescription_text=prescription_text,
            pharmacist_text=pharmacist_text  # Save the date to the database
        )
        db.session.add(new_prescription)
        db.session.commit()

        return redirect('/doc_prescription')

    # Redirect if session is invalid
    return redirect('/other_login')


@app.route('/pharmacist_dash', endpoint='pharmacist_dashboard')
def pharmacist_dash():
    if 'email' in session:
        user = Other.query.filter_by(email=session['email']).first()
        return render_template('pharmacist_dash.html', user=user)
    return redirect('/other_login')


@app.route('/store')
def store():
    if 'email' in session:
        medicines = Medicine.query.all()
        return render_template('store.html', medicines=medicines)
    return redirect('/other_login')

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        name = request.form['name']
        available_dose = request.form['available_dose']
        price = request.form['price']
        side_effect = request.form.get('side_effect')

        new_medicine = Medicine(name=name, available_dose=available_dose, price=price, side_effect=side_effect)
        db.session.add(new_medicine)
        db.session.commit()

        return redirect('/store')

    return render_template('add_medicine.html')  


@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)

    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.available_dose = request.form['available_dose']
        medicine.price = request.form['price']
        medicine.side_effect = request.form.get('side_effect')

        db.session.commit()
        return redirect('/store')

    return render_template('edit_medicine.html', medicine=medicine)  # Create this template for editing.

@app.route('/delete_medicine/<int:id>', methods=['GET', 'POST'])
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    return redirect('/store')


@app.route('/prescribe', methods=['GET', 'POST'])
def prescribe():
    if 'email' not in session:
        return redirect('/other_login')

    user = Other.query.filter_by(email=session['email']).first()
    prescriptions = []

    if request.method == 'POST':
        patient_email = request.form['patient_email']
        # Query the Prescription table for the given patient email
        prescriptions = Prescription.query.filter_by(patient_email=patient_email).all()

    return render_template('prescribe.html', user=user, prescriptions=prescriptions)


@app.route('/admin_M')
def admin_M():
    if 'email' in session:
        user = Other.query.filter_by(email=session['email']).first()
        others = Other.query.all()  # Fetch all doctors and pharmacists
        return render_template('admin_M.html', user=user, others=others)
    return redirect('/other_login')

@app.route('/admin_F')
def admin_F():
    if 'email' in session:
        user = Other.query.filter_by(email=session['email']).first()
        complaints = Complaint.query.all()  # Fetch all complaints
        return render_template('admin_F.html', user=user, complaints=complaints)
    return redirect('/other_login')

@app.route('/delete_complaint/<int:id>', methods=['POST'])
def delete_complaint(id):
    if 'email' in session:
        complaint = Complaint.query.get_or_404(id)
        db.session.delete(complaint)
        db.session.commit()
        flash('Complaint deleted successfully.', 'success')
        return redirect('/admin_F')
    return redirect('/other_login')


@app.route('/edit_other/<int:id>', methods=['GET', 'POST'])
def edit_other(id):
    other = Other.query.get_or_404(id)
    if request.method == 'POST':
        other.name = request.form['name']
        other.role = request.form['role']
        other.specialization = request.form['specialization']
        other.experience = request.form['experience']
        other.contact = request.form['contact']
        other.address = request.form['address']
        db.session.commit()
        return redirect('/admin_M')
    return render_template('edit_other.html', other=other)


@app.route('/delete_other/<int:id>')
def delete_other(id):
    other = Other.query.get_or_404(id)
    db.session.delete(other)
    db.session.commit()
    return redirect('/admin_M')

@app.route('/help')
def help():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('help.html', user=user)
    return redirect('/login')


@app.route('/payment')
def payment():
    if 'email' in session:
        user_email = session['email']
        appointments = Appointment.query.filter_by(patient_email=user_email).all()
        return render_template('payment.html', appointments=appointments)
    return redirect('/login')

@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()

    return redirect('/payment')

@app.route('/accept_appointment_user/<int:id>', methods=['POST'])
def accept_appointment_user(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.patient_ok = "Yes"
    db.session.commit()

    return redirect('/payment')

@app.route('/pay_now/<int:id>', methods=['GET', 'POST'])
def pay_now(id):
    
    if request.method == 'GET':
        return render_template('payment_form.html', appointment_id=id)
    elif request.method == 'POST':
        appointment = Appointment.query.get_or_404(id)
        payment_method = request.form['payment_method']
        appointment.payment = payment_method
        db.session.commit()

        return redirect('/payment')



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' not in session:
        return redirect('/login')

    user_email = session['email']
    user = User.query.filter_by(email=user_email).first()

    # Fetch the patient's additional info
    patient_info = PatientInfo.query.filter_by(email=user_email).first()

    if request.method == 'POST':
        # Get form data
        address = request.form.get('address', '')
        district = request.form.get('district', '')
        post_no = request.form.get('post_no', '')
        blood_type = request.form.get('blood_type', '')
        age = request.form.get('age', None)
        diabetes = request.form.get('diabetes', '')

        # Convert age to integer if provided
        age = int(age) if age else None

        # Update or insert patient info
        if patient_info:
            patient_info.address = address
            patient_info.district = district
            patient_info.post_no = post_no
            patient_info.blood_type = blood_type
            patient_info.age = age
            patient_info.diabetes = diabetes
        else:
            patient_info = PatientInfo(
                email=user_email,
                address=address,
                district=district,
                post_no=post_no,
                blood_type=blood_type,
                age=age,
                diabetes=diabetes
            )
            db.session.add(patient_info)

        db.session.commit()
        return redirect('/profile')

    return render_template('profile.html', user=user, patient_info=patient_info)

@app.route('/doc_profile', methods=['GET', 'POST'])
def doc_profile():
    if 'email' not in session:
        return redirect('/other_login')

    doctor_email = session['email']
    doctor = Other.query.filter_by(email=doctor_email).first()

    if request.method == 'POST':
        # Get form data
        specialization = request.form.get('specialization', '')
        experience = request.form.get('experience', '')
        contact = request.form.get('contact', '')
        address = request.form.get('address', '')
        slots = request.form.get('slots', '')
        day = request.form.get('day', '')
        fees = request.form.get('fees', '')

        # Update doctor profile fields
        doctor.specialization = specialization
        doctor.experience = experience
        doctor.contact = contact
        doctor.address = address
        doctor.slots = slots
        doctor.day = day
        doctor.fees = fees

        db.session.commit()

        return redirect('/doc_profile')

    return render_template('doc_profile.html', doctor=doctor)



@app.route('/appointment')
def appointment():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        doctors = Other.query.filter_by(role='doctor').all()  # Fetch all doctors with the role 'doctor'
        return render_template('appointment.html', doctors=doctors, user=user)
    return redirect('/other_login')

@app.route('/reschedule_appointment/<int:id>', methods=['GET', 'POST'])
def reschedule_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    if request.method == 'POST':
        new_date = request.form['new_date']
        new_day = request.form['new_day']
        new_slot = request.form['new_slot']

        # Update the appointment with new details
        appointment.date = datetime.strptime(new_date, '%Y-%m-%d').date()
        appointment.day = new_day
        appointment.slot = new_slot
        db.session.commit()
        
        flash('Appointment rescheduled successfully.', 'success')
        return redirect('/doc_appointment')
    
    return render_template('reschedule_appointment.html', appointment=appointment)

@app.route('/accept_appointment/<int:id>', methods=['POST'])
def accept_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.doc_ok = "Yes"  # Mark the doctor's approval
    db.session.commit()
    
    flash('Appointment accepted.', 'success')
    return redirect('/doc_appointment')


@app.route('/doc_appointment')
def doc_appointment():
    if 'email' in session:  # Check if the doctor is logged in
        doctor_email = session['email']  # Get the logged-in doctor's email
        # Filter appointments for the doctor where doc_ok is not 'Yes'
        appointments = Appointment.query.filter(Appointment.doc_email == doctor_email, Appointment.doc_ok == None).all()
        return render_template('doc_appointment.html', appointments=appointments)  # Pass data to template
    else:
        return redirect('/other_login')


from datetime import datetime

@app.route('/appointment_form', methods=['GET', 'POST'])
def appointment_form():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        doctors = Other.query.filter_by(role='doctor').all()  # Fetch all doctors
        
        if request.method == 'POST':
            user_email = user.email
            doc_email = request.form['doc_email']
            appointment_date = request.form['appointment_date']
            day = request.form['day']
            appointment_time = request.form['appointment_time']

            # Convert the appointment_date string to a datetime.date object
            try:
                appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            except ValueError:
                
                return redirect('/appointment_form')

            # Create a new appointment record
            new_appointment = Appointment(
                patient_email=user_email,
                doc_email=doc_email,
                date=appointment_date_obj,
                day=day,
                slot=appointment_time,
            )

            db.session.add(new_appointment)
            db.session.commit()
            flash('Appointment booked successfully!', 'success')
            return redirect('/appointment')

        return render_template('appointment_form.html', user=user, doctors=doctors)

    return redirect('/login')


@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    if 'email' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        user_email = session['email']
        category = request.form['complaintType']  # Match the name attribute in the form
        complaint_text = request.form['details']  # Match the textarea name in the form

        # Save complaint to database
        new_complaint = Complaint(user_email=user_email, category=category, complaint_text=complaint_text)
        db.session.add(new_complaint)
        db.session.commit()

        return redirect('/help')


@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Logged out successfully', 'success')
    return redirect('/login')


@app.route('/other_logout')
def other_logout():
    session.pop('email', None)
    flash('Logged out successfully', 'success')
    return redirect('/other_login')


if __name__ == '__main__':
    app.run(debug=True)
