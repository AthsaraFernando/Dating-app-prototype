import openai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate embeddings
def get_embedding(text):
    try:
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding  # Correct way to access data
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Function to combine user data for embedding generation
def combine_user_data(user):
    # Handle Big Five traits and hobbies separately
    big_five = user['big_five']
    big_five_str = ", ".join(f"{trait}: {score}" for trait, score in big_five.items())
    hobbies_str = ", ".join(user['hobbies'])

    # Combine for generating embeddings later (separate Big Five and hobbies for now)
    return {
        'big_five': big_five_str,
        'hobbies': hobbies_str
    }

# Load user data
with open('fake_user_data.json', 'r') as f:
    users = json.load(f)

# Generate embeddings for each user
for user in users:
    user_data = combine_user_data(user)
    
    # Get embeddings for both Big Five and hobbies separately
    big_five_embedding = get_embedding(user_data['big_five'])
    hobbies_embedding = get_embedding(user_data['hobbies'])
    
    # Store embeddings
    if big_five_embedding and hobbies_embedding:
        user['big_five_embedding'] = big_five_embedding
        user['hobbies_embedding'] = hobbies_embedding

# Save embeddings to a file
with open("user_embeddings.json", "w") as file:
    json.dump(users, file, indent=4)

print("Embeddings generation completed!")
