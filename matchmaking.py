import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

# Filter users by gender and age gap
def filter_users(user, users):
    filtered_users = []
    for other_user in users:
        # Gender filter: opposite sex
        if other_user['gender'] != user['gender']:
            # Age filter: age gap of +/- 5 years
            if abs(other_user['age'] - user['age']) <= 5:
                filtered_users.append(other_user)
    return filtered_users

# Calculate cosine similarity between embeddings
def calculate_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

# Generate compatibility scores between users
def get_match_score(user, other_user):
    # Calculate MBTI compatibility score
    mbti_score = MBTI_COMPATIBILITY.get(user['mbti'], {}).get(other_user['mbti'], 0)
    normalized_mbt_score = mbti_score / 100  # Normalize to 0-1 range
    
    # Calculate similarity for Big Five traits
    big_five_similarity = calculate_similarity(user['big_five_embedding'], other_user['big_five_embedding'])
    
    # Calculate similarity for hobbies
    hobbies_similarity = calculate_similarity(user['hobbies_embedding'], other_user['hobbies_embedding'])
    
    # Combine all the scores (adjusted for scale)
    total_score = (normalized_mbt_score * 0.2) + (big_five_similarity * 0.4) + (hobbies_similarity * 0.4)
    
    return total_score




# Matchmaking logic
def get_matches(user):
    # Apply gender and age filtering
    filtered_users = filter_users(user, users)
    
    # Calculate match scores for filtered users
    matches = []
    for other_user in filtered_users:
        score = get_match_score(user, other_user)
        matches.append({
            'user': other_user,
            'compatibility_score': score
        })
    
    # Sort by compatibility score
    matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
    
    return matches

# Example: Get matches for a specific user (user_0)
user_to_match = users[0]  # Replace with the user you're interested in
matches = get_matches(user_to_match)

# Display the top matches with user ID
for match in matches[:20]:  # Top 5 matches
    print(f"User ID: {match['user']['id']}, Match: {match['user']['name']}, Compatibility Score: {match['compatibility_score']:.2f}")
