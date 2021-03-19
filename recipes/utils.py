MODULES_INFO = {
    'title': 'My Recipes',
    'active': 'ingredients',
    'submodules': {
        'ingredients': {
            'id': 'ingredients',
            'name': 'Ingredients',
            'create_btn': 'New Ingredient',
            'template': 'recipes/ingredient_list.html',
            'create_link': 'ingredient-create',
            'list_link': 'ingredient-list',
        },
        'recipes': { 
            'id': 'recipes', 
            'name': 'Recipes', 
            'create_btn': 'New Recipe',
            'template': 'recipes/recipe_list.html',
            'create_link': 'recipe-create',
            'list_link': 'recipe-list',
        },
    },
    'recipes': [],
    'ingredients': [],
}