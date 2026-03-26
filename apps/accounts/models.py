from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model. Registration only needs name, email, password.
    Everything else is filled in later via the profile setup flow.
    """
    email = models.EmailField(unique=True)

    # Profile fields — filled in after registration
    date_of_birth = models.DateField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)

    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (1-3 days/week)'),
        ('moderate', 'Moderately active (3-5 days/week)'),
        ('very_active', 'Very active (6-7 days/week)'),
        ('extra_active', 'Extra active (physical job + exercise)'),
    ]
    activity_level = models.CharField(
        max_length=20, choices=ACTIVITY_CHOICES,
        default='sedentary', null=True, blank=True
    )

    GOAL_CHOICES = [
        ('lose', 'Lose Weight'),
        ('gain', 'Gain Weight'),
        ('maintain', 'Maintain Weight'),
        ('healthy', 'Eat Healthier'),
    ]
    goal = models.CharField(
        max_length=10, choices=GOAL_CHOICES,
        null=True, blank=True
    )

    # Health conditions (multiple allowed)
    has_diabetes = models.BooleanField(default=False)
    has_hypertension = models.BooleanField(default=False)
    has_obesity = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)

    # Calculated fields (updated whenever profile changes)
    daily_calorie_target = models.IntegerField(null=True, blank=True)
    daily_protein_target = models.IntegerField(null=True, blank=True)
    daily_carbs_target = models.IntegerField(null=True, blank=True)
    daily_fat_target = models.IntegerField(null=True, blank=True)

    profile_complete = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def calculate_targets(self):
        """
        Calculate BMR using Mifflin-St Jeor equation,
        then apply activity multiplier and goal adjustment.
        """
        if not all([self.weight_kg, self.height_cm, self.date_of_birth, self.sex]):
            return

        from datetime import date
        age = (date.today() - self.date_of_birth).days // 365

        weight = float(self.weight_kg)
        height = float(self.height_cm)

        # BMR
        if self.sex == 'M':
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # Activity multiplier
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9,
        }
        tdee = bmr * multipliers.get(self.activity_level, 1.2)

        # Goal adjustment
        goal_adjustments = {
            'lose': -500,
            'gain': +500,
            'maintain': 0,
            'healthy': 0,
        }
        calories = tdee + goal_adjustments.get(self.goal, 0)
        self.daily_calorie_target = round(calories)

        # Macro split
        self.daily_protein_target = round((calories * 0.25) / 4)
        self.daily_carbs_target = round((calories * 0.45) / 4)
        self.daily_fat_target = round((calories * 0.30) / 9)

    def save(self, *args, **kwargs):
        self.calculate_targets()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email