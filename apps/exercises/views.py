import hashlib

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone

from .client import get_exercises_for_goal, get_exercise_by_id
from .models import WorkoutLog


def _daily_cache_key(user_id: int, goal: str, date) -> str:
    """
    One stable cache key per user per goal per calendar day.
    Including goal means a goal change mid-day gets a fresh fetch.
    """
    raw = f"workout:{user_id}:{goal}:{date}"
    return hashlib.md5(raw.encode()).hexdigest()


def _seconds_until_midnight() -> int:
    """Cache TTL that expires at local midnight so tomorrow auto-refreshes."""
    now = timezone.localtime()
    from datetime import datetime, timedelta
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(60, int((midnight - now).total_seconds()))


@login_required
def workout_plan(request):
    user  = request.user
    today = timezone.localdate()

    if not user.profile_complete:
        return render(request, "exercises/workout_plan_setup_prompt.html")

    goal      = user.goal or "maintain"
    cache_key = _daily_cache_key(user.id, goal, today)

    exercises = cache.get(cache_key)
    if exercises is None:
        exercises = get_exercises_for_goal(goal)
        cache.set(cache_key, exercises, timeout=_seconds_until_midnight())

    mid     = len(exercises) // 2
    morning = exercises[:mid]
    evening = exercises[mid:]

    logged_ids = set(
        WorkoutLog.objects.filter(user=user, date=today)
        .values_list("exercise_id", flat=True)
    )

    context = {
        "exercises":  exercises,
        "morning":    morning,
        "evening":    evening,
        "logged_ids": logged_ids,
        "remaining":  sum(1 for ex in exercises if ex["id"] not in logged_ids),
        "today":      today,
        "goal_label": user.get_goal_display(),
    }
    return render(request, "exercises/workout_plan.html", context)


@login_required
def log_exercise(request):
    if request.method == "POST":
        today         = timezone.localdate()
        exercise_id   = request.POST.get("exercise_id")
        exercise_name = request.POST.get("exercise_name")
        body_part     = request.POST.get("body_part", "")
        category      = request.POST.get("category", "")
        sets          = int(request.POST.get("sets", 3))
        reps          = int(request.POST.get("reps", 10))

        WorkoutLog.objects.get_or_create(
            user=request.user,
            exercise_id=exercise_id,
            date=today,
            defaults={
                "exercise_name": exercise_name,
                "body_part":     body_part,
                "category":      category,
                "sets":          sets,
                "reps":          reps,
            },
        )
    return redirect("exercises:workout_plan")


@login_required
def workout_history(request):
    logs = WorkoutLog.objects.filter(user=request.user).order_by("-date")[:30]
    return render(request, "exercises/workout_history.html", {"logs": logs})


@login_required
def exercise_detail(request, exercise_id):
    exercise = get_exercise_by_id(exercise_id)
    if not exercise:
        raise Http404("Exercise not found")
    return render(request, "exercises/exercise_detail.html", {"exercise": exercise})