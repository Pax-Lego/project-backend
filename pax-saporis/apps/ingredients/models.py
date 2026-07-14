from django.db import models

from apps.accounts.models import CustomUser


class Ingredient(models.Model):
    class MeasurementType(models.TextChoices):
        WEIGHT = "weight", "Por 100 g"
        UNIT = "unit", "Por unidad"

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="ingredients",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    measurement_type = models.CharField(
        max_length=10,
        choices=MeasurementType.choices,
        default=MeasurementType.WEIGHT,
    )
    calories_per_100g = models.FloatField(
        null=True, blank=True, help_text="Calorías por cada 100 g"
    )
    protein_g = models.FloatField(
        null=True, blank=True, help_text="Proteína en gramos (g) por cada 100 g"
    )
    carbs_g = models.FloatField(
        null=True, blank=True, help_text="Carbohidratos en gramos (g) por 100 g"
    )
    fat_g = models.FloatField(
        null=True, blank=True, help_text="Grasas en gramos (g) por cada 100 g"
    )
    unit_label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Nombre de la unidad (ej. 'huevo', 'rebanada')",
    )
    calories_per_unit = models.FloatField(null=True, blank=True)
    protein_per_unit = models.FloatField(null=True, blank=True)
    carbs_per_unit = models.FloatField(null=True, blank=True)
    fat_per_unit = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name
