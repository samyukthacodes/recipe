import openai
import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import json
# Load .env file
load_dotenv()

# Set up OpenAI API key
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Chat-based language model system messages
system_messages = """Provide personalized vegan recipes based on dietary preferences, restrictions, and with available ingredients. 
Specify your dietary preferences, any restrictions, and available ingredients.
Ensure to include the following elements in the recipe suggestions:
1. Recipe Name
2. Ingredients
3. Instructions
4. Cooking Time

Response should be in following JSON Format

{
"responses":[
    {
    "name": <name of recipe>,
    "ingredients": <list of ingredients>,
    "instructions": <instructions>
    "cooking_time" : <cooking time>
    }]
}

Example: 
For Dietary preferences: Protein, Vitamin; Dietary Restrictions: Sugar, Available ingredients: Oats, chocolate, cashewnut, badam, strawberry, peanut butter
Response should be like the following

{ "responses": [
      { "name": "Chocolate Peanut Butter Oat Bars", 
        "ingredients": [ "1 cup oats", "1/2 cup chocolate chips", "1/2 cup smooth peanut butter", "1/4 cup maple syrup", "1/4 cup crushed cashew nuts" ],
        "instructions": "1. Preheat the oven to 350°F (175°C).\n2. In a mixing bowl, combine the oats, chocolate chips, peanut butter, maple syrup, and crushed cashew nuts. Mix well.\n3. Press the mixture into a greased baking dish.\n4. Bake in the preheated oven for 15-20 minutes or until the edges turn golden brown.\n5. Remove from the oven and let it cool completely before cutting into bars. Enjoy!", "cooking_time": "25 minutes" 
        },
        { "name": "Strawberry Almond Smoothie",
        "ingredients": [ "1 cup strawberries (fresh or frozen)", "1 cup almond milk", "1 tablespoon almond butter", "1 tablespoon maple syrup", "1 handful crushed ice" ], 
        "instructions": "1. In a blender, combine the strawberries, almond milk, almond butter, maple syrup, and crushed ice.\n2. Blend until smooth and creamy.\n3. Pour into glasses and garnish with sliced strawberries, if desired. Enjoy!",
        "cooking_time": "5 minutes" 
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
    st.header("Vegan Recipe Generator")
    st.subheader("Personalized Vegan Recipes Based on Your Preferences")

    # User input for recipe generation
    dietary_preferences = st.text_area("Dietary Preferences:")
    restrictions = st.text_area("Any Dietary Restrictions:")
    available_ingredients = st.text_area("Available Ingredients (comma-separated):")

    user_prompt = f"Provide personalized vegan recipes based on dietary preferences: {dietary_preferences}. Restrictions: {restrictions}. Available Ingredients: {available_ingredients}."

    
    if st.button("Generate Recipe Suggestions"):
        if dietary_preferences and available_ingredients:
            # Get personalized recipes from OpenAI
            recipe_suggestions = get_personalized_recipes(user_prompt)
            print(recipe_suggestions)
            st.success("Recommended Recipes:")
            recipes = json.loads(recipe_suggestions, strict = False)
            for recipe in recipes["responses"]:
                st.header(recipe['name'])
                st.subheader('Ingredients')
                ingredients = " "
                for i in recipe['ingredients']:
                    ingredients += "- " + i + "\n"
                st.write(ingredients)
                st.subheader('Instructions')
                st.write(recipe["instructions"])
                st.write("⏰ Cooking time : " + recipe["cooking_time"])
                st.divider()
            
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
    

# Run the Streamlit app
if __name__ == "__main__":
    recipe_generator()
