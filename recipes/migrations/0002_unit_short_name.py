# Generated by Django 3.1.7 on 2021-03-17 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='short_name',
            field=models.CharField(default='', max_length=3),
            preserve_default=False,
        ),
    ]
