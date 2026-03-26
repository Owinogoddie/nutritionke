from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('meal-plan/', views.meal_plan, name='meal_plan'),
    path('meal-plan/log-item/', views.log_from_plan, name='log_from_plan'),
    path('food-log/', views.food_log, name='food_log'),
    path('food-search/', views.food_search, name='food_search'),
    path('portions/<int:food_id>/', views.get_portions, name='get_portions'),
    path('log-weight/', views.log_weight, name='log_weight'),
]