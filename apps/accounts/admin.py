from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'goal', 'profile_complete', 'daily_calorie_target']
    list_filter = ['goal', 'profile_complete', 'has_diabetes', 'has_hypertension']
    fieldsets = UserAdmin.fieldsets + (
        ('Health Profile', {
            'fields': (
                'date_of_birth', 'sex', 'weight_kg', 'height_cm',
                'activity_level', 'goal', 'has_diabetes',
                'has_hypertension', 'has_obesity', 'is_pregnant',
                'daily_calorie_target', 'profile_complete',
            )
        }),
    )