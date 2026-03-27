import random
import requests
from django.conf import settings

BASE_URL = "https://exercice-api.automately.co.ke/api/v1"
HEADERS = {"x-api-key": settings.EXERCISES_API_KEY}

# Each goal maps to a list of param pools.
# On every call one pool is picked at random, then a random offset is applied
# so repeated calls return different slices of the exercise catalogue.
#
# Pool keys mirror the API's query params:
#   category   – cardio | strength | plyometrics | mobility | balance |
#                stretching | rehabilitation
#   difficulty – beginner | intermediate | advanced
#   bodyPart   – back | cardio | chest | lower arms | lower legs | neck |
#                shoulders | upper arms | upper legs | waist   (optional)
#   limit      – how many exercises to fetch in one call

GOAL_POOLS: dict[str, list[dict]] = {
    # Lose weight → cardio-heavy, some plyometrics for variety
    "lose": [
        {"category": "cardio",      "difficulty": "beginner",     "limit": 8},
        {"category": "cardio",      "difficulty": "intermediate",  "limit": 8},
        {"category": "plyometrics", "difficulty": "intermediate",  "limit": 6},
        {"category": "cardio",      "difficulty": "advanced",      "limit": 6},
        {"category": "plyometrics", "difficulty": "advanced",      "limit": 6},
    ],

    # Gain muscle → strength at every difficulty, varied body-part focus
    "gain": [
        {"category": "strength", "difficulty": "intermediate", "limit": 8},
        {"category": "strength", "difficulty": "intermediate", "limit": 8, "bodyPart": "upper legs"},
        {"category": "strength", "difficulty": "intermediate", "limit": 8, "bodyPart": "back"},
        {"category": "strength", "difficulty": "intermediate", "limit": 8, "bodyPart": "chest"},
        {"category": "strength", "difficulty": "advanced",     "limit": 8},
        {"category": "strength", "difficulty": "advanced",     "limit": 8, "bodyPart": "upper arms"},
        {"category": "strength", "difficulty": "beginner",     "limit": 6},  # deload days
    ],

    # Maintain → moderate strength + mobility mix
    "maintain": [
        {"category": "strength",  "difficulty": "beginner",     "limit": 6},
        {"category": "strength",  "difficulty": "intermediate",  "limit": 6},
        {"category": "mobility",  "difficulty": "beginner",     "limit": 5},
        {"category": "stretching","difficulty": "beginner",     "limit": 5},
        {"category": "balance",   "difficulty": "intermediate",  "limit": 4},
    ],

    # General health → light cardio, stretching, mobility
    "healthy": [
        {"category": "cardio",    "difficulty": "beginner",     "limit": 6},
        {"category": "stretching","difficulty": "beginner",     "limit": 6},
        {"category": "mobility",  "difficulty": "beginner",     "limit": 6},
        {"category": "cardio",    "difficulty": "intermediate",  "limit": 5},
        {"category": "rehabilitation","difficulty": "beginner",  "limit": 4},
    ],
}

# Approximate pool sizes per (category, difficulty) so we can stay within bounds.
# Values are conservative estimates taken from the scraped dataset.
_POOL_SIZES: dict[tuple[str, str], int] = {
    ("cardio",       "beginner"):     23,
    ("cardio",       "intermediate"):  8,
    ("cardio",       "advanced"):      3,
    ("plyometrics",  "intermediate"):  6,
    ("plyometrics",  "advanced"):     11,
    ("strength",     "beginner"):    459,
    ("strength",     "intermediate"):569,
    ("strength",     "advanced"):    152,
    ("mobility",     "beginner"):     29,
    ("stretching",   "beginner"):     52,
    ("balance",      "intermediate"):  4,
    ("rehabilitation","beginner"):     4,
}


def _random_page(params: dict) -> int:
    """Return a random page that stays within the pool."""
    key = (params["category"], params["difficulty"])
    pool_size = _POOL_SIZES.get(key, params["limit"] * 2)
    max_page = max(1, pool_size // params["limit"])
    return random.randint(1, max_page)


def get_exercises_for_goal(goal: str) -> list:
    pools = GOAL_POOLS.get(goal, GOAL_POOLS["maintain"])
    params = dict(random.choice(pools))
    params["page"] = _random_page(params)   # ← page instead of offset

    print(f"[exercises] fetching goal={goal} params={params}")

    try:
        response = requests.get(
            f"{BASE_URL}/exercises",
            headers=HEADERS,
            params=params,
            timeout=10,
        )
        print(f"[exercises] status={response.status_code}")
        response.raise_for_status()
        data = response.json().get("data", [])
        print(f"[exercises] returned {len(data)} exercises")
        random.shuffle(data)
        return data
    except requests.RequestException as e:
        print(f"[exercises] ERROR: {e}")
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