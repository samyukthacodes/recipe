import openai
import os
import streamlit as st
from dotenv import load_dotenv
import json

# Load .env file
load_dotenv()
st.set_page_config(page_title="NutriVegan")
st.header("NutriVegan")

# Set up OpenAI API key
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Chat-based language model system messages
system_messages = """
Provide personalized vegan recipes based on dietary preferences, restrictions, and with available ingredients.
Specify your dietary preferences, any restrictions, and available ingredients.
Ensure to include the following elements in the recipe suggestions:
1. Recipe Name
2. Ingredients
3. Instructions
4. Cooking Time
5. Type (breakfast, lunch, dinner)
6. Cooking Style (Airfryer, Stove, Oven, Grill, Blender, Other)
7. Cuisine Type (Mediterranean, Asian, Keto, etc.)

Response should be in the following JSON Format

{
"responses":[
    {
    "name": <name of recipe>,
    "type": <type of meal>,
    "cooking_styles": <list of cooking styles>,
    "ingredients": <list of ingredients>,
    "instructions": <instructions>
    "cooking_time": <cooking time>,
    "servings": <number of servings>,
    "cuisine_type": <cuisine type>
    }]
}

Example:
For Dietary preferences: Gluten-free; Dietary Restrictions: Soy-free; Available ingredients: Chickpeas, kale, sweet potatoes, coconut milk
Response should be like the following

{ "responses": [
      { "name": "Stir-fried Chickpea Delight",
        "type": "lunch",
        "cooking_styles": ["Airfryer", "Stove"],
        "ingredients": [ "1 cup chickpeas", "1 cup kale", "1 cup sweet potatoes", "1/2 cup coconut milk" ],
        "instructions": "1. Heat oil in a pan.\n2. Stir-fry chickpeas, kale, and sweet potatoes until cooked.\n3. Add coconut milk and stir until well combined.\n4. Serve hot and enjoy!",
        "cooking_time": "20 minutes",
        "servings": 3,
        "cuisine_type": "Asian"
        }
     ] }
"""


def get_personalized_recipes(prompt):
    # Call OpenAI API for recipe suggestions
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_messages},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


def display_recipe(recipe):
    st.header(recipe['name'])
    st.subheader('Type: ' + recipe['type'])
    st.subheader('Cooking Styles: ' + ', '.join(recipe['cooking_styles']))
    st.subheader('Cuisine Type: ' + recipe['cuisine_type'])
    st.subheader('Ingredients')
    ingredients = "\n".join("- " + i for i in recipe['ingredients'])
    st.write(ingredients)
    st.subheader('Instructions')
    st.write(recipe["instructions"])
    st.write("⏰ Cooking time: " + recipe["cooking_time"] + " minutes")
    st.write("Servings: " + str(recipe["servings"]))
    st.divider()


def recipe_generator():
    st.subheader("Personalized Vegan Recipes Based on Your Preferences")

    # User input for recipe generation
    dietary_preferences = st.text_area("Dietary Preferences:")
    restrictions = st.text_area("Any Dietary Restrictions:")
    available_ingredients = st.text_area("Available Ingredients (comma-separated):")
    meal_type = st.selectbox("Select Type:", ["Breakfast", "Lunch", "Dinner"])
    cooking_time = st.slider("Select Cooking Time (minutes):", min_value=1, max_value=120)

    # Checkbox for multiple cooking styles
    cooking_styles = st.multiselect("Choose Cooking Styles:", ["Airfryer", "Stove", "Oven", "Grill", "Blender", "Other"])

    # If "Other" is selected, allow the user to input the type
    if "Other" in cooking_styles:
        custom_type = st.text_input("Enter Custom Type:")
    else:
        custom_type = None

    # Input for the number of servings
    servings = st.number_input("Number of Servings:", min_value=1, value=4, step=1)

    # Input for cuisine type
    cuisine_type = st.text_input("Cuisine Type:")

    user_prompt = f"Provide personalized vegan recipes based on dietary preferences: {dietary_preferences}. Restrictions: {restrictions}. Available Ingredients: {available_ingredients}. Type: {meal_type}. Cooking Time: {cooking_time} minutes. Cooking Styles: {cooking_styles}. Cuisine Type: {cuisine_type}. Servings: {servings}."

    if st.button("Generate Recipe Suggestions"):
        if dietary_preferences and available_ingredients:
            # Get personalized recipes from OpenAI
            recipe_suggestions = get_personalized_recipes(user_prompt)
            print("Received JSON response:", recipe_suggestions)
            st.success("Recommended Recipes:")
            try:
                recipes = json.loads(recipe_suggestions, strict=False)
                for recipe in recipes["responses"]:
                    display_recipe(recipe)
            except json.JSONDecodeError as e:
                st.error(f"Error decoding JSON: {e}")
        else:
            st.warning("Please fill in the required details.")

    # "Try Something New" option to generate a random recipe
    if st.button("Try Something New"):
        random_prompt = "Generate a random vegan recipe"
        random_recipe = get_personalized_recipes(random_prompt)
        st.success("Random Recipe:")
        try:
            random_recipe_data = json.loads(random_recipe, strict=False)
            display_recipe(random_recipe_data["responses"][0])
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}")


# Run the Streamlit app
if __name__ == "__main__":
    recipe_generator()
