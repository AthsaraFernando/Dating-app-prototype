import json
import sys
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

print('matchmaking.py Started XXXXX')

# Load MBTI compatibility chart (with all 16 types)
MBTI_COMPATIBILITY = {
    "INTP": {"ENTJ": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ENTP": {"INTP": 90, "ENTJ": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "INFJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "INFP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ENFP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "INTJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ENTJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ISFP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ISTP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ESTP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ESFP": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ENFJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ESTJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ISFJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
    "ESFJ": {"INTP": 90, "ENTP": 85, "INFJ": 80, "INFP": 75, "ENFP": 70, "ISTP": 60, "ISTJ": 55, "ISFP": 50, "ESFP": 40, "ESTP": 35, "ENFJ": 30, "ESTJ": 25, "ISFJ": 20, "ESFJ": 15, "INTJ": 10},
}

# Load user embeddings
with open("user_embeddings.json", "r") as file:
    users = json.load(file)

def filter_users(user, users):
    return [u for u in users if u['gender'] != user['gender'] and abs(u['age'] - user['age']) <= 5]

def calculate_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

def get_match_score(user, other_user):
    mbti_score = MBTI_COMPATIBILITY.get(user['mbti'], {}).get(other_user['mbti'], 0) / 100
    big_five_similarity = calculate_similarity(user['big_five_embedding'], other_user['big_five_embedding'])
    hobbies_similarity = calculate_similarity(user['hobbies_embedding'], other_user['hobbies_embedding'])
    return (mbti_score * 0.2) + (big_five_similarity * 0.4) + (hobbies_similarity * 0.4)

def get_matches(user):
    filtered_users = filter_users(user, users)
    matches = [{'user': u, 'compatibility_score': get_match_score(user, u)} for u in filtered_users]
    return sorted(matches, key=lambda x: x['compatibility_score'], reverse=True)

if __name__ == "__main__":
    # Retrieve the user ID from the command line argument
    user_id = sys.argv[1]
    print(f"Using user ID: {user_id}")  # Print the user ID received from the command line

    user_to_match = next((u for u in users if u['id'] == user_id), None)
    if not user_to_match:
        print(f"User with ID {user_id} not found.")
        sys.exit(1)

    matches = get_matches(user_to_match)
    output_data = {'user_id': user_to_match['id'], 'matches': [{'user_id': m['user']['id'], 'name': m['user']['name'], 'compatibility_score': round(m['compatibility_score'], 2)} for m in matches[:10]]}
    
    try:
        with open("match_scores.json", "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    user_exists = False
    for entry in existing_data:
        if entry['user_id'] == user_to_match['id']:
            entry['matches'] = output_data['matches']
            user_exists = True
            break

    if not user_exists:
        existing_data.append(output_data)

    with open("match_scores.json", "w") as file:
        json.dump(existing_data, file, indent=4)

    print("Match scores have been written to match_scores.json")
