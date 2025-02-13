from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import subprocess
from openai import OpenAI


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

# Chat Page (Displays the chat UI)
@app.route('/chat/<user_id>')
def chat(user_id):
    # Load accepted/rejected data
    accepted_rejected = load_json(ACCEPTED_REJECTED_FILE, {})
    user_choices = accepted_rejected.get(user_id, {"accepted": []})
    accepted_user_ids = user_choices["accepted"]

    # Retrieve user data for accepted matches
    users = load_json(USER_DATA_FILE, [])
    contacts = [user for user in users if user["id"] in accepted_user_ids]

    return render_template('chat.html', user_id=user_id, contacts=contacts)


# Path to chat messages file
CHAT_MESSAGES_FILE = 'messages.json'

# Function to load chat messages
def load_chat_messages():
    return load_json(CHAT_MESSAGES_FILE, {})

# Function to save chat messages
def save_chat_messages(messages):
    save_json(CHAT_MESSAGES_FILE, messages)

# Chat Messages Route (Get Messages for a Conversation)
@app.route('/chat/messages/<user_id>/<contact_id>', methods=['GET'])
def get_chat_messages(user_id, contact_id):
    messages = load_chat_messages()

    # Get the conversation between user and contact
    chat_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
    chat = messages.get(chat_id, [])

    return jsonify({"status": "success", "messages": chat})

# Send Message Route (Post New Message)
@app.route('/chat/send', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    message = data.get("message")

    if not sender_id or not receiver_id or not message:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    messages = load_chat_messages()

    # Create a unique chat_id based on sender and receiver
    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

    # Add the message to the chat
    if chat_id not in messages:
        messages[chat_id] = []

    messages[chat_id].append({"sender_id": sender_id, "receiver_id": receiver_id, "message": message, "timestamp": "2025-02-12T12:00:00"})  # Add timestamp for better tracking

    save_chat_messages(messages)

    return jsonify({"status": "success", "message": "Message sent."})


# Initialize the DeepSeek API client using the API key from the .env file
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

@app.route('/chat/ai-suggestions/<user_id>/<contact_id>', methods=['GET'])
def ai_suggestions(user_id, contact_id):
    # Fetch previous messages between user and contact
    messages = load_chat_messages()
    chat_id = f"{min(user_id, contact_id)}_{max(user_id, contact_id)}"
    chat = messages.get(chat_id, [])

    # Generate the conversation context from the last few messages
    context = "\n".join([message["message"] for message in chat[-5:]])  # Use the last 5 messages

    # Make the API call to generate suggestions
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Give a practical conversation starter or a pick up line in a dating app when talk to a person who like reading books, keep it very short and sweet and flirty ."},
            ],
            stream=False
        )
        suggestions = response.choices[0].message.content.split('\n')  # Assuming the response is a list of suggestions

        return jsonify({"status": "success", "suggestions": suggestions})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

if __name__ == '__main__':
    app.run(debug=True)
