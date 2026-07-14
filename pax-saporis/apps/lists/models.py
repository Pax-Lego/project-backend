from django.db import models

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient
from apps.recipes.models import Recipe


class IngredientList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ingredient_lists",
        null=True,
        blank=True,
        help_text="Nulo para la lista Default global",
    )
    name = models.CharField(max_length=255)
    is_builtin = models.BooleanField(
        default=False, help_text="Identifica la lista Default global (única)"
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name="lists", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["is_builtin"],
                condition=models.Q(is_builtin=True),
                name="unique_builtin_ingredient_list",
            ),
        ]

    def __str__(self):
        return self.name


class RecipeList(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipe_lists",
        null=True,
        blank=True,
        help_text="Nulo para la lista Default global",
    )
    name = models.CharField(max_length=255)
    is_builtin = models.BooleanField(
        default=False, help_text="Identifica la lista Default global (única)"
    )
    recipes = models.ManyToManyField(Recipe, related_name="lists", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["is_builtin"],
                condition=models.Q(is_builtin=True),
                name="unique_builtin_recipe_list",
            ),
        ]

    def __str__(self):
        return self.name
