from django.db import models
from apps.accounts.models import CustomUser
from apps.recipes.models import Recipe


class DailyPlan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='daily_plans')
    name = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date', 'name')

    def __str__(self):
        return f"{self.name} ({self.date})"

    @property
    def total_calories(self):
        return round(sum(pm.calories for pm in self.plan_meals.all()), 2)

    @property
    def total_protein(self):
        return round(sum(pm.protein for pm in self.plan_meals.all()), 2)

    @property
    def total_carbs(self):
        return round(sum(pm.carbs for pm in self.plan_meals.all()), 2)

    @property
    def total_fat(self):
        return round(sum(pm.fat for pm in self.plan_meals.all()), 2)


class PlanMeal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', 'Breakfast'
        LUNCH = 'lunch', 'Lunch'
        DINNER = 'dinner', 'Dinner'
        SNACK = 'snack', 'Snack'
        SUPPLEMENT = 'supplement', 'Supplement'

    UNIQUE_MEAL_TYPES = {MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER}

    daily_plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name='plan_meals')
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    name = models.CharField(max_length=100, blank=True, null=True, help_text="Requerido para snack y supplement")
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Unicidad para breakfast/lunch/dinner: mismo plan no puede tener dos del mismo tipo
        # Para snack/supplement: el nombre los diferencia
        constraints = [
            models.UniqueConstraint(
                fields=['daily_plan', 'meal_type'],
                condition=models.Q(meal_type__in=['breakfast', 'lunch', 'dinner']),
                name='unique_main_meal_per_plan'
            ),
            models.UniqueConstraint(
                fields=['daily_plan', 'meal_type', 'name'],
                condition=models.Q(meal_type__in=['snack', 'supplement']),
                name='unique_snack_supplement_name_per_plan'
            ),
        ]

    def __str__(self):
        label = self.name if self.name else self.meal_type
        return f"{label} - {self.daily_plan.date}"

    @property
    def calories(self):
        return round(self.recipe.total_calories if self.recipe else 0, 2)

    @property
    def protein(self):
        return round(self.recipe.total_protein if self.recipe else 0, 2)

    @property
    def carbs(self):
        return round(self.recipe.total_carbs if self.recipe else 0, 2)

    @property
    def fat(self):
        return round(self.recipe.total_fat if self.recipe else 0, 2)