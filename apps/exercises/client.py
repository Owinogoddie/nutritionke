import random
import requests
from django.conf import settings
from django.utils import timezone

BASE_URL = "https://exercice-api.automately.co.ke/api/v1"
HEADERS = {"x-api-key": settings.EXERCISES_API_KEY}

# Many pools per goal — the day-of-year index picks one deterministically,
# so each day feels fresh without ever being random within a day.
GOAL_POOLS: dict[str, list[dict]] = {
    "lose": [
        {"category": "cardio",      "difficulty": "beginner",     "bodyPart": "cardio"},
        {"category": "cardio",      "difficulty": "beginner",     "bodyPart": "waist"},
        {"category": "cardio",      "difficulty": "intermediate", "bodyPart": "cardio"},
        {"category": "cardio",      "difficulty": "intermediate", "bodyPart": "upper legs"},
        {"category": "plyometrics", "difficulty": "intermediate"},
        {"category": "plyometrics", "difficulty": "advanced"},
        {"category": "cardio",      "difficulty": "beginner",     "bodyPart": "upper legs"},
        {"category": "cardio",      "difficulty": "advanced"},
    ],
    "gain": [
        {"category": "strength", "difficulty": "intermediate", "bodyPart": "chest"},
        {"category": "strength", "difficulty": "intermediate", "bodyPart": "back"},
        {"category": "strength", "difficulty": "intermediate", "bodyPart": "upper legs"},
        {"category": "strength", "difficulty": "intermediate", "bodyPart": "upper arms"},
        {"category": "strength", "difficulty": "intermediate", "bodyPart": "shoulders"},
        {"category": "strength", "difficulty": "advanced",     "bodyPart": "chest"},
        {"category": "strength", "difficulty": "advanced",     "bodyPart": "back"},
        {"category": "strength", "difficulty": "advanced",     "bodyPart": "upper legs"},
        {"category": "strength", "difficulty": "advanced",     "bodyPart": "upper arms"},
        {"category": "strength", "difficulty": "beginner",     "bodyPart": "waist"},   # core day
    ],
    "maintain": [
        {"category": "strength",      "difficulty": "beginner",     "bodyPart": "upper legs"},
        {"category": "strength",      "difficulty": "beginner",     "bodyPart": "chest"},
        {"category": "strength",      "difficulty": "beginner",     "bodyPart": "back"},
        {"category": "strength",      "difficulty": "beginner",     "bodyPart": "upper arms"},
        {"category": "mobility",      "difficulty": "beginner"},
        {"category": "stretching",    "difficulty": "beginner"},
        {"category": "strength",      "difficulty": "intermediate", "bodyPart": "upper legs"},
        {"category": "strength",      "difficulty": "intermediate", "bodyPart": "shoulders"},
        {"category": "balance",       "difficulty": "intermediate"},
        {"category": "strength",      "difficulty": "beginner",     "bodyPart": "waist"},
    ],
    "healthy": [
        {"category": "cardio",        "difficulty": "beginner",     "bodyPart": "cardio"},
        {"category": "stretching",    "difficulty": "beginner"},
        {"category": "mobility",      "difficulty": "beginner"},
        {"category": "cardio",        "difficulty": "beginner",     "bodyPart": "upper legs"},
        {"category": "cardio",        "difficulty": "intermediate", "bodyPart": "cardio"},
        {"category": "rehabilitation","difficulty": "beginner"},
        {"category": "stretching",    "difficulty": "beginner"},
        {"category": "cardio",        "difficulty": "beginner",     "bodyPart": "waist"},
    ],
}


def _todays_pool(goal: str) -> dict:
    """
    Pick a pool using the day-of-year as a stable index.
    Same pool all day long, rotates to the next one tomorrow.
    """
    pools = GOAL_POOLS.get(goal, GOAL_POOLS["maintain"])
    day_index = timezone.localdate().timetuple().tm_yday  # 1-365
    return pools[day_index % len(pools)]


def get_exercises_for_goal(goal: str) -> list:
    pool = _todays_pool(goal)
    params = {**pool, "limit": 6}
    try:
        response = requests.get(
            f"{BASE_URL}/exercises",
            headers=HEADERS,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException:
        return []


def get_exercise_by_id(exercise_id: str) -> dict | None:
    try:
        response = requests.get(
            f"{BASE_URL}/exercises/{exercise_id}",
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None