# Generated by Django 3.1.7 on 2021-03-17 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_unit_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeingredient',
            name='unit_cost',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
