from django.db.models.signals import pre_save
from django.dispatch import receiver
from . import models


@receiver(pre_save, sender=models.RecipeIngredient)
def calculate_amount_to_show(sender, instance, **kwargs):
    ingredient = instance.ingredient
    cost = ingredient.cost
    amount = ingredient.amount
    multiplier = ingredient.unit.multiplier

    instance.unit_cost = cost / (multiplier * amount)
    
