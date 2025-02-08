import random
import json

# Define possible values
names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Peyton", "Quinn"]
locations = ["New York", "Los Angeles", "London", "Berlin", "Tokyo"]
mbti_types = ["INTP", "ENTP", "INFJ", "ENFJ", "ISTJ", "ESTJ", "ISFP", "ESFP"]
big_five_traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
hobbies = ["Reading", "Gaming", "Hiking", "Cooking", "Traveling", "Photography", "Music", "Sports"]

# Function to generate a fake user
def generate_fake_user(user_id):
    return {
        "id": f"user_{user_id}",
        "name": random.choice(names),
        "age": random.randint(18, 45),
        "gender": random.choice(["Male", "Female"]),  # Only Male and Female now
        "location": random.choice(locations),
        "mbti": random.choice(mbti_types),
        "big_five": {trait: round(random.uniform(0, 1), 2) for trait in big_five_traits},
        "hobbies": random.sample(hobbies, k=random.randint(2, 4))
    }

# Generate dataset of 100 users
fake_users = [generate_fake_user(i) for i in range(100)]

# Save dataset as JSON file
with open("fake_user_data.json", "w") as f:
    json.dump(fake_users, f, indent=4)

print("Fake user data generated and saved to fake_user_data.json")
