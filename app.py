from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import timedelta
import mysql.connector
import random

app = Flask(__name__)

# --- SESSION STABILITY CONFIGURATION ---
app.secret_key = 'happy_dental_secure_key_2026' 
app.permanent_session_lifetime = timedelta(minutes=30)

@app.before_request
def make_session_permanent():
    session.permanent = True

# --- MYSQL CONFIGURATION ---
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dental_website',
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**mysql_config)

# --- MAIN NAVIGATION ROUTES ---

@app.route('/')
@app.route('/index')
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments")
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('index.html', data=data)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    doctor_list = [
        {'name': 'Dr. Ishwar Singh', 'qualification': 'BDS, MDS', 'specialization': 'General Dentistry', 'experience': '7 Years', 'image': 'dr-ishwar.jpg'},
        {'name': 'Dr. Kashish', 'qualification': 'BDS (Gold Medalist)', 'specialization': 'Pediatric Dentist', 'experience': '4 Years', 'image': 'dr-kashish.jpg'},
        {'name': 'Dr. Siddhesh', 'qualification': 'MDS - Orthodontics', 'specialization': 'Braces Specialist', 'experience': '6 Years', 'image': 'dr-siddesh.jpg'}
    ]
    return render_template('doctors.html', doctors=doctor_list)

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')

@app.route('/awards')
def awards():
    return render_template('awards.html')

@app.route('/support')
def support():
    return render_template('support.html')

# --- APPOINTMENT BOOKING PROCESS ---

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    doctor = request.form.get('doctor')
    date = request.form.get('date')
    time = request.form.get('time')

    try:
        db = get_db_connection()
        cursor = db.cursor()
        
        # SQL query to insert data
        query = "INSERT INTO appointments (name, email, phone, doctor, date, time) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (name, email, phone, doctor, date, time)
        
        cursor.execute(query, values)
        db.commit()
        
        cursor.close()
        db.close()
        
        return "Appointment Booked Successfully!"
        
    except Exception as e:
        return f"An error occurred: {e}. Check if column 'doctor' exists in your table.", 500

# --- LOGIN & DASHBOARD SYSTEM ---

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login_process', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username and password:
        session['user'] = username
        return redirect(url_for('dashboard'))
    
    return "Invalid Credentials", 401

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', username=session['user'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear() 
    return redirect(url_for('login'))

# --- SPECIALIZED ROUTES ---

@app.route('/view-single/<doctor_name>')
def show_single(doctor_name):
    doctor_list = [
        {'name': 'Dr. Ishwar Singh', 'qualification': 'BDS, MDS', 'specialization': 'General Dentistry', 'experience': '7 Years', 'image': 'dr-ishwar.jpg'},
        {'name': 'Dr. Kashish', 'qualification': 'BDS (Gold Medalist)', 'specialization': 'Pediatric Dentist', 'experience': '4 Years', 'image': 'dr-kashish.jpg'},
        {'name': 'Dr. Siddhesh', 'qualification': 'MDS - Orthodontics', 'specialization': 'Braces Specialist', 'experience': '6 Years', 'image': 'dr-siddesh.jpg'}
    ]
    selected_doctor = next((doc for doc in doctor_list if doc['name'] == doctor_name), None)
    if selected_doctor:
        return render_template("doctor-profile.html", doctor=selected_doctor)
    return "Doctor not found", 404

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower()
    if any(word in user_message for word in ["pain", "hurt", "ache", "swelling"]):
        response = ("Before you reach the clinic: 1. Rinse with warm salt water. "
                    "2. Use a cold compress on the outside of your cheek for 15 mins. "
                    "3. Do not place a crushed tablet on your gums as it causes burns!")
    elif any(word in user_message for word in ["medicine", "tablet", "pill", "paracetamol"]):
        response = ("For pain: You can take Paracetamol or Ibuprofen. "
                    "IMPORTANT: Do not take Antibiotics without a doctor's prescription.")
    elif any(word in user_message for word in ["food", "eat", "drink"]):
        response = ("Stick to soft, cool foods: Curd rice, mashed potatoes, or cold smoothies.")
    elif "fact" in user_message:
        response = "Did you know? If you're right-handed, you tend to chew your food on the right side!"
    else:
        response = "I can help with: Pain relief tips, medicine advice, or diet after surgery."
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)