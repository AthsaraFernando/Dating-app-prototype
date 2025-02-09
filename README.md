# Dating App Prototype

## Description

The Dating App Prototype is a proof-of-concept matchmaking system that uses personality traits and embeddings to find compatible matches. The system relies on MBTI personality types, Big Five personality traits, and vector embeddings to calculate match scores between users. The prototype is built with Flask and integrates simple authentication, data storage, and matchmaking functionality.

## Matching Algorithm and Weights

The matchmaking system uses the following weighted criteria to calculate compatibility:

- **MBTI Compatibility (40%)**: Uses a predefined compatibility chart for all 16 MBTI types.
- **Big Five Personality Traits (30%)**: Calculates similarity using Euclidean distance between users' Big Five traits.
- **Vector Embeddings (20%)**: Uses cosine similarity between user embeddings generated from provided data.
- **Hobbies and Interests (10%)**: Matches users based on common hobbies.

## Overview

This prototype is a minimal implementation designed for testing and development. The app allows users to sign up, input personality traits, and check their match scores with other users. The backend is implemented using Flask, and data is stored in JSON files.

## File Structure

```
/Dating-app-prototype
  ├── app.py
  ├── venv
  ├── .env
  ├── .gitignore
  ├── generate_embeddings.py
  ├── generate_fake_data.py
  ├── match_scores.json
  ├── matchmaking.py
  ├── requirements.txt
  ├── user_embeddings.json
  ├── fake_user_data.json
  └── templates/
      ├── home.html
      ├── login.html
      ├── sign_up.html
      ├── form.html
      ├── profile.html
      └── test.html
```

## File Descriptions

- **`app.py`** - The main Flask application that handles user authentication, form submissions, and rendering templates.
- **`generate_embeddings.py`** - Generates vector embeddings for users based on their personality traits.
- **`generate_fake_data.py`** - Creates a set of fake user profiles for testing purposes.
- **`matchmaking.py`** - Runs the matchmaking algorithm, calculating match scores based on MBTI, Big Five traits, and vector similarity.
- **`match_scores.json`** - Stores the match scores for each user after running the matchmaking script.
- **`user_embeddings.json`** - Stores the embeddings for each user, which are used for similarity calculations.
- **`fake_user_data.json`** - Stores user profiles, including personality traits and preferences.
- **`templates/`** - Contains HTML templates for the frontend.
  - `home.html` - Main landing page.
  - `login.html` - User login page.
  - `sign_up.html` - User registration page.
  - `form.html` - Profile update form.
  - `profile.html` - Displays user profile.
  - `test.html` - Displays match results.

## Setup and Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/Dating-app-prototype.git
   cd Dating-app-prototype
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the Flask application:
   ```sh
   python app.py
   ```
5. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   ```

## Running the Matchmaking Process

1. Create user embeddings:
   ```sh
   python generate_embeddings.py
   ```
2. Run the matchmaking script:
   ```sh
   python matchmaking.py user_0  # Replace `user_0` with the actual user ID
   ```
3. View the matches in `test.html`.

## Security Concerns

- **No password hashing**: User IDs are used as passwords, which is insecure for real-world applications.
- **No database**: All data is stored in JSON files, which can be easily modified.
- **No user session management**: Users are not properly authenticated beyond checking IDs.
- **Vulnerable to data corruption**: No error handling for file modifications.

## Future Improvements

- Implement proper authentication with hashed passwords.
- Replace JSON storage with a database (e.g., PostgreSQL, MongoDB).
- Improve the matchmaking algorithm using more robust ML techniques.
- Enhance frontend UI for better user experience.

This project is for **testing purposes only** and is not intended for production use.
