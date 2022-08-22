import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def load_ingredients(name, measurement_unit):
    Ingredient.objects.get_or_create(
        name=name,
        measurement_unit=measurement_unit,
    )


filename_func_names = {
    'ingredients.csv': load_ingredients,
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for filename, func in filename_func_names.items():
            path = os.path.join(settings.BASE_DIR, '../data/') + filename
            with open(path, 'r', encoding='utf-8') as file:
                data = csv.reader(file)
                next(data)
                for name, measurement_unit in data:
                    func(name, measurement_unit)
                print(f'Added {filename}')
