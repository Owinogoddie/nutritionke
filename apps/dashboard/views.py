import json
from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum

from apps.nutrition.models import FoodLog, WeightLog, MealPlan


@login_required
def home(request):
    user = request.user
    today = timezone.localdate()

    logs = FoodLog.objects.filter(user=user, date=today)
    consumed_calories = sum(log.calories for log in logs)
    consumed_protein  = sum(log.protein  for log in logs)
    consumed_carbs    = sum(log.carbs    for log in logs)
    consumed_fat      = sum(log.fat      for log in logs)

    calorie_target = user.daily_calorie_target or 2000
    protein_target = user.daily_protein_target or 50
    carbs_target   = user.daily_carbs_target   or 250
    fat_target     = user.daily_fat_target     or 65

    def pct(consumed, target):
        if not target:
            return 0
        return min(round((consumed / target) * 100), 100)

    # 7-day calorie trend
    seven_days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_logs = FoodLog.objects.filter(user=user, date=day)
        day_cals  = round(sum(l.calories for l in day_logs))
        seven_days.append({
            'date': day.strftime('%a'),
            'calories': day_cals,
        })

    context = {
        'today': today,
        'consumed_calories': round(consumed_calories),
        'consumed_protein':  round(consumed_protein, 1),
        'consumed_carbs':    round(consumed_carbs,   1),
        'consumed_fat':      round(consumed_fat,     1),
        'calorie_target': calorie_target,
        'protein_target': protein_target,
        'carbs_target':   carbs_target,
        'fat_target':     fat_target,
        'calorie_pct': pct(consumed_calories, calorie_target),
        'protein_pct': pct(consumed_protein,  protein_target),
        'carbs_pct':   pct(consumed_carbs,    carbs_target),
        'fat_pct':     pct(consumed_fat,      fat_target),
        'remaining_calories': max(calorie_target - round(consumed_calories), 0),
        'logs': logs,
        'latest_weight': WeightLog.objects.filter(user=user).order_by('-date').first(),
        'seven_days_json': json.dumps(seven_days),
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def progress(request):
    user = request.user
    today = timezone.localdate()
    thirty_days_ago = today - timedelta(days=29)

    # Weight logs (oldest → newest for chart)
    weight_logs = WeightLog.objects.filter(user=user).order_by('date')[:30]
    latest_weight = weight_logs.last()

    # Calorie logs per day for last 30 days
    calorie_target = user.daily_calorie_target or 2000
    calorie_rows = []
    logged_days  = 0
    total_cals   = 0

    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        day_logs = FoodLog.objects.filter(user=user, date=day)
        day_cals = round(sum(l.calories for l in day_logs))
        calorie_rows.append({
            'date':     day.strftime('%-d %b'),
            'calories': day_cals,
            'target':   calorie_target,
        })
        if day_cals > 0:
            logged_days += 1
            total_cals  += day_cals

    avg_calories = round(total_cals / logged_days) if logged_days else 0

    weight_data = [
        {'date': w.date.strftime('%-d %b'), 'weight': float(w.weight_kg)}
        for w in weight_logs
    ]

    context = {
        'weight_logs':       weight_logs,
        'latest_weight':     latest_weight,
        'logged_days':       logged_days,
        'avg_calories':      avg_calories,
        'calorie_data_json': json.dumps(calorie_rows),
        'weight_data_json':  json.dumps(weight_data),
    }
    return render(request, 'dashboard/progress.html', context)


@login_required
def tips(request):
    user = request.user
    tips_list = get_tips_for_user(user)
    return render(request, 'dashboard/tips.html', {'tips': tips_list})


def get_tips_for_user(user):
    tips = []

    if user.goal == 'lose':
        tips.append({
            'icon': '🔥',
            'title': 'Calorie Deficit',
            'body': 'You are eating 500 kcal below your maintenance. At this rate you can expect to lose about 0.5 kg per week.',
            'color': 'orange',
        })
        tips.append({
            'icon': '🥬',
            'title': 'Fill up on vegetables',
            'body': 'Sukuma wiki, spinach, and cabbage are very low in calories but filling. Pile them on your plate first.',
            'color': 'green',
        })

    elif user.goal == 'gain':
        tips.append({
            'icon': '💪',
            'title': 'Calorie Surplus',
            'body': 'Eat 500 kcal above your maintenance daily. Focus on protein-rich foods like eggs, beans, and lean meat.',
            'color': 'blue',
        })
        tips.append({
            'icon': '🥑',
            'title': 'Healthy calorie density',
            'body': 'Add avocado, groundnuts, and whole milk to your meals. They add calories without large volumes.',
            'color': 'green',
        })

    if user.has_diabetes:
        tips.append({
            'icon': '🩺',
            'title': 'Diabetes: Watch your carbs',
            'body': 'Choose finger millet ugali or whole grain options over refined maize ugali. They raise blood sugar more slowly.',
            'color': 'red',
        })
        tips.append({
            'icon': '🫘',
            'title': 'Beans are your friend',
            'body': 'Beans, lentils, and green grams have a low glycaemic index and help keep blood sugar stable.',
            'color': 'amber',
        })

    if user.has_hypertension:
        tips.append({
            'icon': '❤️',
            'title': 'Reduce salt intake',
            'body': 'Cook with less salt and avoid adding table salt. Use lemon juice, coriander, and spices for flavour instead.',
            'color': 'red',
        })

    if user.date_of_birth:
        age = (date.today() - user.date_of_birth).days // 365
        if age >= 60:
            tips.append({
                'icon': '🦴',
                'title': 'Bone Health',
                'body': 'At your age, calcium and vitamin D are crucial. Include milk, yoghurt, and dark leafy greens daily.',
                'color': 'blue',
            })
        elif age <= 19:
            tips.append({
                'icon': '🌱',
                'title': 'Growing strong',
                'body': 'You need more iron and calcium for growth. Eat dark greens, beans, eggs, and drink milk regularly.',
                'color': 'green',
            })

    if user.is_pregnant:
        tips.append({
            'icon': '🤰',
            'title': 'Pregnancy nutrition',
            'body': 'You need extra folate, iron, and protein. Include eggs, dark leafy greens, beans, and liver regularly.',
            'color': 'pink',
        })

    if not tips:
        tips.append({
            'icon': '💧',
            'title': 'Stay hydrated',
            'body': 'Drink at least 8 glasses of water daily. Start your morning with a glass before chai.',
            'color': 'blue',
        })

    return tips