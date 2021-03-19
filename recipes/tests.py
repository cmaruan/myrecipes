from django.test import TestCase
from django.shortcuts import reverse

import json

from . import models

class BaseTestCase(TestCase):
    def create_default_units(self):
        models.Unit.objects.create(
            # pk = 1
            name='Kilogram',
            short_name='kg',
            multiplier=1000,
            type='m',)
        models.Unit.objects.create(
            # pk = 2
            name='Gram',
            short_name='g',
            multiplier=1,
            type='m',)
        models.Unit.objects.create(
            # pk = 3
            name='Liter',
            short_name='L',
            multiplier=1,
            type='v',)
        models.Unit.objects.create(
            # pk = 2
            name='Milliliter',
            short_name='ml',
            multiplier=0.001,
            type='v',)
    
    def create_ingredients(self):
        # Create two ingredients
        models.Ingredient.objects.create(
            name='banana',
            cost=10,
            unit_id=1,
            article_number='B001',
            amount=10)
        models.Ingredient.objects.create(
            name='milk',
            cost=5,
            unit_id=3,
            article_number='B002',
            amount=2)

class IngredientsTestCase(BaseTestCase):
    def setUp(self):
        self.create_default_units()

    def test_can_create_ingredient_with_post(self):
        data = {
            'name': 'banana',
            'cost': '10',
            'unit': '1',
            'article_number': 'a001',
            'amount': '10'
        }
        response = self.client.post(reverse('ingredient-create'), data)
        self.assertNotEqual(models.Ingredient.objects.count(), 0)
    
    def test_required_fields_for_post(self):
        data = {
            'name': 'banana',
            'cost': '10',
            'unit': '1',
            'article_number': 'a001',
            'amount': '10'
        }
        not_required = []
        for field in data.keys():
            invalid_data = data.copy()
            invalid_data.pop(field)
            response = self.client.post(reverse('ingredient-create'), invalid_data)
            content = response.content
            decoded = content.decode()
            if 'This field is required' not in decoded:
                not_required.append(field)
        error_message = f'The following fields should be required {not_required}'
        self.assertEqual(len(not_required), 0, error_message)
        self.assertEqual(models.Ingredient.objects.count(), 0, 'No object should have been created.')
    

class RecipeTestCase(BaseTestCase):

    def setUp(self):
        self.create_default_units()
        self.create_ingredients()


    def test_can_create_recipe_with_post(self):
        data = {
            'name': 'weird cookie',
            'ingredients': json.dumps([
                {'id': '1', 'selectedAmount': 2, 'unit_id': 1},
                {'id': '2', 'selectedAmount': 3, 'unit_id': 3},
            ])
        }
        response = self.client.post(reverse('recipe-create'), data)
        self.assertNotEqual(models.Recipe.objects.count(), 0, 'Recipe object must be created')
        # print('Recipes in DB:', models.Recipe.objects.count())
    
    def test_update_recipe_with_post(self):
        data = {
            'name': 'weird cookie',
            'ingredients': json.dumps([
                {'id': '1', 'selectedAmount': 2, 'unit_id': 1},
                {'id': '2', 'selectedAmount': 3, 'unit_id': 3},
            ])
        }
        self.client.post(reverse('recipe-create'), data)
        data = {
            'name': 'weird cookie',
            'ingredients': json.dumps([
                {'id': '2', 'selectedAmount': 3, 'unit_id': 3},
            ])
        }
        self.client.post(reverse('recipe-update', kwargs={'pk': '1'}), data)
        recipe = models.Recipe.objects.get(pk=1)
        ingredients = recipe.ingredients.all()
        ingredients_of_recipe = models.RecipeIngredient.objects.filter(
            ingredient=ingredients[0],
            recipe=recipe
        )
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(len(ingredients_of_recipe), 1)
