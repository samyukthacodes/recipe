# recipe_recommendation.py

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Sample data for recipes
recipes_data = pd.DataFrame({
    'Recipe': ['Vegan Pasta', 'Quinoa Salad', 'Sweet Potato Curry', 'Chickpea Stir-Fry'],
    'Ingredients': [
        'pasta, tomato sauce, vegetables',
        'quinoa, vegetables, vinaigrette',
        'sweet potato, coconut milk, curry paste',
        'chickpeas, vegetables, soy sauce'
    ]
})

# User input for preferences
st.sidebar.title('User Preferences')
dietary_preferences = st.sidebar.text_input('Dietary Preferences (comma-separated)', 'vegan')
restrictions = st.sidebar.text_input('Restrictions (comma-separated)', '')
ingredient_vulnerability = st.sidebar.text_input('Ingredient Vulnerability', '')

# Create user data DataFrame
user_data = pd.DataFrame({
    'User': ['User1'],
    'Dietary_Preferences': [dietary_preferences],
    'Restrictions': [restrictions],
    'Ingredient_Vulnerability': [ingredient_vulnerability]
})

# Preprocess data
recipes_data['text'] = recipes_data['Ingredients'].str.replace(',', ' ')
user_data['text'] = user_data[['Dietary_Preferences', 'Restrictions', 'Ingredient_Vulnerability']].apply(lambda x: ' '.join(x), axis=1)

# Vectorize text data
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(pd.concat([recipes_data['text'], user_data['text']]))

# Calculate cosine similarity
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Streamlit app
st.title('Vegan Recipe Recommender')

# Display user preferences
st.sidebar.subheader('User Preferences')
st.sidebar.text('Dietary Preferences: ' + dietary_preferences)
st.sidebar.text('Restrictions: ' + restrictions)
st.sidebar.text('Ingredient Vulnerability: ' + ingredient_vulnerability)

# Recommend recipes
user_index = user_data.index[0]
cosine_sim_user = cosine_sim[user_index]
similar_recipes = list(enumerate(cosine_sim_user))

# Sort recipes based on similarity
similar_recipes = sorted(similar_recipes, key=lambda x: x[1], reverse=True)

# Display recommended recipes
st.subheader('Recommended Recipes')
for i in range(1, min(6, len(similar_recipes))):  # Display at most 5 recipes
    recipe_index = similar_recipes[i][0]

    # Check if the recipe_index is within the valid range
    if recipe_index < len(recipes_data):
        st.write(recipes_data['Recipe'].iloc[recipe_index])
    else:
        st.warning("Recipe index out of bounds.")
