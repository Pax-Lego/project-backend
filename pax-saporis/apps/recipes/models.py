from django.db import models

from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient


class Recipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name

    @property
    def total_calories(self):
        return sum(ingredient.calories for ingredient in self.ingredients_rel.all())

    @property
    def total_protein(self):
        return sum(ingredient.protein for ingredient in self.ingredients_rel.all())

    @property
    def total_carbs(self):
        return sum(ingredient.carbs for ingredient in self.ingredients_rel.all())

    @property
    def total_fat(self):
        return sum(ingredient.fat for ingredient in self.ingredients_rel.all())


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients_rel"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(
        help_text="Cantidad en gramos (ingredientes por peso) o en unidades (ingredientes por unidad)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("recipe", "ingredient")

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity}"

    @property
    def calories(self):
        if self.ingredient.measurement_type == Ingredient.MeasurementType.UNIT:
            return (self.ingredient.calories_per_unit or 0) * self.quantity
        return (self.ingredient.calories_per_100g / 100) * self.quantity

    @property
    def protein(self):
        if self.ingredient.measurement_type == Ingredient.MeasurementType.UNIT:
            return (self.ingredient.protein_per_unit or 0) * self.quantity
        return (self.ingredient.protein_g / 100) * self.quantity

    @property
    def carbs(self):
        if self.ingredient.measurement_type == Ingredient.MeasurementType.UNIT:
            return (self.ingredient.carbs_per_unit or 0) * self.quantity
        return (self.ingredient.carbs_g / 100) * self.quantity

    @property
    def fat(self):
        if self.ingredient.measurement_type == Ingredient.MeasurementType.UNIT:
            return (self.ingredient.fat_per_unit or 0) * self.quantity
        return (self.ingredient.fat_g / 100) * self.quantity
