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
USER_CHOICES_FILE = 'user_choices.json'
ACCEPTED_REJECTED_FILE = 'accepted_rejected.json'

# Function to load JSON data
def load_json(file_path, default={}):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return default
    return default

# Function to save JSON data
def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        users = load_json(USER_DATA_FILE, [])
        if any(user['id'] == user_id for user in users):
            return redirect(url_for('test', user_id=user_id))
        flash('Invalid user ID', 'error')
        return redirect(url_for('login'))
    return render_template('login.html')

# Test Page (Displays Matches)
@app.route('/test/<user_id>')
def test(user_id):
    match_scores = load_json(MATCH_SCORES_FILE, [])
    user_matches = next((entry['matches'] for entry in match_scores if entry['user_id'] == user_id), [])
    user_choices = load_json(ACCEPTED_REJECTED_FILE, {}).get(user_id, {"accepted": [], "rejected": []})
    accepted_user_ids = user_choices["accepted"]
    rejected_user_ids = user_choices["rejected"]
    return render_template('test.html', user_id=user_id, matches=user_matches, accepted_user_ids=accepted_user_ids, rejected_user_ids=rejected_user_ids)


# Accept or Reject Matches
@app.route('/accept_reject', methods=['POST'])
def accept_reject():
    data = request.get_json()
    print("Received data:", data)  # Debugging: Check what data is coming in

    user_id = data.get("user_id")
    match_id = data.get("match_id")
    choice = data.get("choice")

    if not user_id or not match_id or not choice:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    # Load previous accept/reject data
    accepted_rejected_file = 'accepted_rejected.json'
    choices = load_json(accepted_rejected_file, {})

    # Ensure the user_id exists in the JSON structure
    if user_id not in choices:
        choices[user_id] = {"accepted": [], "rejected": []}

    # Store the match_id in the correct list
    if choice == "accept" and match_id not in choices[user_id]["accepted"]:
        choices[user_id]["accepted"].append(match_id)
    elif choice == "reject" and match_id not in choices[user_id]["rejected"]:
        choices[user_id]["rejected"].append(match_id)

    # Save the updated choices
    save_json(accepted_rejected_file, choices)

    return jsonify({"status": "success", "message": f"Choice '{choice}' saved for match '{match_id}'."})


# Run Matching Script (Triggered on "Check Matches")
@app.route('/run-matching/<user_id>', methods=['POST'])
def run_matching(user_id):
    embedding_result = subprocess.run(["python", "generate_embeddings.py"], capture_output=True, text=True)
    matching_result = subprocess.run(["python", "matchmaking.py", user_id], capture_output=True, text=True)

    if embedding_result.returncode != 0 or matching_result.returncode != 0:
        return jsonify({"status": "error", "message": "Error running scripts"})

    match_scores = load_json(MATCH_SCORES_FILE, [])
    user_matches = next((entry["matches"] for entry in match_scores if entry["user_id"] == user_id), [])
    return jsonify({"status": "done", "matches": user_matches})


# Sign-Up Page
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        users = load_json(USER_DATA_FILE, [])
        if any(user['id'] == user_id for user in users):
            flash('User ID already exists!', 'error')
            return redirect(url_for('sign_up'))

        users.append({"id": user_id})
        save_json(USER_DATA_FILE, users)
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
            "age": int(request.form.get('age')),
            "gender": request.form.get('gender'),
            "location": request.form.get('location'),
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

        users = load_json(USER_DATA_FILE, [])
        for user in users:
            if user['id'] == user_id:
                user.update(user_data)
                break
        
        save_json(USER_DATA_FILE, users)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('form.html', user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
