from django.db import migrations


def create_builtin_lists(apps, schema_editor):
    IngredientList = apps.get_model("lists", "IngredientList")
    RecipeList = apps.get_model("lists", "RecipeList")
    Ingredient = apps.get_model("ingredients", "Ingredient")
    Recipe = apps.get_model("recipes", "Recipe")

    ing_list, _ = IngredientList.objects.get_or_create(
        is_builtin=True, defaults={"name": "Default", "user": None}
    )
    rec_list, _ = RecipeList.objects.get_or_create(
        is_builtin=True, defaults={"name": "Default", "user": None}
    )
    ing_list.ingredients.add(*Ingredient.objects.filter(is_default=True))
    rec_list.recipes.add(*Recipe.objects.filter(is_default=True))


def delete_builtin_lists(apps, schema_editor):
    IngredientList = apps.get_model("lists", "IngredientList")
    RecipeList = apps.get_model("lists", "RecipeList")
    IngredientList.objects.filter(is_builtin=True).delete()
    RecipeList.objects.filter(is_builtin=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("lists", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_builtin_lists, delete_builtin_lists),
    ]
