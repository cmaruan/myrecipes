# MyRecipes

MyRecipes is an app that allows you to know how much you are spending on a recipe given the amount of ingredients used. This app was developed using Django 3, so to use it, you will need a python3 environment. 

There are two options to setup the app:

1. Execute the remote script

    ```bash
    curl -s https://raw.githubusercontent.com/cmaruan/myrecipes/main/install.sh | bash -s
    ``` 

    This script will clone the repository into the current directory, create a virtual environment, install all dependencies and apply all migrations to the database. Currently, SQLite is being used. The script assumes it will be run on a Linux environment with `pip` and `venv` python modules.

    The script also starts the development server provided by django.

2. Installation step-by-step

    First, clone the repository

    ```bash
    $ git clone https://github.com/cmaruan/myrecipes.git myrecipes
    ```
    
    Change the directoty

    ```bash
    cd myrecipes
    ```

    Create a new virtual environtment
     ```bash
    python3 -m venv venv
    ```

    If an error happens, check if you have `venv` installed. On Ubuntu, simply type `sudo apt install python3-venv` to install the package.

    Activate the virtual environtment
     ```bash
    source venv/bin/activate
    ```

    Install the required packages
    
    ```bash
    pip install -r requirements.txt
    ```

    You might need to install pip. On Ubuntu, use `sudo apt install python3-pip`

    Apply all migrations


    ```bash
    python manage.py makemigrations recipes
    python manage.py migrate 
    ```

    This step is optional, but you can load some fixtures about default units.

    ```bash
    python manage.py loaddata recipes/fixtures/units.json
    ```
    Please note that if you are on Windows, you will need to update the path!
    To add other units, you must use the Django Admin.


    
    And start the development server

     ```bash
    python manage.py runserver
    ```

## Security

Please note that Django uses a variable called SECRET_KEY for cryptographic signing. MyRecipe does not provide this value by default. The app tries to find an evironment variable named `DJANGO_SECRET` to use it as the secret key. If it fails, a new one will be generated. However, the app will not remember the previously generated secret key. So it's best if you create one and save it as an environment variable for your system.
By default, My Recipes has `DEBUG` turned off. To turn it on, set the environment variable `DJANGO_DEBUG` to `True`

## Creating new units

The default fixtures create the following units: gram, kilogram, liter, milliliter, centiliter. For extra units, you will need to use the djando admin site. Units are objects that have the follwing fields: 
- `name`: The full name for the unit.
- `short_name`: The abrreviation used for the unit
- `type`: If the unit measures mass, use `m`. For units of volume, use `v`.
- `multiplier`: This number tells MyRecipe how to calculate the proportions between a type of unit. For instance, if the Gram is the default unit, a kilogram must have a multiplier of 1000. If you choose the kilogram as default unit, the gram must have a multiplier of 0.001. The fixtures for units provided with the project use Gram and Liter as default units with multipliers 1.

