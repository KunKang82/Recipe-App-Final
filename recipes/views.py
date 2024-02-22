from django.shortcuts import render                         #imported by default
from django.views.generic import ListView, DetailView       #to display lists
from .models import Recipe                                  #to access recipe model
from django.contrib.auth.mixins import LoginRequiredMixin   #to protect class-based view
from django.contrib.auth.decorators import login_required   #to protect function-based view
from .forms import RecipesSearchForm, CreateRecipeForm
import pandas as pd
from .utils import get_recipename_from_id, get_chart

from django.db.models import Q  # Import Q object for comples queries

# Create your views here.
def recipes_home(request):
    return render(request, 'recipes/recipes_home.html')

class RecipeListView(LoginRequiredMixin, ListView):         #class-based view
    model = Recipe                                            #specify model
    template_name = 'recipes/main.html'                       #specity template

class RecipeDetailView(LoginRequiredMixin, DetailView):     #class-based view
    model = Recipe                                            #specify model
    template_name = 'recipes/detail.html'                     #specify template

#define function-based view - records(request)  
#keep protected
@login_required
def records(request):
    # Initialize the search form
    form = RecipesSearchForm(request.POST or None)
    recipes_df = None
    chart = None
    qs = Recipe.objects.none()  # Initialize with an empty queryset

    if request.method == 'POST':
        # Retrieve input values from the form
        recipe_name = request.POST.get('recipe_name')
        ingredients = request.POST.get('ingredients')
        recipe_diff = request.POST.get('recipe_diff')
        chart_type = request.POST.get('chart_type')

        try:
            # Use Q objects for complex queries
            q_objects = Q()

            # If recipe_name is provided, add a filter for name containing the input
            if recipe_name:
                q_objects |= Q(name__icontains=recipe_name)
            # If ingredients is provided, add a filter for ingredients containing the input
            if ingredients:
                q_objects |= Q(ingredients__icontains=ingredients)
            # If recipe_diff is provided, add a filter for difficulty matching the input
            if recipe_diff:
                q_objects |= Q(difficulty=recipe_diff)

            # Filter recipes based on the constructed query
            qs = Recipe.objects.filter(q_objects)
            
            if qs.exists():
                # Convert the queryset to a DataFrame for further processing
                recipes_df = pd.DataFrame(qs.values())

                # Generate a chart based on the selected chart type
                chart = get_chart(chart_type, recipes_df, labels=recipes_df['name'].values)
                                
                # Convert DataFrame to HTML for rendering in the template
                recipes_df = recipes_df.to_html()

                # Print recipes_df to check its content
                print("recipes_df content:")
                print(recipes_df)

            # Debug output
            print("recipes_df:")
            print(recipes_df)
            print("qs:")
            print(qs)

        except Exception as e:
            # Print an error message if an exception occurs during processing
            print(f"Error: {str(e)}")

    # Prepare the context to be passed to the template
    context = {
        'form': form,
        'recipes_df': recipes_df,
        'recipes': qs,
        'chart': chart,
    }

    # Render the template with the provided context
    return render(request, 'recipes/records.html', context)

@login_required
def create_view(request):
    create_form = CreateRecipeForm(request.POST or None, request.FILES)
    name = None
    cooking_time = None
    difficulty = None
    ingredients = None
    pic = None

    if request.method == 'POST':

        try:
            recipe = Recipe.objects.create(
                name = request.POST.get('name'),
                cooking_time = request.POST.get('cooking_time'),
                difficulty = request.POST.get('difficulty'),
                ingredients = request.POST.get('ingredients'),
                pic = request.POST.get('pic')
            )

            recipe.save()

        except:
            print('Error!!!')

    context = {
        'create_form': create_form,
        'name': name,
        'cooking_time': cooking_time,
        'difficulty': difficulty,
        'ingredients': ingredients,
        'pic': pic
    }

    return render(request, 'recipes/create.html', context)