from django.contrib import admin
from .models import Food, FoodGroup, PortionSize, FoodLog, MealPlan, MealPlanItem, WeightLog


@admin.register(FoodGroup)
class FoodGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'group', 'kcal_per_100g', 'protein_g']
    list_filter = ['group']
    search_fields = ['name', 'code']


@admin.register(PortionSize)
class PortionSizeAdmin(admin.ModelAdmin):
    list_display = ['food', 'label', 'weight_g']
    search_fields = ['food__name']


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'food', 'meal_type', 'calories', 'date']
    list_filter = ['meal_type', 'date']


@admin.register(WeightLog)
class WeightLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight_kg', 'date']