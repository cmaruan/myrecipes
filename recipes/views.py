from django.views import generic
from django.views.generic.edit import FormMixin
from django.shortcuts import redirect, reverse, get_object_or_404
from django.db.models import F, Q
import json

from .models import Ingredient, Recipe, Unit
from .forms import CreateIngredientForm, UpdateIngredientForm, RecipeForm
from . import utils

class IngredientListView(generic.TemplateView):
    template_name = 'recipes/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = utils.MODULES_INFO
        query = Q(disabled=False)
        search = self.request.GET.get('search')
        if search:
            query &= Q(name__icontains=search) | Q(article_number__icontains=search)
            context['search'] = search
        context['items'] = Ingredient.objects.filter(query)
        context['module']['active'] = 'ingredients'
        return context
    
    
    

class RecipeListView(generic.TemplateView):
    template_name = 'recipes/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = utils.MODULES_INFO
        search = self.request.GET.get('search')
        if search:
            context['items'] = Recipe.objects.filter(name__icontains=search)
            context['search'] = search
        else:
            context['items'] = Recipe.objects.all()
        context['module']['active'] = 'recipes'
        return context
    

class IngredientUpdateView(generic.UpdateView, ):
    model = Ingredient
    form_class = UpdateIngredientForm
    context_object_name = 'ingredient'
    template_name = 'recipes/ingredient_form.html'

    def get_success_url(self):
        return reverse('ingredient-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = utils.MODULES_INFO
        context['module']['active'] = 'ingredients'
        return context

    def get_queryset(self):
        return Ingredient.objects.filter(disabled=False)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'delete' in request.POST:
            instance.disabled = True
            instance.save()
        elif 'save' in request.POST:
            return super().post(request, *args, **kwargs)
        return redirect(reverse('ingredient-list'))


class RecipeView(generic.FormView):
    template_name = 'recipes/recipe_form.html'
    form_class = RecipeForm

    def get_success_url(self):
        return reverse('recipe-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = utils.MODULES_INFO
        context['module']['active'] = 'recipes'
        context['ingredients'] = Ingredient.objects.all()
        context['units'] = Unit.objects.all()
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        POST = dict(self.request.POST)
        kwargs['name'] = getattr(POST, 'name', None)
        kwargs['ingredients'] = getattr(POST, 'ingredients', None)

        return kwargs

class RecipeUpdateView(RecipeView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        self.object = recipe
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        pk = kwargs['pk']
        recipe = get_object_or_404(Recipe, pk=pk)
        self.object = recipe
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.object.pk
        return kwargs



class RecipeCreateView(RecipeView):
    pass
    


class MyRecipesView(generic.TemplateView):
    template_name = 'recipes/main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        submodule = request.GET.get('submodule', 'ingredients')
        context["module"] = utils.MODULES_INFO
    
        if submodule == 'ingredients':
            queryset = Ingredient.objects.filter(disabled=False)
        elif submodule == 'recipes':
            queryset = Recipe.objects.all()
        else:
            queryset = []
        context['items'] = queryset
        context['module']['active'] = submodule
        return self.render_to_response(context)

class IngredientCreateView(generic.CreateView):
    model = Ingredient
    form_class = CreateIngredientForm
    template_name = 'recipes/ingredient_form.html'

    def get_success_url(self):
        return reverse('homepage')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["module"] = utils.MODULES_INFO
        context['module']['active'] = 'ingredients'
        return context

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)