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
Provide personalized vegan recipes(atleast two) based on:
1. dietary preferences
2. dietary restrictions
3. Available ingredients.
4. Cooking time(in minutes)
5. Cooking Equipments Available
6. Type of meal
7. Number of servings
8. Cuisine type

Number of ingredients outside of the available ingredients shouldn't be more. Try to stay within the limit of available ingedients. 
Cooking time should be within the limit mentioned with available ingredients. Lesser the cooking time, the better.
Should take the available cooking equipments into consideration.

Ensure to include the following elements in the recipe suggestions:
1. Recipe Name
2. Ingredients
3. Instructions
4. Cooking Time(in minutes)
5. Cuisine Type (Mediterranean, Asian, Keto, etc.)

Response should be in the following JSON Format

{
"responses":[
    {
    "name": <name of recipe>,
    "ingredients": <list of ingredients>,
    "instructions": <instructions>
    "cooking_time": <cooking time>,
    "servings": <servings>,
    "cuisine_type": <cuisine type>
    }]
}

Example:
For 
Dietary preferences: High Protein; 
Dietary Restrictions: No sugar; 
Available ingredients: Oats, banana, blueberry, strawberry, almond milk, cocoa powder, cashew nuts, peanut butter
Type of meal: Breakfast
Cooking time: 15
Cooking Equipments Available: Blender
Number of servings: 3
Cuisine type: None


Response should be like the following

{
"responses":[
    {
    "name": "Protein-Packed Berry Smoothie Bowl",
    "ingredients": ["1 cup oats", "1 banana", "1/2 cup blueberries", "1/2 cup strawberries", "1 cup almond milk", "1 tbsp cocoa powder", "2 tbsp cashew nuts", "2 tbsp peanut butter"],
    "instructions": "1. In a blender, combine oats, banana, blueberries, strawberries, almond milk, cocoa powder, cashew nuts, and peanut butter.
2. Blend until smooth and creamy.
3. Pour the smoothie into bowls.
4. Top with additional berries, cashew nuts, and a drizzle of peanut butter.
5. Serve and enjoy!",
    "cooking_time": "15 minutes",
    "servings": 3,
    "cuisine_type": "Breakfast"
    },
    { "name": "Protein-Packed Banana Smoothie Bowl",
        "ingredients": [ "1 cup oats", "1 banana", "1 cup blueberries", "1 cup strawberries", "1 cup almond milk", "2 tbsp cocoa powder", "2 tbsp cashew nuts", "2 tbsp peanut butter" ],
        "instructions": "1. In a blender, combine oats, banana, blueberries, strawberries, almond milk, cocoa powder, cashew nuts, and peanut butter.
2. Blend until smooth and creamy.
3. Pour the mixture into bowls.
4. Optional: Top with additional banana slices, blueberries, strawberries, and cashew nuts.
5. Serve immediately and enjoy!",
        "cooking_time": "15 minutes",
        "servings": 3,
        "cuisine_type": "Breakfast"
    },
    { 
        "name": "Protein-Packed Banana Muffins",
        "ingredients": ["1 cup oats", "1 scoop protein powder", "1/2 cup almond milk", "1/4 cup cashews", "1/4 cup cocoa powder", "1 banana", "2 tbsp peanut butter"],
        "instructions": "1. Preheat the oven to 350°F (175°C). Grease a muffin tin or line with cupcake liners.
2. In a blender, combine oats, protein powder, almond milk, cashews, cocoa powder, banana, and peanut butter.
3. Blend until smooth and creamy.
4. Pour the mixture into a mixing bowl.
5. Add additional oats or almond milk if needed to adjust the consistency.
6. Spoon the batter into the prepared muffin tin, filling each cup about 3/4 full.
7. Optional: Top with additional cashews or banana slices.
8. Bake for 12-15 minutes, or until a toothpick inserted into the center of a muffin comes out clean.
9. Remove from the oven and let cool for a few minutes before transferring to a wire rack to cool completely.
10. Serve and enjoy!",
        "cooking_time": "17 minutes",
        "servings": 2,
        "cuisine_type": "American"
        }

]
}

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
