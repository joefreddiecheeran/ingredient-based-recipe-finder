let ingredients = [];

function addIngredient() {
    const input = document.getElementById('ingredient-input');
    const ingredient = input.value.trim();
    if (ingredient && !ingredients.includes(ingredient)) {
        ingredients.push(ingredient);
        updateIngredientList();
    }
    input.value = '';
}

function removeIngredient(ingredient) {
    ingredients = ingredients.filter(i => i !== ingredient);
    updateIngredientList();
}

function updateIngredientList() {
    const listContainer = document.getElementById('ingredient-list');
    listContainer.innerHTML = '';
    ingredients.forEach(ingredient => {
        const pill = document.createElement('span');
        pill.className = 'ingredient-pill';
        pill.innerHTML = `${ingredient} <button onclick="removeIngredient('${ingredient}')">x</button>`;
        listContainer.appendChild(pill);
    });
}

function searchRecipes() {
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients }),
    })
    .then(response => response.json())
    .then(data => {
        displayRecipes(data.recipes);
    });
}

function displayRecipes(recipes) {
    const resultsContainer = document.getElementById('recipe-grid');
    const recipeCount = document.getElementById('recipe-count');

    if (recipes.length) {
        recipeCount.textContent = `You can make ${recipes.length} recipes`;
        resultsContainer.innerHTML = `
            ${recipes.map(recipe => `
                <div class="recipe-card">
                    <h3>${recipe.RecipeName}</h3>
                    <p>Ingredients: ${recipe.Ingredients}</p>
                    <p>Instructions: ${recipe.Instructions.slice(0, 100)}...</p>
                    <a href="${recipe.SourceURL}" target="_blank">View Recipe</a>
                </div>
            `).join('')}
        `;
    } else {
        recipeCount.textContent = '';
        resultsContainer.innerHTML = '<p>No recipes found. Try different ingredients.</p>';
    }
}
