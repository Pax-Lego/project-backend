from django.core.management.base import BaseCommand

from apps.ingredients.models import Ingredient
from apps.lists.models import IngredientList, RecipeList
from apps.recipes.models import Recipe


class Command(BaseCommand):
    help = "Crea/actualiza las listas Default globales con los ingredientes y recetas is_default=True"

    def handle(self, *args, **options):
        ing_list, _ = IngredientList.objects.get_or_create(
            is_builtin=True, defaults={"name": "Default"}
        )
        rec_list, _ = RecipeList.objects.get_or_create(
            is_builtin=True, defaults={"name": "Default"}
        )
        ing_list.ingredients.add(*Ingredient.objects.filter(is_default=True))
        rec_list.recipes.add(*Recipe.objects.filter(is_default=True))

        self.stdout.write(
            self.style.SUCCESS(
                f"Default lists synced: {ing_list.ingredients.count()} ingredients, "
                f"{rec_list.recipes.count()} recipes"
            )
        )
