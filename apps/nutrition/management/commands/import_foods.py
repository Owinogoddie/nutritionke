import json
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from apps.nutrition.models import Food, FoodGroup, PortionSize


class Command(BaseCommand):
    help = 'Import Kenyan foods and portion sizes from JSON files'

    def handle(self, *args, **kwargs):
        data_dir = Path(settings.BASE_DIR) / 'data'

        self.stdout.write('Importing foods...')
        self.import_foods(data_dir / 'kenya_foods_database.json')

        self.stdout.write('Importing portions...')
        self.import_portions(data_dir / 'kenya_portion_sizes.json')

        self.stdout.write(self.style.SUCCESS('Import complete!'))

    def import_foods(self, filepath):
        with open(filepath, 'r') as f:
            foods = json.load(f)

        for item in foods:
            # Skip entries with no real name
            if not item.get('name') or item['name'].replace('.', '').strip().replace('0', '').replace('1', '') == '':
                continue

            group, _ = FoodGroup.objects.get_or_create(
                code=item.get('group_code', '00'),
                defaults={'name': item.get('group', 'Unknown')}
            )

            Food.objects.update_or_create(
                code=item['code'],
                defaults={
                    'name': item['name'],
                    'group': group,
                    'kcal_per_100g': item.get('kcal_per_100g', 0) or 0,
                    'protein_g': item.get('protein_g', 0) or 0,
                    'fat_g': item.get('fat_g', 0) or 0,
                    'carbs_g': item.get('carbs_g', 0) or 0,
                    'fibre_g': item.get('fibre_g', 0) or 0,
                }
            )
        self.stdout.write(f'  Foods imported: {Food.objects.count()}')

    def import_portions(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)

        for entry in data.get('portions', []):
            try:
                food = Food.objects.get(code=entry['food_code'])
            except Food.DoesNotExist:
                continue

            for p in entry.get('portions', []):
                PortionSize.objects.get_or_create(
                    food=food,
                    label=p['label'],
                    defaults={
                        'description': p.get('description', ''),
                        'weight_g': p.get('weight_g', 100),
                        'typical_use': p.get('typical_use', ''),
                    }
                )
        self.stdout.write(f'  Portions imported: {PortionSize.objects.count()}')