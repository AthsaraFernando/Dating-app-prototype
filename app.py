from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

# Path to the JSON file
USER_DATA_FILE = 'fake_user_data.json'

# Function to load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return []

# Function to save user data
def save_user_data(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Route for the Home page (initial page)
@app.route('/')
def home():
    return render_template('home.html')

# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')

        # Load users data from the JSON file
        users = load_user_data()

        # Check if user exists
        for user in users:
            if user['id'] == user_id:
                # If login is successful, redirect to a test page (or another page)
                return redirect(url_for('test'))

        # If login fails, show a flash message
        flash('Invalid user ID', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

# Route for a simple test page after login
@app.route('/test')
def test():
    return "Login Successful! This is a test page."

# Route for the sign-up page
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form.get('user_id')

        # Load existing users data
        users = load_user_data()

        # Check if user already exists
        if any(user['id'] == user_id for user in users):
            flash('User ID already exists!', 'error')
            return redirect(url_for('sign_up'))

        # Add new user (using user_id as both the username and password)
        users.append({"id": user_id, "password": user_id})

        # Save updated user data
        save_user_data(users)

        flash('User created successfully!', 'success')

        # Redirect to the form page to complete the profile
        return redirect(url_for('form', user_id=user_id))

    return render_template('sign_up.html')

# Route for the profile form page
@app.route('/form/<user_id>', methods=['GET', 'POST'])
def form(user_id):
    if request.method == 'POST':
        # Gather user profile data from the form
        user_data = {
            "id": user_id,
            "name": request.form.get('name'),
            "age": request.form.get('age'),
            "gender": request.form.get('gender'),
            "city": request.form.get('city'),
            "mbti": request.form.get('mbti'),
            "big_five": {
                "Openness": float(request.form.get('openness')),
                "Conscientiousness": float(request.form.get('conscientiousness')),
                "Extraversion": float(request.form.get('extraversion')),
                "Agreeableness": float(request.form.get('agreeableness')),
                "Neuroticism": float(request.form.get('neuroticism')),
            },
            "hobbies": request.form.getlist('hobbies')
        }

        # Update the user data in the JSON file
        users = load_user_data()
        for user in users:
            if user['id'] == user_id:
                user.update(user_data)
                break
        
        save_user_data(users)

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('form.html', user_id=user_id)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
