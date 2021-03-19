from django.db import models
from django.db.models import F, Sum
from django.shortcuts import reverse

class Unit(models.Model):
    class TypesOfUnit(models.TextChoices):
        VOLUME = 'v', 'Volume'
        MASS = 'm', 'Mass'

    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=3, unique=True)
    multiplier = models.FloatField()
    type = models.CharField(max_length=1, choices=TypesOfUnit.choices)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    article_number = models.CharField(max_length=50, unique=True)
    cost = models.FloatField()
    amount = models.FloatField()
    disabled = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    parent = models.ForeignKey("Ingredient", on_delete=models.CASCADE, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('ingredient-update', args=[self.pk])

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=256)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )

    def __str__(self):
        return self.name
    
    def cost(self):
        recipe_cost = self.ingredients.aggregate(
            cost=Sum(
                F('recipeingredient__unit_cost') * 
                F('recipeingredient__amount') * 
                F('recipeingredient__display_unit__multiplier')
        ))
        return recipe_cost['cost']

    

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField()
    display_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    unit_cost = models.FloatField()

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} {self.unit_cost * self.amount * self.display_unit.multiplier}'