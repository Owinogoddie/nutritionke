import random
from datetime import date
from .models import Food, PortionSize, MealPlan, MealPlanItem


# ── Food code groups for each meal slot ───────────────────────────────────────
# These are food codes from your Kenya database grouped by suitability

BREAKFAST_CODES = [
    '15001',  # Uji wa Mahindi
    '15014',  # Finger Millet Porridge
    '15013',  # Cassava Porridge
    '15122',  # Oatmeal
    '15123',  # Oat Porridge
    '15019',  # White Chapati
    '15020',  # Brown Chapati
    '15081',  # Chai ya Maziwa
    '15022',  # Fried Egg
    '15023',  # Omelette
    '01007',  # White Bread
    '01005',  # Brown Bread
]

LUNCH_CODES = [
    '15005',  # Whole Maize Ugali
    '15009',  # Refined Maize Ugali
    '15100',  # Finger Millet Ugali
    '15074',  # Boiled Rice
    '15036',  # Pilau
    '15053',  # Githeri
    '15086',  # Muthokoi
    '15054',  # Mukimo
    '15019',  # Chapati
]

DINNER_CODES = [
    '15005',  # Ugali
    '15009',  # Refined Ugali
    '15074',  # Boiled Rice
    '15075',  # Fried Rice
    '15053',  # Githeri
    '15056',  # Matoke
    '15037',  # Mseto wa Ndengu
    '15038',  # Mseto wa Maharagwe
]

PROTEIN_CODES = [
    '15087',  # Beef Stew
    '15108',  # Stewed Goat Meat
    '15070',  # Stewed Chicken
    '15017',  # Omena Stew
    '15096',  # Fried Tilapia
    '15107',  # Stewed Nile Perch
    '15044',  # Green Gram Stew
    '15045',  # Bean Stew
    '15046',  # Lentil Stew
    '15092',  # Pigeon Peas Stew
]

VEG_CODES = [
    '15031',  # Sukumawiki
    '15032',  # Stir-fried Cabbage
    '15076',  # Stir-fried Spinach
    '15030',  # Terere
    '15039',  # Nderema
]

SNACK_CODES = [
    '05003',  # Avocado
    '05019',  # Mango
    '05004',  # Banana
    '10009',  # Groundnuts
    '15025',  # Meat Samosa
    '15003',  # Kaimati
    '06026',  # Yoghurt
    '05011',  # Guava
]

# Low-GI alternatives for diabetic users
LOW_GI_SWAPS = {
    '15005': '15100',  # Whole maize ugali → Finger millet ugali
    '15009': '15100',  # Refined ugali → Finger millet ugali
    '15074': '15037',  # Boiled rice → Mseto wa Ndengu
    '15036': '15053',  # Pilau → Githeri
}

# Low-sodium proteins for hypertension
LOW_SODIUM_PROTEINS = [
    '15087',  # Beef Stew (homemade)
    '15108',  # Stewed Goat
    '15070',  # Stewed Chicken
    '15044',  # Green Gram Stew
    '15045',  # Bean Stew
    '15046',  # Lentil Stew
]


def get_default_portion(food):
    """Get the medium/standard portion for a food, fallback to 100g."""
    portion = food.portions.filter(
        label__icontains='medium'
    ).first() or food.portions.filter(
        label__icontains='standard'
    ).first() or food.portions.first()
    return portion


def calc_nutrition(food, weight_g):
    """Return dict of nutrition for a given weight."""
    return {
        'calories': round((food.kcal_per_100g * weight_g) / 100, 1),
        'protein': round((food.protein_g * weight_g) / 100, 1),
        'carbs': round((food.carbs_g * weight_g) / 100, 1),
        'fat': round((food.fat_g * weight_g) / 100, 1),
    }


def apply_health_swaps(codes, user):
    """Swap foods based on health conditions."""
    result = []
    for code in codes:
        if user.has_diabetes and code in LOW_GI_SWAPS:
            result.append(LOW_GI_SWAPS[code])
        else:
            result.append(code)
    return result


def pick_food(codes):
    """Randomly pick one food from a list of codes, skip missing."""
    random.shuffle(codes)
    for code in codes:
        try:
            return Food.objects.get(code=code)
        except Food.DoesNotExist:
            continue
    return None


def generate_meal_plan(user, target_date=None):
    """
    Generate a full day meal plan for the user.
    Returns a MealPlan object with all items attached.
    """
    if target_date is None:
        target_date = date.today()

    # Delete existing plan for this date if regenerating
    MealPlan.objects.filter(user=user, date=target_date).delete()

    calorie_target = user.daily_calorie_target or 2000

    # Calorie split: breakfast 25%, lunch 35%, dinner 30%, snack 10%
    targets = {
        'breakfast': calorie_target * 0.25,
        'lunch': calorie_target * 0.35,
        'dinner': calorie_target * 0.30,
        'snack': calorie_target * 0.10,
    }

    plan = MealPlan.objects.create(user=user, date=target_date)
    items = []

    # ── BREAKFAST ─────────────────────────────────────────────────────────────
    b_codes = apply_health_swaps(BREAKFAST_CODES.copy(), user)
    b_main = pick_food(b_codes)

    if b_main:
        portion = get_default_portion(b_main)
        weight = portion.weight_g if portion else 250
        nutrition = calc_nutrition(b_main, weight)
        items.append(MealPlanItem(
            meal_plan=plan,
            food=b_main,
            portion=portion,
            meal_type='breakfast',
            weight_g=weight,
            **nutrition,
        ))

    # ── LUNCH ─────────────────────────────────────────────────────────────────
    # Carb base
    l_codes = apply_health_swaps(LUNCH_CODES.copy(), user)
    l_carb = pick_food(l_codes)

    # Protein side
    p_codes = LOW_SODIUM_PROTEINS.copy() if user.has_hypertension else PROTEIN_CODES.copy()
    l_protein = pick_food(p_codes)

    # Vegetable side
    l_veg = pick_food(VEG_CODES.copy())

    for food, meal_type in [(l_carb, 'lunch'), (l_protein, 'lunch'), (l_veg, 'lunch')]:
        if food:
            portion = get_default_portion(food)
            weight = portion.weight_g if portion else 150
            nutrition = calc_nutrition(food, weight)
            items.append(MealPlanItem(
                meal_plan=plan,
                food=food,
                portion=portion,
                meal_type=meal_type,
                weight_g=weight,
                **nutrition,
            ))

    # ── DINNER ────────────────────────────────────────────────────────────────
    # Avoid repeating lunch carb
    d_codes = [c for c in DINNER_CODES if c != getattr(l_carb, 'code', None)]
    d_codes = apply_health_swaps(d_codes, user)
    d_carb = pick_food(d_codes)

    # Different protein from lunch
    d_p_codes = [c for c in p_codes if c != getattr(l_protein, 'code', None)]
    d_protein = pick_food(d_p_codes)

    # Different veg from lunch
    d_v_codes = [c for c in VEG_CODES if c != getattr(l_veg, 'code', None)]
    d_veg = pick_food(d_v_codes) or l_veg

    for food in [d_carb, d_protein, d_veg]:
        if food:
            portion = get_default_portion(food)
            weight = portion.weight_g if portion else 150
            nutrition = calc_nutrition(food, weight)
            items.append(MealPlanItem(
                meal_plan=plan,
                food=food,
                portion=portion,
                meal_type='dinner',
                weight_g=weight,
                **nutrition,
            ))

    # ── SNACK ─────────────────────────────────────────────────────────────────
    snack = pick_food(SNACK_CODES.copy())
    if snack:
        portion = get_default_portion(snack)
        weight = portion.weight_g if portion else 100
        nutrition = calc_nutrition(snack, weight)
        items.append(MealPlanItem(
            meal_plan=plan,
            food=snack,
            portion=portion,
            meal_type='snack',
            weight_g=weight,
            **nutrition,
        ))

    # ── Save all items ─────────────────────────────────────────────────────────
    MealPlanItem.objects.bulk_create(items)

    # Update plan totals
    all_items = MealPlanItem.objects.filter(meal_plan=plan)
    plan.total_calories = round(sum(i.calories for i in all_items))
    plan.total_protein = round(sum(i.protein for i in all_items), 1)
    plan.total_carbs = round(sum(i.carbs for i in all_items), 1)
    plan.total_fat = round(sum(i.fat for i in all_items), 1)
    plan.save()

    return plan