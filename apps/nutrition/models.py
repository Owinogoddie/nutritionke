from django.db import models
from django.conf import settings


class FoodGroup(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Food(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(FoodGroup, on_delete=models.SET_NULL, null=True)
    kcal_per_100g = models.FloatField()
    protein_g = models.FloatField()
    fat_g = models.FloatField()
    carbs_g = models.FloatField()
    fibre_g = models.FloatField()

    def __str__(self):
        return self.name

    def calories_for_weight(self, weight_g):
        return round((self.kcal_per_100g * weight_g) / 100, 1)

    def protein_for_weight(self, weight_g):
        return round((self.protein_g * weight_g) / 100, 1)


class PortionSize(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='portions')
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    weight_g = models.FloatField()
    typical_use = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.food.name} — {self.label} ({self.weight_g}g)"


class MealPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    total_calories = models.IntegerField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.email} — {self.date}"


class MealPlanItem(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    portion = models.ForeignKey(PortionSize, on_delete=models.SET_NULL, null=True)
    meal_type = models.CharField(max_length=15, choices=MEAL_CHOICES)
    weight_g = models.FloatField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    def __str__(self):
        return f"{self.meal_type}: {self.food.name}"


class FoodLog(models.Model):
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    portion = models.ForeignKey(PortionSize, on_delete=models.SET_NULL, null=True, blank=True)
    meal_type = models.CharField(max_length=15, choices=MEAL_CHOICES)
    weight_g = models.FloatField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()
    date = models.DateField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.email} — {self.food.name} ({self.date})"


class WeightLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1)
    date = models.DateField()
    note = models.CharField(max_length=200, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.email} — {self.weight_kg}kg on {self.date}"