from django.urls import path
from . import views

app_name = "exercises"

urlpatterns = [
    path("workout-plan/", views.workout_plan, name="workout_plan"),
    # path("workout/shuffle/", views.shuffle_workout, name="shuffle_workout"),
    path("log-exercise/", views.log_exercise, name="log_exercise"),
    path("history/", views.workout_history, name="workout_history"),
    # path("debug/", views.debug_exercises, name="debug_exercises"),
    path("<str:exercise_id>/", views.exercise_detail, name="exercise_detail"),  # always last
]