from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # For flash messages

# Paths to JSON files
USER_DATA_FILE = 'fake_user_data.json'
MATCH_SCORES_FILE = 'match_scores.json'
USER_EMBEDDINGS_FILE = 'user_embeddings.json'

# Function to save user data
def save_user_data(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Function to load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return []


# Function to load match scores
def load_match_scores():
    if os.path.exists(MATCH_SCORES_FILE):
        with open(MATCH_SCORES_FILE, 'r') as file:
            try:
                data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                data = []
        return data
    return []  # Return an empty list if file doesn't exist


# Function to save match scores
def save_match_scores(scores):
    with open(MATCH_SCORES_FILE, 'w') as file:
        json.dump(scores, file, indent=4)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        users = load_user_data()
        if any(user['id'] == user_id for user in users):
            return redirect(url_for('test', user_id=user_id))
        flash('Invalid user ID', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

# Test Page (Displays Matches)
@app.route('/test/<user_id>')
def test(user_id):
    match_scores = load_match_scores()
    user_matches = []
    
    # Find the user in the match_scores list
    for entry in match_scores:
        if entry['user_id'] == user_id:
            user_matches = entry.get('matches', [])
            break

    return render_template('test.html', user_id=user_id, matches=user_matches)

# Run Matching Script (Triggered on "Check Matches")
@app.route('/run-matching/<user_id>', methods=['POST'])
def run_matching(user_id):
    # Load existing match scores (or create the file if it doesn't exist)
    match_scores = load_match_scores()

    # Run the embedding generation and matchmaking scripts
    embedding_result = subprocess.run(["python", "generate_embeddings.py"], capture_output=True, text=True)

    # Pass user_id to matchmaking.py
    matching_result = subprocess.run(["python", "matchmaking.py", user_id], capture_output=True, text=True)

    print("Embedding Script Output:", embedding_result.stdout)
    print("Matching Script Output:", matching_result.stdout)

    if embedding_result.returncode != 0 or matching_result.returncode != 0:
        return jsonify({"status": "error", "message": "Error running scripts"})

    # Reload the match scores after the scripts have run
    match_scores = load_match_scores()

    # Update or create the match entry for the user
    user_matches = [
        {"user_id": "user_11", "name": "Alex", "compatibility_score": 0.88},
        {"user_id": "user_2", "name": "Peyton", "compatibility_score": 0.83},
        {"user_id": "user_8", "name": "Casey", "compatibility_score": 0.82},
        {"user_id": "user_4", "name": "Jamie", "compatibility_score": 0.8}
    ]  # Replace this with actual match data

    # Check if the user already exists in the match_scores list
    user_found = False
    for entry in match_scores:
        if entry['user_id'] == user_id:
            entry['matches'] = user_matches
            user_found = True
            break

    # If the user is not found, add a new entry
    if not user_found:
        match_scores.append({"user_id": user_id, "matches": user_matches})

    # Save the updated match scores
    save_match_scores(match_scores)

    return jsonify({"status": "done", "matches": user_matches})

# Sign-Up Page
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        users = load_user_data()
        if any(user['id'] == user_id for user in users):
            flash('User ID already exists!', 'error')
            return redirect(url_for('sign_up'))

        users.append({"id": user_id, "password": user_id})
        save_user_data(users)
        flash('User created successfully!', 'success')
        return redirect(url_for('form', user_id=user_id))
    
    return render_template('sign_up.html')

# Profile Form Page
@app.route('/form/<user_id>', methods=['GET', 'POST'])
def form(user_id):
    if request.method == 'POST':
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

        users = load_user_data()
        for user in users:
            if user['id'] == user_id:
                user.update(user_data)
                break
        
        save_user_data(users)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('form.html', user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
