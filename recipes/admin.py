from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    readonly_fields = ['unit_cost']
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    readonly_fields = ['cost']
    list_display = [
        'name',
        'cost',
    ]