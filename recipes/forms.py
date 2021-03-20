import json
from django import forms
from django.db.models import F
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Ingredient, Unit, Recipe, RecipeIngredient

class CreateIngredientForm(forms.ModelForm):
    cost = forms.CharField(max_length=50, required=True, label='Cost €')
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'article_number',
            'cost',
            'amount',
            'unit',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class=''),
                Column('article_number', css_class=''),
                css_class='grid grid-cols-2 gap-4'
            ),
            Row(
                Column('cost', css_class=''),
                Column('amount', css_class=''),
                Column('unit', css_class=''),
                css_class='grid grid-cols-3 gap-4'
            ),
            Row(
                Column(
                    Submit('save', 'Save', css_class='bg-blue-900 text-gray-100 py-2 px-3 rounded-md'),
                    css_class='flex justify-end'
                ),
                css_class='grid'
            )
        )

    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if not amount:
            raise forms.ValidationError('Amount must be grater than zero', code='invalid')
        return amount

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if not cost:
            raise forms.ValidationError('Cost must be grater than zero', code='invalid')
        return cost

class UpdateIngredientForm(CreateIngredientForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='mb-0'),
                Column('article_number', css_class='mb-0'),
                css_class='grid grid-cols-2 gap-4'
            ),
            Row(
                Column('cost', css_class='mb-0'),
                Column('amount', css_class='mb-0'),
                Column('unit', css_class='mb-0'),
                css_class='grid grid-cols-3 gap-4'
            ),
            Row(
                Column(
                    Submit('delete', 'Delete',css_class='bg-red-900 text-red-100 py-2 px-3 rounded-md'),
                    Submit('save', 'Save', css_class='ml-3 bg-blue-900 text-gray-100 py-2 px-3 rounded-md'),
                    css_class='flex justify-end'
                ),
                 css_class='grid'
            )
        )

class RecipeForm(forms.Form):
    name = forms.CharField(required=True)
    directions = forms.CharField(required=True)
    ingredients = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', None)
        data = kwargs.pop('data', {})

        values = {}
        kwargs.pop('name')
        kwargs.pop('ingredients')

        name = data.get('name', None)
        ingredients = data.get('ingredients', None)
        directions = data.get('directions', None)

        if name:
            values.update(name=name)
        elif self.pk:
            recipe = Recipe.objects.get(pk=self.pk)
            values.update(name=recipe.name)

        if directions:
            values.update(directions=directions)
        elif self.pk:
            values.update(directions=recipe.directions)
        
        if ingredients:
            values.update(ingredients=ingredients)
        elif self.pk:
            ingredients = recipe.ingredients.values(
                'unit_id',
                'id',
                itemCost=F('amount')*F('recipeingredient__unit_cost')*F('recipeingredient__display_unit__multiplier'),
                selectedAmount=F('amount'),
                selectedUnit=F('recipeingredient__display_unit__short_name'))
            values.update(ingredients=json.dumps(list(ingredients)))

        if name or ingredients:
            kwargs.update(data=values)
  
        super().__init__(*args, **kwargs)

    def clean_ingredients(self):
        ingredients = json.loads(self.data.get('ingredients'))

        if len(ingredients) == 0:
            raise forms.ValidationError('A recipe must have at least one ingredient')

        for ingredient in ingredients:
            if ingredient['selectedAmount'] == 0:
                raise forms.ValidationError('All ingredients must have an amount greater than zero')

            try:
                db_ingredient = Ingredient.objects.get(pk=ingredient['id'])
            except:
                raise forms.ValidationError('One or more ingredients were invalid. Please try again.')

            display_unit = Unit.objects.get(pk=ingredient['unit_id'])
            msg = 'You cannot convert between different types of unit: {ingredient} from {unit} to {display_unit}'
            if display_unit.type != db_ingredient.unit.type:
                self.add_error('ingredients', msg.format(**{
                    'ingredient': db_ingredient.name,
                    'unit': db_ingredient.unit.name,
                    'display_unit': display_unit.name,
                }))
            
        return ingredients
    
    def save(self):
        cleaned_data = super().clean()

        name = cleaned_data.get('name')
        ingredients = cleaned_data.get('ingredients')
        directions = cleaned_data.get('directions')
        pk = getattr(self, 'pk', None)

        if name and ingredients and directions:
            if pk:
                recipe = Recipe.objects.get(pk=pk)
                recipe.name = name
                recipe.directions = directions
                recipe.save()

                RecipeIngredient.objects.filter(recipe=recipe).delete()
                recipe.ingredients.clear()
            else:
                recipe = Recipe.objects.create(name=name, directions=directions)
                
            for ingredient in ingredients:
                RecipeIngredient.objects.create(
                    amount=ingredient['selectedAmount'],
                    ingredient_id=ingredient['id'],
                    recipe=recipe,
                    display_unit_id=ingredient['unit_id']
                )
        