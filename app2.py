import openai
import os
import streamlit as st
from dotenv import load_dotenv
import json
import random

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
    "servings": <number of servings>
    }]
}

Example:
For Dietary preferences: Protein, Vitamin; Dietary Restrictions: Sugar, Available ingredients: Oats, chocolate, cashewnut, badam, strawberry, peanut butter
Response should be like the following

{ "responses": [
      { "name": "Chocolate Peanut Butter Oat Bars",
        "type": "breakfast",
        "cooking_styles": ["Oven"],
        "ingredients": [ "1 cup oats", "1/2 cup chocolate chips", "1/2 cup smooth peanut butter", "1/4 cup maple syrup", "1/4 cup crushed cashew nuts" ],
        "instructions": "1. Preheat the oven to 350°F (175°C).\n2. In a mixing bowl, combine the oats, chocolate chips, peanut butter, maple syrup, and crushed cashew nuts. Mix well.\n3. Press the mixture into a greased baking dish.\n4. Bake in the preheated oven for 15-20 minutes or until the edges turn golden brown.\n5. Remove from the oven and let it cool completely before cutting into bars. Enjoy!",
        "cooking_time": "25 minutes",
        "servings": 4
        },
        { "name": "Strawberry Almond Smoothie",
        "type": "breakfast",
        "cooking_styles": ["Blender"],
        "ingredients": [ "1 cup strawberries (fresh or frozen)", "1 cup almond milk", "1 tablespoon almond butter", "1 tablespoon maple syrup", "1 handful crushed ice" ],
        "instructions": "1. In a blender, combine the strawberries, almond milk, almond butter, maple syrup, and crushed ice.\n2. Blend until smooth and creamy.\n3. Pour into glasses and garnish with sliced strawberries, if desired. Enjoy!",
        "cooking_time": "5 minutes",
        "servings": 2
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

# Main part of the Streamlit app
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

    user_prompt = f"Provide personalized vegan recipes based on dietary preferences: {dietary_preferences}. Restrictions: {restrictions}. Available Ingredients: {available_ingredients}. Type: {meal_type}. Cooking Time: {cooking_time} minutes. Cooking Styles: {cooking_styles}. Servings: {servings}."

    if st.button("Generate Recipe Suggestions"):
        if dietary_preferences and available_ingredients:
            # Get personalized recipes from OpenAI
            recipe_suggestions = get_personalized_recipes(user_prompt)
            print(recipe_suggestions)
            st.success("Recommended Recipes:")
            recipes = json.loads(recipe_suggestions, strict=False)
            for recipe in recipes["responses"]:
                st.header(recipe['name'])
                st.subheader('Type: ' + (custom_type if custom_type else recipe['type']))
                st.subheader('Cooking Styles: ' + ', '.join(recipe['cooking_styles']))
                st.subheader('Ingredients')
                ingredients = " "
                for i in recipe['ingredients']:
                    ingredients += "- " + i + "\n"
                st.write(ingredients)
                st.subheader('Instructions')
                st.write(recipe["instructions"])
                st.write("⏰ Cooking time: " + recipe["cooking_time"] + " minutes")
                st.write("Servings: " + str(recipe["servings"]))
                st.divider()

            # Allow user to add reviews after seeing the recipes
            reviews = st.text_area("Add Reviews:")
            st.write("Reviews: " + reviews)

            from pathlib import Path
            speech_file_path = Path(__file__).parent / "speech.mp3"
            response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=recipe_suggestions
            )
            response.stream_to_file(speech_file_path)
        else:
            st.warning("Please fill in the required details.")

    # "Try Something New" option to generate a random recipe
    if st.button("Try Something New"):
        random_prompt = "Generate a random vegan recipe"
        random_recipe = get_personalized_recipes(random_prompt)
        st.success("Random Recipe:")
        random_recipe_data = json.loads(random_recipe, strict=False)
        st.header(random_recipe_data["responses"][0]["name"])
        st.subheader('Type: ' + random_recipe_data["responses"][0]["type"])
        st.subheader('Cooking Styles: ' + ', '.join(random_recipe_data["responses"][0]["cooking_styles"]))
        st.subheader('Ingredients')
        random_ingredients = " "
        for i in random_recipe_data["responses"][0]["ingredients"]:
            random_ingredients += "- " + i + "\n"
        st.write(random_ingredients)
        st.subheader('Instructions')
        st.write(random_recipe_data["responses"][0]["instructions"])
        st.write("⏰ Cooking time: " + random_recipe_data["responses"][0]["cooking_time"])
        st.write("Servings: " + str(random_recipe_data["responses"][0]["servings"]))
        st.divider()

# Run the Streamlit app
if __name__ == "__main__":
    recipe_generator()
