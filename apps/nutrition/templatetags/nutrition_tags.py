from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.simple_tag
def meal_slots():
    return [
        ('breakfast', 'Breakfast', '🌅'),
        ('lunch', 'Lunch', '☀️'),
        ('dinner', 'Dinner', '🌙'),
        ('snack', 'Snack', '🍎'),
    ]