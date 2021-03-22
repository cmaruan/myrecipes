from django.test import TestCase
from django.shortcuts import reverse

import re
import json

from . import models

class BaseTestCase(TestCase):
    def create_default_units(self):
        self.kg = models.Unit.objects.create(
            # pk = 1
            name='Kilogram',
            short_name='kg',
            multiplier=1000,
            type='m',)
        self.g = models.Unit.objects.create(
            # pk = 2
            name='Gram',
            short_name='g',
            multiplier=1,
            type='m',)
        self.L = models.Unit.objects.create(
            # pk = 3
            name='Liter',
            short_name='L',
            multiplier=1,
            type='v',)
        self.ml = models.Unit.objects.create(
            # pk = 4
            name='Milliliter',
            short_name='ml',
            multiplier=0.001,
            type='v',)
    
    def create_ingredients(self):
        # Create two ingredients
        # 300g of Banana is $5
        # 1Kg of Banana is $16.67
        models.Ingredient.objects.create(
            name='banana',
            article_number='B001',
            cost=5,
            amount=300,
            unit=self.g)
            
        # 2L of Milk is $4
        # 1L of Milk is $2
        models.Ingredient.objects.create(
            name='milk',
            article_number='B002',
            cost=4,
            amount=2,
            unit=self.L)

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
            'directions': 'Steps',
            'ingredients': json.dumps([
                {'id': '1', 'selectedAmount': 2, 'unitId': 1},
                {'id': '2', 'selectedAmount': 3, 'unitId': 3},
            ])
        }
        response = self.client.post(reverse('recipe-create'), data)
        self.assertNotEqual(models.Recipe.objects.count(), 0, 'Recipe object must be created')
        # print('Recipes in DB:', models.Recipe.objects.count())
    
    def test_update_recipe_with_post(self):
        data = {
            'name': 'weird cookie',
            'directions': 'steps',
            'ingredients': json.dumps([
                {'id': '1', 'selectedAmount': 2, 'unitId': 1},
                {'id': '2', 'selectedAmount': 3, 'unitId': 3},
            ])
        }
        self.client.post(reverse('recipe-create'), data)
        data = {
            'name': 'weird cookie',
            'ingredients': json.dumps([
                {'id': '2', 'selectedAmount': 3, 'unitId': 3},
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

    def test_form_rejects_invalid_unit_conversion(self):
        data = {
            'name': 'weird cookie',
            'ingredients': json.dumps([
                {'id': '1', 'selectedAmount': 2, 'unitId': 3},
            ])
        }
        response = self.client.post(reverse('recipe-create'), data)
        content = response.content
        self.assertIn('You cannot convert between different types of unit', content.decode())

    def test_recipe_cost_is_correct(self):
        data = {
            'name': 'Pancake',
            'directions': 'steps',
            'ingredients': json.dumps([
                # 100g of Banana = 1.67
                {'id': '1', 'selectedAmount': 100, 'unitId': 2},
                # 100ml of Milk  = 0.20
                {'id': '2', 'selectedAmount': 100, 'unitId': 4},
            ])
        }
        response = self.client.post(reverse('recipe-create'), data)
        recipe = models.Recipe.objects.first()
        self.assertAlmostEqual(recipe.cost(), 1.87, 2)

    def test_recipe_cost_updates_accordingly(self):
        data = {
            'name': 'Pancake',
            'directions': 'steps',
            'ingredients': json.dumps([
                # 100g of Banana = 1.67
                {'id': '1', 'selectedAmount': 100, 'unitId': self.g.pk},
                # 100ml of Milk  = 0.20
                {'id': '2', 'selectedAmount': 100, 'unitId': self.ml.pk},
            ])
        }
        updated_data = {
            'name': 'Pancake',
            'directions': 'steps',
            'ingredients': json.dumps([
                # 1Kg of Banana = 16.67
                {'id': '1', 'selectedAmount': 1, 'unitId': self.kg.pk},
                # 400ml of Milk  = 0.80
                {'id': '2', 'selectedAmount': 0.4, 'unitId': self.L.pk},
            ])
        }
        response = self.client.post(reverse('recipe-create'), data)
        self.client.post(reverse('recipe-update', kwargs={'pk': '1'}), updated_data)
        recipe = models.Recipe.objects.first()

        self.assertAlmostEqual(recipe.cost(), 17.47, 2)

    def test_correct_ingredients_are_processed_by_backend(self):
        data = {
            'name': 'Pancake',
            'directions': 'steps',
            'ingredients': json.dumps([
                # 100g of Banana = 1.67
                {'id': '1', 'selectedAmount': 100, 'unitId': self.g.pk},
                # 100ml of Milk  = 0.20
                {'id': '2', 'selectedAmount': 100, 'unitId': self.ml.pk},
            ])
        }
        self.client.post(reverse('recipe-create'), data)
        response = self.client.get(reverse('recipe-update', kwargs={'pk': 1}))
        content = response.content
        decoded = content.decode()
        match = re.search(r'ingredientsSelected = JSON.parse\(\'(.*)\'\);', decoded)
        self.assertIsNotNone(match, "The object 'ingredientsSelected must be initialized'")

        returned_data = json.loads(match.group(1))
        self.assertEqual(returned_data[0]['id'], 1)
        self.assertEqual(returned_data[0]['unitId'], self.g.pk)
        self.assertAlmostEqual(returned_data[0]['selectedAmount'], 100)
        self.assertEqual(returned_data[1]['id'], 2)
        self.assertEqual(returned_data[1]['unitId'], self.ml.pk)
        self.assertAlmostEqual(returned_data[1]['selectedAmount'], 100)
