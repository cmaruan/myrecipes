from django.urls import path, include
from .views import (
    IngredientListView,
    IngredientUpdateView,
    IngredientCreateView,
    RecipeListView,
    RecipeCreateView,
    RecipeUpdateView,
    MyRecipesView,
)

urlpatterns = [
    path('', MyRecipesView.as_view(), name='homepage'),

    path('ingredients/', IngredientListView.as_view(), name='ingredient-list'),
    path('ingredients/create/', IngredientCreateView.as_view(), name='ingredient-create'),
    path('ingredients/<int:pk>/', IngredientUpdateView.as_view(), name='ingredient-update'),
    
    path('recipes/', RecipeListView.as_view(), name='recipe-list'),
    path('recipes/create/', RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/<int:pk>', RecipeUpdateView.as_view(), name='recipe-update')
    
]
