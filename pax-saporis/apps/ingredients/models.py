from django.db import models

from apps.accounts.models import CustomUser


class Ingredient(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ingredients",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    calories_per_100g = models.FloatField(help_text="Calorías por cada 100 g")
    protein_g = models.FloatField(help_text="Proteína en gramos (g) por cada 100 g")
    carbs_g = models.FloatField(help_text="Carbohidratos en gramos (g) por 100 g")
    fat_g = models.FloatField(help_text="Grasas en gramos (g) por cada 100 g")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name
