#!/usr/bin/bash

git clone https://github.com/cmaruan/myrecipes.git myrecipes
cd myrecipes
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations recipes
python manage.py migrate
python manage.py loaddata recipes/fixtures/units.json
python manage.py runserver