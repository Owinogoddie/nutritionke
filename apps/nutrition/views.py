from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Food, PortionSize, FoodLog, MealPlan, MealPlanItem, WeightLog
from .meal_engine import generate_meal_plan


@login_required
def meal_plan(request):
    user = request.user
    today = timezone.localdate()

    # Regenerate if requested
    if request.method == 'POST' and request.POST.get('action') == 'regenerate':
        plan = generate_meal_plan(user, today)
        return redirect('nutrition:meal_plan')

    # Get or generate today's plan
    try:
        plan = MealPlan.objects.prefetch_related(
            'items__food', 'items__portion'
        ).get(user=user, date=today)
    except MealPlan.DoesNotExist:
        if not user.profile_complete:
            return render(request, 'nutrition/meal_plan_setup_prompt.html')
        plan = generate_meal_plan(user, today)

    # Group items by meal type
    meals = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'snack': [],
    }
    for item in plan.items.all():
        meals[item.meal_type].append(item)

    context = {
        'plan': plan,
        'meals': meals,
        'today': today,
        'calorie_target': user.daily_calorie_target or 2000,
    }
    return render(request, 'nutrition/meal_plan.html', context)


@login_required
def log_from_plan(request):
    """Log an entire meal plan item directly to food log."""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = MealPlanItem.objects.get(id=item_id, meal_plan__user=request.user)
            FoodLog.objects.create(
                user=request.user,
                food=item.food,
                portion=item.portion,
                meal_type=item.meal_type,
                weight_g=item.weight_g,
                calories=item.calories,
                protein=item.protein,
                carbs=item.carbs,
                fat=item.fat,
                date=timezone.localdate(),
            )
        except MealPlanItem.DoesNotExist:
            pass
    return redirect('nutrition:meal_plan')


@login_required
def food_log(request):
    user = request.user
    today = timezone.localdate()

    if request.method == 'POST':
        food_id = request.POST.get('food_id')
        portion_id = request.POST.get('portion_id')
        meal_type = request.POST.get('meal_type', 'lunch')
        custom_weight = request.POST.get('custom_weight')

        try:
            food = Food.objects.get(id=food_id)

            if portion_id:
                portion = PortionSize.objects.get(id=portion_id)
                weight = portion.weight_g
            else:
                weight = float(custom_weight or 100)
                portion = None

            calories = (food.kcal_per_100g * weight) / 100
            protein = (food.protein_g * weight) / 100
            carbs = (food.carbs_g * weight) / 100
            fat = (food.fat_g * weight) / 100

            FoodLog.objects.create(
                user=user,
                food=food,
                portion=portion,
                meal_type=meal_type,
                weight_g=weight,
                calories=round(calories, 1),
                protein=round(protein, 1),
                carbs=round(carbs, 1),
                fat=round(fat, 1),
                date=today,
            )
            return redirect('nutrition:food_log')

        except (Food.DoesNotExist, ValueError):
            pass

    logs = FoodLog.objects.filter(user=user, date=today)
    total_calories = sum(l.calories for l in logs)

    return render(request, 'nutrition/food_log.html', {
        'logs': logs,
        'today': today,
        'total_calories': round(total_calories),
        'calorie_target': user.daily_calorie_target or 2000,
    })


@login_required
def food_search(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        foods = Food.objects.filter(
            Q(name__icontains=query)
        ).select_related('group')[:15]

        results = [{
            'id': f.id,
            'name': f.name,
            'group': f.group.name if f.group else '',
            'kcal': f.kcal_per_100g,
        } for f in foods]
        return JsonResponse({'results': results})

    return JsonResponse({'results': []})


@login_required
def get_portions(request, food_id):
    portions = PortionSize.objects.filter(food_id=food_id)
    data = [{
        'id': p.id,
        'label': p.label,
        'weight_g': p.weight_g,
        'description': p.description,
    } for p in portions]
    return JsonResponse({'portions': data})


@login_required
def log_weight(request):
    if request.method == 'POST':
        weight = request.POST.get('weight_kg')
        note = request.POST.get('note', '')
        try:
            WeightLog.objects.update_or_create(
                user=request.user,
                date=timezone.localdate(),
                defaults={
                    'weight_kg': float(weight),
                    'note': note,
                }
            )
        except (ValueError, TypeError):
            pass
    return redirect('dashboard:progress')