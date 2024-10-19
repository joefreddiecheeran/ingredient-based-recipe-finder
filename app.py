from flask import Flask, render_template, request
import pandas as pd
import re
from collections import Counter

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('recipes.csv')

# Add RecipeID as a unique identifier
df['RecipeID'] = df.index + 1

# Preprocess text by removing punctuation, lowercasing, and tokenizing
def preprocess_text(text):
    text = re.sub(r'[^\w\s]', '', text.lower())  # Remove punctuation and lowercase
    return text.split()  # Tokenize

# Preprocess both ingredients and instructions
df['Cleaned-Ingredients'] = df['Ingredients'].apply(preprocess_text)
df['Cleaned-Instructions'] = df['Instructions'].apply(preprocess_text)

# Create a combined "document" of ingredients and instructions for each recipe
df['Combined-Text'] = df['Cleaned-Ingredients'] + df['Cleaned-Instructions']

# Calculate term frequencies in the combined ingredients + instructions
all_terms = [item for sublist in df['Combined-Text'] for item in sublist]
term_freq = Counter(all_terms)

# Function to calculate the relevance score for a recipe based on searched ingredients
def calculate_relevance(query_ingredients, recipe_text, term_freq, N):
    relevant_score = 1
    non_relevant_score = 1
    for ingredient in query_ingredients:
        # Probability of term given relevance
        P_t_R = (recipe_text.count(ingredient) + 1) / N  # Count of term in recipe text (ingredients + instructions)
        # Probability of term given non-relevance
        P_t_NR = (term_freq[ingredient] + 1) / (N + 1)  # Count of term in the entire dataset
        
        relevant_score *= P_t_R
        non_relevant_score *= P_t_NR
    
    return relevant_score / non_relevant_score

# Function to preprocess query ingredients
def preprocess_query(query):
    return preprocess_text(query)

# Define a function to get relevant recipes based on query ingredients
def get_relevant_recipes(query_ingredients):
    N = len(df)  # Total number of recipes
    query_ingredients = preprocess_query(query_ingredients)
    
    # Calculate relevance for each recipe
    df['Relevance'] = df['Combined-Text'].apply(lambda recipe_text: 
                                                calculate_relevance(query_ingredients, recipe_text, term_freq, N))
    
    # Sort recipes based on relevance score (higher is better)
    return df.sort_values(by='Relevance', ascending=False)

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html', recipes=None)

# Route to handle search queries
@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').lower().strip()
    if not query:
        return render_template('index.html', recipes=[], recipe_count=0, searched_ingredients=None)

    relevant_recipes = get_relevant_recipes(query)
    # Include RecipeID along with other fields
    recipes = relevant_recipes[['RecipeID', 'RecipeName', 'Ingredients', 'TotalTimeInMins']].to_dict(orient='records')

    # Count the number of relevant recipes
    recipe_count = len(recipes)

    # Split the query to get individual ingredients and remove any empty strings
    searched_ingredients = [ingredient for ingredient in query.split() if ingredient]

    return render_template('index.html', recipes=recipes, recipe_count=recipe_count, searched_ingredients=searched_ingredients)






# Route to display an individual recipe
@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = df[df['RecipeID'] == recipe_id].iloc[0]
    return render_template('recipe.html', recipe=recipe)



if __name__ == '__main__':
    app.run(debug=True)
