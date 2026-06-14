from django.db import models
from apps.accounts.models import CustomUser
from apps.ingredients.models import Ingredient


class Recipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

    @property
    def total_calories(self):
        return sum(ri.calories for ri in self.ingredients_rel.all())

    @property
    def total_protein(self):
        return sum(ri.protein for ri in self.ingredients_rel.all())

    @property
    def total_carbs(self):
        return sum(ri.carbs for ri in self.ingredients_rel.all())

    @property
    def total_fat(self):
        return sum(ri.fat for ri in self.ingredients_rel.all())


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients_rel')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_g = models.FloatField(help_text="Cantidad en gramos")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity_g}g"

    @property
    def calories(self):
        return (self.ingredient.calories_per_100g / 100) * self.quantity_g

    @property
    def protein(self):
        return (self.ingredient.protein_g / 100) * self.quantity_g

    @property
    def carbs(self):
        return (self.ingredient.carbs_g / 100) * self.quantity_g

    @property
    def fat(self):
        return (self.ingredient.fat_g / 100) * self.quantity_g
