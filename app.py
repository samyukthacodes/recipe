import openai
import os
import streamlit as st
from deta import Deta
import bcrypt
import datetime
from datetime import date
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
from dotenv import load_dotenv
from pathlib import Path
from pathlib import Path
import requests
import json
import random
from PIL import Image
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
image = Image.open('nutrilogo.png')

st.set_page_config(page_title='NutriVeg', page_icon='nutriilogo.png')

# Load .env file
load_dotenv()
st.sidebar.image(image, width=275)

# Set up OpenAI API key
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set up Deta
DETA_KEY = os.getenv('DETA_KEY')
deta = Deta(DETA_KEY)
db = deta.Base('user')
recipes_db = deta.Base('recipes')



def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  # Decode bytes to string

# Function to insert a new user with dietary information
def insert_user(email, username, password,dietary_restrictions):
    date_joined = str(datetime.datetime.now())
    hashed_password = hash_password(password)

    return db.put({
        'key': username,
        'username': username,
        'password': hashed_password,
        'date_joined': date_joined,

        'dietary_restrictions': dietary_restrictions,
        'responses': [],
        'history': []
    })


# Function to authenticate a user
def authenticate_user(username, password, page_visited):
    user = db.get(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # Ensure 'history' key exists or create it
        user['history'] = user.get('history', [])

        # Update login history for the specific page
        login_time = str(datetime.datetime.now())
        user['history'].append({'login_time': login_time, 'page_visited': page_visited})

        db.put(user)
        return user
    return None

def sign_up():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(':green[Sign Up]')
        email = st.text_input(':blue[Email]', placeholder='Enter Your Email')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password1 = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')
        password2 = st.text_input(':blue[Confirm Password]', placeholder='Confirm Your Password', type='password')
        dietary_restrictions = st.text_input(':blue[Dietary Restrictions]', placeholder='Enter Your Dietary Restrictions')

        if st.form_submit_button('Sign Up'):
            if password1 == password2:
                result = insert_user(email, username, password1, dietary_restrictions)
                st.success(f"User {username} successfully created! Date joined: {result['date_joined']}")
            else:
                st.error("Passwords do not match. Please try again.")

def login():
    with st.sidebar.form(key='login', clear_on_submit=True):
        st.subheader(':green[Log In]')
        username = st.text_input(':blue[Username]', placeholder='Enter Your Username')
        password = st.text_input(':blue[Password]', placeholder='Enter Your Password', type='password')

        if st.form_submit_button('Log In'):
            user = authenticate_user(username, password, "Dashboard")
            if user:
                st.session_state.is_authenticated = True
                st.success(f"Welcome back, {user['username']}! Last login: {datetime.datetime.now()}")
                st.session_state.username = user['username']
                st.session_state.is_authenticated = True
                return user
                
                
            else:
                st.error("Authentication failed. Please check your username and password.")
        



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
Should take the available cooking equipments into consideration.
Food should not contain ingredients that does not align with dietary restrictions.
Ensure to include the following elements in the recipe suggestions:
1. Recipe Name
2. Ingredients
3. Instructions
4. Cooking Time(in minutes)

Response should be in the following JSON Format

{
"responses":[
    {
    "name": <name of recipe>,
    "ingredients": <list of ingredients>,
    "instructions": <instructions>
    "cooking_time": <cooking time>,
    "servings": <servings>,
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
    "servings": 3
    },
    { "name": "Protein-Packed Banana Smoothie Bowl",
        "ingredients": [ "1 cup oats", "1 banana", "1 cup blueberries", "1 cup strawberries", "1 cup almond milk", "2 tbsp cocoa powder", "2 tbsp cashew nuts", "2 tbsp peanut butter" ],
        "instructions": "1. In a blender, combine oats, banana, blueberries, strawberries, almond milk, cocoa powder, cashew nuts, and peanut butter.
2. Blend until smooth and creamy.
3. Pour the mixture into bowls.
4. Optional: Top with additional banana slices, blueberries, strawberries, and cashew nuts.
5. Serve immediately and enjoy!",
        "cooking_time": "15 minutes",
        "servings": 3
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
        "servings": 2
        }

]
}

"""



# Function to load Lottie file from URL
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()



def display_recipe(recipe):
    st.header(recipe['name'])
    st.subheader('Ingredients')
    ingredients = "\n".join("- " + i for i in recipe['ingredients'])
    st.write(ingredients)
    st.subheader('Instructions')
    st.write(recipe["instructions"])
    st.write("⏰ Cooking time: " + recipe["cooking_time"])
    st.write("Servings: " + str(recipe["servings"]))
    st.divider()


# Now you can use the json_file_path in your Streamlit app or other parts of your code.
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
def recipe_generator(username):
    st.subheader("Personalized Vegan Recipes Based on Your Preferences")

    # User input for recipe generation
    dietary_preferences = st.text_area("Dietary Preferences:", key = "dietary_preferences")
    restrictions = st.text_area("Any Dietary Restrictions:", key = "dietary_restrictions")
    available_ingredients = st.text_area("Available Ingredients (comma-separated):", key = "available_ingredients")
    meal_type = st.selectbox("Select Type:", ["Breakfast", "Lunch", "Dinner"], key = "meal_Type")
    cooking_time = st.slider("Select Cooking Time (minutes):", min_value=1, max_value=120, key = "cooking_time")
    cooking_styles = st.multiselect("Choose Cooking Styles:", ["Airfryer", "Stove", "Oven", "Grill", "Blender", "Other"])

    
    # If cooking style is chosen as "Other," allow the user to input the type
    if cooking_styles == "Other":
        custom_type = st.text_input("Enter Custom Type:")
    else:
        custom_type = None
    
    # Input for cuisine type
    
    # Input for the number of servings
    servings = st.number_input("Number of Servings:", min_value=1, value=4, step=1)
    cuisine_type = st.text_input("Cuisine Type:")


    user_prompt = f"""Provide personalized vegan recipes based on 
    dietary preferences: {dietary_preferences},
    Restrictions: {restrictions},
    Available Ingredients: {available_ingredients},
    Type: {meal_type},
    Cooking Time: {cooking_time} minutes,
    Cooking Styles: {cooking_styles},
    Cuisine Type: {cuisine_type},
    Servings: {servings}."""

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

        
# Display the signup form in the sidebar
with st.sidebar:
    st.title('NutriVeg')
    
    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'])
    
    if choice == "Sign Up":
        sign_up()
    elif choice == "Login":
        user = login()
        if user:
            st.session_state["username"] = user['key']
             # Pass the username to the recipe_generator function
    if st.session_state.is_authenticated:
        placeholder = st.empty()
        if placeholder.button("Logout"):
            st.session_state.is_authenticated = False
            placeholder.empty()
    
          

# Function to insert a new recipe
def insert_recipe(username, title, ingredients, recipe_content):
    timestamp = str(datetime.datetime.now())
    return recipes_db.put({'username': username, 'title': title, 'ingredients': ingredients, 'recipe': recipe_content, 'timestamp': timestamp})

# Function to get all recipes
def get_all_recipes():
    recipes = recipes_db.fetch().items
    print(recipes)
    return recipes

# Main part of the Streamlit app
def recipe_social_media():

    # Display all recipes
    st.title("Recipes Feed")
    recipes = get_all_recipes()
    for recipe in recipes[::-1]:
        st.write(f"**{recipe['username']}**:")
        st.header(recipe['title'])
        st.subheader('Ingredients')
        st.write(recipe['ingredients'])
        st.subheader('Instructions')
        st.write(recipe['recipe'])
        
        st.divider()

def upload_recipes(username):
    title = st.text_input("Title")
    ingredients = st.text_area("Ingredients: ", key = 'ingredients')
    recipe_content = st.text_area("Recipe Content:", key = 'recipe_content')
    if st.button("Upload Recipe"):
        insert_recipe(username=username, ingredients=ingredients, title=title, recipe_content=recipe_content)
        st.success("Recipe uploaded successfully!")


# Run the Streamlit app
if __name__ == "__main__":
    
# 2. Horizontal menu
    st.title("NutriVeg")
    st.subheader("Elevate Your Plate with AI-Powered Plant Bliss")
    selected_horizontal = option_menu(None, ["Home", "Dashboard", "Social media","Upload Recipe", 'Contact'], 
        icons=['house', 'chat-dots','people-fill','clock-history', 'telephone'], 
        menu_icon="cast", default_index=0, orientation="horizontal")


    # Load Lottie file for animation (replace with your actual Lottie URL)
    lottie_hello = load_lottieurl("https://lottie.host/6729af09-07c8-4adb-a768-3a2f366834b3/WO1501fN3r.json")

    # Content based on selected option
    if selected_horizontal == "Home":
        st_lottie(
            lottie_hello,
            speed=1,
            reverse=False,
            loop=True,
            quality="low",  # medium; high
            height=300,
            width=300,
            key=None,
        )

        st.header("Overview")
        st.markdown("""An AI-powered vegan recipe app catering to personalized preferences, restrictions, and ingredient availability, doubling as a social platform for users to share, review, and like recipes.
        """)

        st.header("Our Mission")

        st.markdown("""Empowering individuals to embrace a plant-based lifestyle by offering tailored vegan recipes and fostering a vibrant community through shared culinary experiences.""")

        st.header("Our Services")

        st.markdown("""Personalized recipe generation based on dietary needs, restrictions, and ingredient availability, coupled with a social media platform for users to upload, review, and like vegan recipes.
        """)

    elif selected_horizontal == 'Dashboard':
        if st.session_state.is_authenticated:
            recipe_generator(st.session_state["username"])
        else:
            st.error('Please Login')
    elif selected_horizontal == 'Contact':
        st.header("Contact Us")

        contacts = [
            {"name": "Samyuktha Sudheer", "phone": "+123456789", "email": "samyusudheer@gmail.com"},
            {"name": "Rose Mary P John", "phone": "+987654321", "email": "rosemarypjohn@gmail.com"},
            {"name": "Riya Derose Micheal", "phone": "+111223344", "email": "riyaderose@gmail.com"},
            {"name": "Thej T Thomas", "phone": "+555666777", "email": "thejtthomas@gmail.com"}
        ]

        phone_icon = "📞"
        mail_icon = "✉️"

        for contact in contacts:
            st.subheader(contact["name"])
            st.write(f"{phone_icon} Phone: {contact['phone']}")
            st.write(f"{mail_icon} Email: {contact['email']}")
            st.write("---")
    elif selected_horizontal == "Upload Recipe":
        if st.session_state.is_authenticated:
            upload_recipes(st.session_state.username)
        else:
            st.error('Please Login')
    elif selected_horizontal == 'Social media':
        if st.session_state.is_authenticated:
            recipe_social_media()
        else:
            st.error('Please Login')
        



    

    