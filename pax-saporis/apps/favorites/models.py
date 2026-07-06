from django.db import models

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient
from apps.plans.models import DailyPlan
from apps.recipes.models import Recipe


class FavoriteIngredient(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorite_ingredients"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "ingredient")

    def __str__(self):
        return f"{self.user.email} → {self.ingredient.name}"


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorite_recipes"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "recipe")

    def __str__(self):
        return f"{self.user.email} → {self.recipe.name}"


class FavoritePlan(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorite_plans"
    )
    plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "plan")

    def __str__(self):
        return f"{self.user.email} → {self.plan.name}"
