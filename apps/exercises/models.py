from django.db import models
from django.conf import settings


class WorkoutLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workout_logs",
    )
    exercise_id = models.CharField(max_length=20)
    exercise_name = models.CharField(max_length=200)
    body_part = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=10)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-logged_at"]

    def __str__(self):
        return f"{self.user} — {self.exercise_name} on {self.date}"