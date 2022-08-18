import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


def ingredients_create(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1],
    )


filename_func_names = {
    'ingredients.csv': ingredients_create,
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for filename, func in filename_func_names.items():
            path = os.path.join(settings.BASE_DIR, '../data/') + filename
            with open(path, 'r', encoding='utf-8') as file:
                data = csv.reader(file)
                next(data)
                for row in data:
                    func(row)
                print(f'Added {filename}')
